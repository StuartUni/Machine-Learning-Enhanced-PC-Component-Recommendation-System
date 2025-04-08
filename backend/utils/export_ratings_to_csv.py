# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-08
# Description:
# Connects to users.db, filters out ratings with build_ids not in labeled_builds.csv,
# and writes the valid ratings to ratings.csv

import sqlite3
import pandas as pd
import os

def export_ratings_to_csv(db_path: str, output_csv_path: str, labeled_path: str):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT user_id, build_id, rating FROM ratings", conn)
        conn.close()

        if df.empty:
            print("⚠️ No ratings found in the database.")
            return

        labeled_df = pd.read_csv(labeled_path)
        valid_build_ids = set(labeled_df["build_id"])

        before = len(df)
        df = df[df["build_id"].isin(valid_build_ids)]
        removed = before - len(df)

        if df.empty:
            print("⚠️ No valid ratings after filtering.")
        else:
            os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
            df.to_csv(output_csv_path, index=False)
            print(f"✅ Exported {len(df)} valid ratings to {output_csv_path}")
            if removed:
                print(f"🧹 Removed {removed} invalid ratings (missing builds)")
    except Exception as e:
        print(f"❌ Failed to export ratings: {e}")

# 🔁 CLI
if __name__ == "__main__":
    DB_PATH = os.path.join("backend", "data", "users.db")
    LABELED_PATH = os.path.join("backend", "data", "builds", "labeled_builds.csv")
    OUTPUT_CSV = os.path.join("backend", "data", "ratings.csv")
    export_ratings_to_csv(DB_PATH, OUTPUT_CSV, LABELED_PATH)