"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script fetches game system requirements from the Steam API.
It:
- Extracts game names using fuzzy matching.
- Retrieves Steam App IDs and fetches system requirements.
- Parses and formats the extracted requirements.
"""

from bs4 import BeautifulSoup
import requests
import json
import time
import re
import html
import os
from fuzzywuzzy import process, fuzz
from utils.component_matcher import match_requirements_to_components

# ✅ Define file path for saving game requirements
GAME_REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), "game_requirements.json")

def save_game_requirements(game_name, requirements):
    """Saves fetched game requirements to JSON for future use."""
    if not os.path.exists(GAME_REQUIREMENTS_FILE):
        game_data = {}
    else:
        try:
            with open(GAME_REQUIREMENTS_FILE, "r") as f:
                game_data = json.load(f)
        except json.JSONDecodeError:
            game_data = {}

    game_data[game_name] = requirements

    with open(GAME_REQUIREMENTS_FILE, "w") as f:
        json.dump(game_data, f, indent=4)
    
    print(f"✅ Game requirements saved for '{game_name}'.")

def load_game_requirements():
    """Loads existing game requirements from JSON file."""
    if os.path.exists(GAME_REQUIREMENTS_FILE):
        try:
            with open(GAME_REQUIREMENTS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def extract_game_name(user_query):
    """Extracts the most likely game name from a natural language query."""
    patterns = [r"play (.+)", r"run (.+)", r"for (.+)", r"that can (.+)", r"to (.+)"]
    
    for pattern in patterns:
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return user_query  

def normalize_game_name(name):
    """Lowercase, remove special chars, and simplify spaces."""
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()

def get_steam_appid(user_query):
    """Search for the correct Steam App ID with smart fallback if fuzzy match isn't perfect."""
    game_name = extract_game_name(user_query)
    print(f"🔍 Extracted Game Name: '{game_name}' from Query: '{user_query}'")

    search_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(search_url)

    if response.status_code == 200:
        games = response.json().get("applist", {}).get("apps", [])

        filtered_games = [
            game for game in games if all(x not in game["name"].lower() for x in
                ["demo", "pack", "soundtrack", "expansion", "dlc", "mod", "beta", "test", "playtest", "campaign", "pass", "bonus", "pre order", "expansion", "trailer", "deluxe edition", "game of the year", "goty", "ultimate edition", "complete edition", "definitive edition", "remastered", "remake", "collection", "bundle", "season pass", "season", "free to play", "free", "early access", "access", "alpha", "beta", "test", "playtest"])
                and len(game["name"]) > 3
                and len(game["name"]) <= 50  # ✅ Reasonable name length
                and "(" not in game["name"]  # ✅ Avoid parentheses which usually mean extras
        ]

        game_dict = {game["name"]: game["appid"] for game in filtered_games}
        game_names = list(game_dict.keys())

        # ✅ Normalize names for comparison
        normalized_query = normalize_game_name(game_name)
        normalized_games = {normalize_game_name(name): name for name in game_names}

        # ✅ Exact Match Check (normalized)
        for norm_name, original_name in normalized_games.items():
            if norm_name == normalized_query:
                print(f"✅ Found Exact Match: {original_name} (App ID: {game_dict[original_name]})")
                return game_dict[original_name], original_name

        # ✅ Fuzzy Match
        best_match, confidence = process.extractOne(normalized_query, normalized_games.keys(), scorer=fuzz.token_set_ratio)
        best_match_original = normalized_games[best_match]

        if confidence >= 75:
            print(f"✅ Fuzzy Matched Game: {best_match_original} (Confidence: {confidence}%)")
            return game_dict[best_match_original], best_match_original

        # ✅ Partial Match as fallback
        for norm_name, original_name in normalized_games.items():
            if normalized_query in norm_name:
                print(f"✅ Partial Match: {original_name}")
                return game_dict[original_name], original_name

        print(f"❌ No good match for '{game_name}'. Best fuzzy match was '{best_match_original}' ({confidence}%)")
        return None, None

    print(f"❌ Steam API unavailable.")
    return None, None

