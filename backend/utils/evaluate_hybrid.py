# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-08
# Description:
# This script evaluates the hybrid model using Precision@K and Recall@K
# by comparing predicted top-k builds with actual user-rated builds.

import os
import sys
import pandas as pd

# ✅ Set up import path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(BACKEND_DIR)

from recommender.hybrid_recommender import get_hybrid_recommendation

def precision_recall_at_k(predicted, actual, k=3):
    predicted_k = predicted[:k]
    actual_set = set(actual)
    relevant = [p for p in predicted_k if p in actual_set]
    precision = len(relevant) / k
    recall = len(relevant) / len(actual_set) if actual_set else 0
    return precision, recall

# 🧪 Run evaluation for a known user_id
if __name__ == "__main__":
    user_id = "9"
    budget = 900
    k = 3

    result = get_hybrid_recommendation({
        "budget": budget,
        "query": "general",
        "user_id": user_id,
        "mode": "hybrid"
    })

    # ✅ Normalize predicted build IDs
    top_k = [str(b["build_id"]).strip() for b in result.get("collaborative_top_k", [])]

    # ✅ Load and normalize actual rated builds
    ratings_path = os.path.join(BACKEND_DIR, "data", "ratings.csv")
    ratings_df = pd.read_csv(ratings_path)

    actual_rated = ratings_df[
        ratings_df["user_id"].astype(str) == str(user_id)
    ]["build_id"].astype(str).str.strip().tolist()

    # ✅ Compute metrics
    precision, recall = precision_recall_at_k(top_k, actual_rated, k=k)

    print("📊 Evaluation Results")
    print(f"User ID: {user_id}")
    print(f"Top-{k} Predictions: {top_k}")
    print(f"Actual Rated Builds: {actual_rated}")
    print(f"✅ Precision@{k}: {precision:.2f}")
    print(f"✅ Recall@{k}: {recall:.2f}")