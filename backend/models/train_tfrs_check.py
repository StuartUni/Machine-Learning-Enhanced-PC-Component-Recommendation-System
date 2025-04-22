"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-07
Description:
This script checks if a TensorFlow Recommenders (TFRS) model already exists.
Features:
- If no model exists (or retraining is forced), exports ratings from the SQLite database
- Triggers training of a new TFRS model and saves it to disk
- Supports manual retraining via command-line execution
"""

import os
from models.train_tfrs_model import train_model
from utils.export_ratings_to_csv import export_ratings_to_csv

def train_if_needed(force_retrain=False):
    #  Correct file paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "tfrs_model.keras")
    DB_PATH = os.path.join(BASE_DIR, "database", "users.db")  
    CSV_PATH = os.path.join(BASE_DIR, "data", "ratings.csv")
    LABELED_PATH = os.path.join(BASE_DIR, "data", "builds", "labeled_builds.csv")

    #  Train model if it doesn't exist or retraining is forced
    if not os.path.exists(MODEL_PATH) or force_retrain:
        print("🔄 No existing model found or retraining forced. Exporting and training now...")
        export_ratings_to_csv(DB_PATH, CSV_PATH, LABELED_PATH)
        train_model(CSV_PATH, MODEL_PATH)
        return True
    else:
        print(" Reusing existing TFRS model.")
        return False

#  CLI usage
if __name__ == "__main__":
    train_if_needed()