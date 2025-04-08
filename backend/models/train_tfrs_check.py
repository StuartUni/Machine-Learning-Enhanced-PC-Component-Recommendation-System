# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-07
# Description:
# Checks if a TFRS model exists and only trains a new one if it doesn't.
# It also exports ratings from users.db to ratings.csv before training.

import os
from models.train_tfrs_model import train_model
from utils.export_ratings_to_csv import export_ratings_to_csv

def train_if_needed(force_retrain=False):
    MODEL_PATH = os.path.join("backend", "models", "tfrs_model.keras")
    DB_PATH = os.path.join("backend", "data", "users.db")
    CSV_PATH = os.path.join("backend", "data", "ratings.csv")

    if not os.path.exists(MODEL_PATH) or force_retrain:
        print("🔄 No existing model found or retraining forced. Exporting and training now...")
        export_ratings_to_csv(DB_PATH, CSV_PATH)
        train_model(CSV_PATH, MODEL_PATH)
        return True
    else:
        print("✅ Reusing existing TFRS model.")
        return False

# Example usage
if __name__ == "__main__":
    train_if_needed()