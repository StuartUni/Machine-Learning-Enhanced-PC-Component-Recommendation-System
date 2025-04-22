"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-08
Description:
This script connects to users.db, filters out ratings with build IDs not found in labeled_builds.csv,
and exports the valid ratings to ratings.csv for model training.
"""

import sqlite3
import pandas as pd
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
LABELED_PATH = os.path.join(BASE_DIR, "data", "builds", "labeled_builds.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "ratings.csv")

def export_ratings_to_csv(db_path: str, output_csv_path: str, labeled_path: str):
    """Exports filtered valid ratings to a CSV file."""
    try:
        # Connect to database and load ratings
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT user_id, build_id, rating FROM ratings", conn)
        conn.close()

        if df.empty:
            return  # No ratings to export

        # Load labeled builds
        labeled_df = pd.read_csv(labeled_path)
        valid_build_ids = set(labeled_df["build_id"])

        # Filter ratings for valid build IDs
        before_count = len(df)
        df = df[df["build_id"].isin(valid_build_ids)]
        removed_count = before_count - len(df)

        if df.empty:
            return  # No valid ratings to export

        # Ensure output directory exists and save CSV
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        df.to_csv(output_csv_path, index=False)

    except Exception as e:
        print(f"Failed to export ratings: {e}")

# CLI usage
if __name__ == "__main__":
    export_ratings_to_csv(DB_PATH, OUTPUT_CSV, LABELED_PATH)