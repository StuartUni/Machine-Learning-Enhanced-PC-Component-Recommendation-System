# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-04
# Description:
# Loads and runs a content-based recommendation model using cosine similarity
# on a set of labeled builds (generated combinations of compatible components).
# This approach uses a MinMaxScaler specifically trained for content-based matching.

import os
import joblib
import pandas as pd
import numpy as np

# ✅ Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCALER_PATH = os.path.join(BASE_DIR, "models", "content_scaler.pkl")
BUILD_DATA_PATH = os.path.join(BASE_DIR, "data", "builds", "labeled_builds.csv")

# ✅ Ensure dependencies exist
if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError("❌ Content-based scaler not found. Train it using train_content_scaler.py.")
if not os.path.exists(BUILD_DATA_PATH):
    raise FileNotFoundError("❌ Labeled build dataset not found.")

# ✅ Load scaler and dataset
scaler = joblib.load(SCALER_PATH)
build_df = pd.read_csv(BUILD_DATA_PATH)

# ✅ Ensure required features are present
FEATURE_COLUMNS = ["cpu_score", "gpu_score", "ram_gb", "storage_gb", "price"]
if not all(col in build_df.columns for col in FEATURE_COLUMNS):
    raise ValueError("❌ Required feature columns missing from labeled_builds.csv")

def recommend_build_from_features(user_features: dict, top_k: int = 1):
    """
    Recommends the top-k most similar PC builds using a content-based filtering approach.
    user_features = {
        'cpu_score': float,
        'gpu_score': float,
        'ram_gb': int,
        'storage_gb': int,
        'price': float
    }
    """
    input_df = pd.DataFrame([user_features])
    scaled_input = scaler.transform(input_df)

    build_features = build_df[FEATURE_COLUMNS]
    scaled_builds = scaler.transform(build_features)

    # ✅ Use Euclidean distance (could replace with cosine if desired)
    distances = np.linalg.norm(scaled_builds - scaled_input, axis=1)
    build_df["similarity"] = -distances  # Lower distance = higher similarity

    top_builds = build_df.sort_values("similarity", ascending=False).head(top_k)
    return top_builds.to_dict(orient="records")

# 🧪 Local Test
if __name__ == "__main__":
    # Example input (you can adjust as needed for real testing)
    user_input = {
        "cpu_score": 18000,
        "gpu_score": 14000,
        "ram_gb": 16,
        "storage_gb": 1000,
        "price": 1200
    }

    top_builds = recommend_build_from_features(user_input, top_k=1)

    print("✅ Top Content-Based Build Recommendation:")
    for build in top_builds:
        print(build)