def parse_requirements(pc_req):
    """Extracts system requirements from Steam HTML and cleans them up for matching."""
    from bs4 import BeautifulSoup
    import html

    # ✅ Format check
    if isinstance(pc_req, list) and pc_req:
        pc_req = pc_req[0]

    if not isinstance(pc_req, str) or pc_req == "Not available":
        return {"CPU": "Unknown", "RAM": "Unknown", "GPU": "Unknown"}

    decoded_html = html.unescape(pc_req)
    soup = BeautifulSoup(decoded_html, "html.parser")
    lines = [line.strip() for line in soup.get_text(separator="\n").split("\n") if line.strip()]

    requirements = {"CPU": "Unknown", "RAM": "Unknown", "GPU": "Unknown"}
    prev_line = ""

    for line in lines:
        clean_line = line.lower()

        if "processor" in prev_line or "cpu" in clean_line:
            cleaned = sanitize_component_string(line)
            requirements["CPU"] = cleaned
        elif "graphics" in prev_line or "gpu" in clean_line:
            cleaned = sanitize_component_string(line)
            requirements["GPU"] = cleaned
        elif "memory" in clean_line or "ram" in clean_line:
            ram_match = re.search(r"(\d+)\s*gb", line, re.IGNORECASE)
            requirements["RAM"] = ram_match.group(1) + " GB" if ram_match else "Unknown"

        prev_line = clean_line

    return requirements

def sanitize_component_string(raw_string):
    """
    Cleans vague or noisy CPU/GPU strings to make them more matcher-friendly.
    """
    raw_string = raw_string.lower()

    # Remove vague/non-model keywords
    junk_words = [
        "integrated", "graphics card", "grapics", "grapics card", "hd graphics", "gpu",
        "better", "equivalent", "or better", "or higher", "recommended", "video card",
        "compatible", "support", "graphics:", "card:"
    ]
    for junk in junk_words:
        raw_string = raw_string.replace(junk, "")

    # Strip parenthesis and punctuation
    raw_string = re.sub(r"\(.*?\)", "", raw_string)
    raw_string = re.sub(r"[^a-zA-Z0-9\s\-\.]", "", raw_string)

    return raw_string.strip().title()

def get_game_system_requirements(game_name, budget):
    """Fetch system requirements from Steam API and match them to components within budget."""
    
    NON_GAMES = ["general", "work", "school", "office", "content creation", "design"]
    if game_name.lower() in NON_GAMES:
        print(f"⚠️ Skipping Steam API request for non-game query: {game_name}")
        return {"error": f"'{game_name}' is not a recognized game."}

    appid, matched_name = get_steam_appid(game_name)
    if not appid:
        print(f"❌ ERROR: Game '{game_name}' not found on Steam.")
        return {"error": f"Game '{game_name}' not found on Steam."}

    store_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    headers = {"User-Agent": "Mozilla/5.0"}

    time.sleep(2)  # Prevents API rate limits
    response = requests.get(store_url, headers=headers)

    if response.status_code != 200:
        return {"error": f"Failed to retrieve data from Steam API for '{game_name}'."}

    game_data = response.json()
    if str(appid) not in game_data or not game_data[str(appid)]["success"]:
        return {"error": "Failed to fetch system requirements from Steam API."}

    game_info = game_data[str(appid)]["data"]
    pc_req = game_info.get("pc_requirements", {})

    min_requirements = parse_requirements(pc_req.get("minimum", "Not available"))
    rec_requirements = parse_requirements(pc_req.get("recommended", "Not available"))

    if min_requirements["CPU"] == "Unknown":
        min_requirements = parse_requirements(pc_req.get("minimum", "Unknown"))
    if rec_requirements["CPU"] == "Unknown":
        rec_requirements = parse_requirements(pc_req.get("recommended", "Unknown"))

    game_info = {
        "game": matched_name,
        "steam_appid": appid,
        "minimum_requirements": min_requirements,
        "recommended_requirements": rec_requirements
    }

    save_game_requirements(matched_name, game_info)
    return game_info