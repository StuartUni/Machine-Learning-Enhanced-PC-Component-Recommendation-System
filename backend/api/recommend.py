"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script defines the recommendation API for the PC Component Recommendation System.
It:
- Loads a trained machine learning model.
- Processes user input (budget, use case, and game preferences).
- Uses TF-IDF to match game requirements.
- Selects the best PC components based on budget allocation.
"""

from fastapi import APIRouter, HTTPException
import joblib
import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.component_matcher import match_requirements_to_components
from utils.steam_api_fetcher import get_game_system_requirements

# ✅ Initialize Router
recommend_router = APIRouter()

# ✅ Load Model & Scaler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sklearn_recommendation_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    raise HTTPException(status_code=500, detail="❌ Model or Scaler file missing. Train the model first.")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ✅ Load Component Data
DATA_DIR = os.path.join(BASE_DIR, "data")
COMPONENT_FILES = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "case": "preprocessed_filtered_case.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
}

# ✅ Load datasets
component_data = {}
for key, filename in COMPONENT_FILES.items():
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df["price"] = df.get("original_price", df["price"])  # Ensure price consistency
        component_data[key] = df
    else:
        print(f"⚠️ Warning: Missing {key} file at {file_path}")

# ✅ Budget Allocation Strategy
budget_allocation = {
    "gaming": {"cpu": 0.25, "gpu": 0.40, "ram": 0.10, "motherboard": 0.10, "power_supply": 0.05, "case": 0.025, "cpu_cooler": 0.025},
    "work": {"cpu": 0.42, "gpu": 0.22, "ram": 0.15, "motherboard": 0.10, "power_supply": 0.10, "cpu_cooler": 0.10},
    "school": {"cpu": 0.42, "gpu": 0.17, "ram": 0.20, "motherboard": 0.10, "power_supply": 0.10, "cpu_cooler": 0.10},
    "general": {"cpu": 0.40, "gpu": 0.25, "ram": 0.15, "motherboard": 0.10, "power_supply": 0.10, "cpu_cooler": 0.10}
}

# ✅ Load Game Requirements from JSON
GAME_REQUIREMENTS_FILE = os.path.join(BASE_DIR, "data", "game_requirements.json")
game_data = json.load(open(GAME_REQUIREMENTS_FILE, "r")) if os.path.exists(GAME_REQUIREMENTS_FILE) else {}

# ✅ Initialize TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix, game_names = None, []

def update_tfidf():
    """Updates the TF-IDF model with game descriptions."""
    global tfidf_vectorizer, tfidf_matrix, game_names
    game_descriptions, game_names = [], []

    for game, details in game_data.items():
        if "error" in details:
            continue
        min_req = details.get("minimum_requirements", {})
        description = f"CPU: {min_req.get('CPU', 'Unknown')}, GPU: {min_req.get('GPU', 'Unknown')}, RAM: {min_req.get('RAM', 'Unknown')}"
        game_descriptions.append(description)
        game_names.append(game)

    if game_descriptions:
        tfidf_matrix = tfidf_vectorizer.fit_transform(game_descriptions)
        print("✅ TF-IDF Model Updated with Game Data")

update_tfidf()

def find_best_matching_game(user_input):
    """Finds the most relevant game based on user input using TF-IDF, with exact matching fallback."""
    for game in game_names:
        if user_input.lower() in game.lower():
            return game
    if tfidf_matrix is None:
        return None
    user_vector = tfidf_vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    best_match_idx = np.argmax(similarities)
    return game_names[best_match_idx] if similarities[best_match_idx] >= 0.3 else None

@recommend_router.post("/recommend")
def get_recommendation(user_input: dict):
    """Returns recommended PC components based on user budget and use case (gaming, work, etc.)."""

    if "budget" not in user_input or "query" not in user_input:
        raise HTTPException(status_code=400, detail="❌ Please provide a budget and query.")

    budget, user_query = user_input["budget"], user_input["query"].lower()
    if not isinstance(budget, (int, float)) or budget <= 0:
        raise HTTPException(status_code=400, detail="❌ Invalid budget. Enter a number greater than 0.")

    matched_game = find_best_matching_game(user_query)

    if matched_game:
        game_requirements = game_data.get(matched_game, {})

        # ✅ If requirements do not exist, fetch them from Steam API
        if not game_requirements:
            print(f"🌐 Fetching game details from Steam API for: {matched_game}")
            game_requirements = get_game_system_requirements(matched_game, budget)

            # ✅ Save newly fetched game data for future use
            if "error" not in game_requirements:
                game_data[matched_game] = game_requirements
                with open(GAME_REQUIREMENTS_FILE, "w") as file:
                    json.dump(game_data, file, indent=4)

    else:
        print(f"❌ Game '{user_query}' not found. Querying Steam API...")
        game_requirements = get_game_system_requirements(user_query, budget)

        if "error" not in game_requirements:
            matched_game = game_requirements["game"]
            game_data[matched_game] = game_requirements
            with open(GAME_REQUIREMENTS_FILE, "w") as file:
                json.dump(game_data, file, indent=4)
        else:
            return {"error": f"Game '{user_query}' not found on Steam."}

    matched_components = match_requirements_to_components(game_requirements.get("minimum_requirements", {}), budget)

    return {
        "matched_game": matched_game if matched_game else "Unknown",
        "recommended_components": matched_components
    }