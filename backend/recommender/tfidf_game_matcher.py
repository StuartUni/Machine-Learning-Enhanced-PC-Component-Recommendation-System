# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-02
# Description: Utility for updating and retrieving the best-matching game title using TF-IDF vectorization.

import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global state
GAME_REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), "..", "utils", "game_requirements.json")
tfidf_vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = None
game_names = []

# Load game data
def load_game_data():
    if os.path.exists(GAME_REQUIREMENTS_FILE):
        with open(GAME_REQUIREMENTS_FILE, "r") as f:
            return json.load(f)
    return {}

# Update TF-IDF model based on game descriptions
def update_tfidf_model():
    global tfidf_matrix, game_names
    game_data = load_game_data()

    game_descriptions = []
    game_names = []

    for game, details in game_data.items():
        if "error" in details:
            continue

        min_req = details.get("minimum_requirements", {})
        description = f"CPU: {min_req.get('CPU', 'Unknown')}, GPU: {min_req.get('GPU', 'Unknown')}, RAM: {min_req.get('RAM', 'Unknown')}"
        game_descriptions.append(description)
        game_names.append(game)

    if game_descriptions:
        tfidf_matrix = tfidf_vectorizer.fit_transform(game_descriptions)

# Find the best matching game based on user input
def find_best_matching_game(user_input):
    if not tfidf_matrix or not game_names:
        update_tfidf_model()

    user_vector = tfidf_vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

    best_match_idx = similarities.argmax()
    best_match_game = game_names[best_match_idx]
    confidence_score = similarities[best_match_idx]

    if confidence_score < 0.3:
        return None
    return best_match_game
