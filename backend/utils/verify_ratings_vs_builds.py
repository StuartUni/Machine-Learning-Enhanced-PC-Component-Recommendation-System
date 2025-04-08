# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-08
# Description:
# Verifies that build_ids in the ratings table exist in labeled_builds.csv

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join("backend", "data", "users.db")
LABELED_PATH = os.path.join("backend", "data", "builds", "labeled_builds.csv")

# Load labeled build_ids
labeled_df = pd.read_csv(LABELED_PATH)
valid_build_ids = set(labeled_df["build_id"])

# Load ratings from DB
conn = sqlite3.connect(DB_PATH)
ratings_df = pd.read_sql_query("SELECT * FROM ratings", conn)
conn.close()

# Check mismatches
ratings_df["is_valid"] = ratings_df["build_id"].isin(valid_build_ids)
invalid_ratings = ratings_df[~ratings_df["is_valid"]]
valid_ratings = ratings_df[ratings_df["is_valid"]]

print(f"✅ Valid ratings found: {len(valid_ratings)}")
print(f"❌ Invalid ratings found: {len(invalid_ratings)}")

if not invalid_ratings.empty:
    print("⚠️ Invalid build_ids:")
    print(invalid_ratings["build_id"].tolist())