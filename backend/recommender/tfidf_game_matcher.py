# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-02
# Description: Uses TF-IDF to match user game queries with existing game requirement entries.

import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Path to Game Requirements JSON (used by Steam API fetcher)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_REQUIREMENTS_FILE = os.path.join(BASE_DIR, "utils", "game_requirements.json")

# ✅ TF-IDF Globals
tfidf_vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = None
game_names = []

def update_tfidf_model():
    """Reloads game descriptions and updates the TF-IDF vectorizer."""
    global tfidf_vectorizer, tfidf_matrix, game_names

    if not os.path.exists(GAME_REQUIREMENTS_FILE):
        print("❌ No game_requirements.json found.")
        return

    with open(GAME_REQUIREMENTS_FILE, "r") as file:
        data = json.load(file)

    game_descriptions = []
    game_names = []

    for game, details in data.items():
        if "error" in details:
            continue

        desc = details.get("minimum_requirements", {})
        description = f"CPU: {desc.get('CPU', 'Unknown')}, GPU: {desc.get('GPU', 'Unknown')}, RAM: {desc.get('RAM', 'Unknown')}"
        game_descriptions.append(description)
        game_names.append(game)

    if game_descriptions:
        tfidf_matrix = tfidf_vectorizer.fit_transform(game_descriptions)
        print(f"✅ TF-IDF Model updated with {len(game_names)} games.")
    else:
        print("⚠️ No game descriptions available for TF-IDF.")

def find_best_matching_game(user_input):
    """Returns the best matching game name using TF-IDF or None if confidence is too low."""
    if tfidf_matrix is None or len(game_names) == 0:
        update_tfidf_model()

    if tfidf_matrix is None or len(game_names) == 0:
        return None

    user_vector = tfidf_vectorizer.transform([user_input])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    best_match_index = similarity_scores.argmax()
    confidence = similarity_scores[best_match_index]

    if confidence < 0.3:
        print("⚠️ TF-IDF confidence too low:", confidence)
        return None

    return game_names[best_match_index]