# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-08
# Description:
# Seeds the users.db with valid build_ids from labeled_builds.csv.
# Clears existing ratings to avoid mismatched or outdated rows.
# Ensures compatible training data for the TFRS model.

import sqlite3
import pandas as pd
import os
import random

def seed_valid_ratings(db_path: str, labeled_path: str, user_id: str = "9", rating_count: int = 10):
    if not os.path.exists(labeled_path):
        print(f"❌ Labeled builds file not found: {labeled_path}")
        return

    df = pd.read_csv(labeled_path)
    build_ids = df["build_id"].tolist()

    if len(build_ids) < rating_count:
        print(f"⚠️ Only {len(build_ids)} builds available, adjusting rating count.")
        rating_count = len(build_ids)

    sampled = random.sample(build_ids, rating_count)
    ratings = [(user_id, build_id, round(random.uniform(3.0, 5.0), 1)) for build_id in sampled]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id TEXT,
            build_id TEXT,
            rating REAL
        )
    """)

    # 🧹 Clean up old ratings first
    cursor.execute("DELETE FROM ratings")

    # ✅ Insert valid ratings
    cursor.executemany("INSERT INTO ratings (user_id, build_id, rating) VALUES (?, ?, ?)", ratings)
    conn.commit()
    conn.close()

    print(f"✅ Inserted {rating_count} valid ratings for user_id={user_id}.")

# 🔁 Run this to populate your DB with valid ratings
if __name__ == "__main__":
    DB_PATH = os.path.join("backend", "data", "users.db")
    LABELED_PATH = os.path.join("backend", "data", "builds", "labeled_builds.csv")
    seed_valid_ratings(DB_PATH, LABELED_PATH, user_id="9", rating_count=10)