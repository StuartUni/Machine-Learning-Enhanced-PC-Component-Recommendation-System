"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-03-25
Description:
This script fetches game system requirements from the Steam API for recommendation purposes.
Features:
- Extracts game names using regex matching
- Retrieves Steam App IDs with fuzzy matching
- Parses system requirements into CPU, GPU, and RAM fields
- Saves fetched requirements into a local JSON file
"""

import os
import re
import time
import json
import html
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process, fuzz
from utils.component_matcher import match_requirements_to_components

# Define file path for saving game requirements
GAME_REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), "game_requirements.json")

def save_game_requirements(game_name, requirements):
    """Saves fetched game requirements to JSON."""
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

def load_game_requirements():
    """Loads existing game requirements from JSON."""
    if os.path.exists(GAME_REQUIREMENTS_FILE):
        try:
            with open(GAME_REQUIREMENTS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def extract_game_name(user_query):
    """Extracts likely game name from natural language query."""
    patterns = [r"play (.+)", r"run (.+)", r"for (.+)", r"that can (.+)", r"to (.+)"]
    for pattern in patterns:
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return user_query

def normalize_game_name(name):
    """Normalizes game names for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()

def get_steam_appid(user_query):
    """Finds the best matching Steam App ID using fuzzy matching."""
    game_name = extract_game_name(user_query)

    search_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(search_url)

    if response.status_code == 200:
        games = response.json().get("applist", {}).get("apps", [])

        filtered_games = [
            game for game in games if all(x not in game["name"].lower() for x in
                ["demo", "pack", "soundtrack", "expansion", "dlc", "mod", "beta", "test", "playtest", "campaign",
                 "pass", "bonus", "pre order", "expansion", "trailer", "deluxe edition", "game of the year", "goty",
                 "ultimate edition", "complete edition", "definitive edition", "remastered", "remake", "collection",
                 "bundle", "season pass", "season", "free to play", "free", "early access", "access", "alpha", "beta",
                 "test", "playtest"])
                and 3 < len(game["name"]) <= 50
                and "(" not in game["name"]
        ]

        game_dict = {game["name"]: game["appid"] for game in filtered_games}
        game_names = list(game_dict.keys())

        normalized_query = normalize_game_name(game_name)
        normalized_games = {normalize_game_name(name): name for name in game_names}

        for norm_name, original_name in normalized_games.items():
            if norm_name == normalized_query:
                return game_dict[original_name], original_name

        best_match, confidence = process.extractOne(normalized_query, normalized_games.keys(), scorer=fuzz.token_set_ratio)
        best_match_original = normalized_games[best_match]

        if confidence >= 75:
            return game_dict[best_match_original], best_match_original

        for norm_name, original_name in normalized_games.items():
            if normalized_query in norm_name:
                return game_dict[original_name], original_name

    return None, None

def parse_requirements(pc_req):
    """Parses CPU, GPU, and RAM from Steam requirements HTML."""
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
    """Cleans raw component description strings."""
    raw_string = raw_string.lower()

    junk_words = [
        "integrated", "graphics card", "grapics", "grapics card", "hd graphics", "gpu",
        "better", "equivalent", "or better", "or higher", "recommended", "video card",
        "compatible", "support", "graphics:", "card:"
    ]

    for junk in junk_words:
        raw_string = raw_string.replace(junk, "")

    raw_string = re.sub(r"\(.*?\)", "", raw_string)
    raw_string = re.sub(r"[^a-zA-Z0-9\s\-\.]", "", raw_string)

    return raw_string.strip().title()

def get_game_system_requirements(game_name, budget):
    """Fetches and parses system requirements for a game from the Steam API."""
    NON_GAMES = ["general", "work", "school", "office", "content creation", "design"]

    if game_name.lower() in NON_GAMES:
        return {"error": f"'{game_name}' is not a recognized game."}

    appid, matched_name = get_steam_appid(game_name)
    if not appid:
        return {"error": f"Game '{game_name}' not found on Steam."}

    store_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    headers = {"User-Agent": "Mozilla/5.0"}

    time.sleep(2)  # Respect Steam's API limits
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

    result = {
        "game": matched_name,
        "steam_appid": appid,
        "minimum_requirements": min_requirements,
        "recommended_requirements": rec_requirements
    }

    save_game_requirements(matched_name, result)
    return result