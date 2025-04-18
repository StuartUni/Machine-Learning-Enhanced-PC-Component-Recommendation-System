# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-18
# Description:
# Checks if ratings in users.db are valid (i.e., build_id exists in labeled_builds.csv).
# Prints number of valid and invalid ratings.

import sqlite3
import pandas as pd
import os

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR,  "database", "users.db")
LABELED_PATH = os.path.join(BASE_DIR,  "data", "builds", "labeled_builds.csv")

# ✅ Load ratings
conn = sqlite3.connect(DB_PATH)
ratings_df = pd.read_sql_query("SELECT * FROM ratings", conn)
conn.close()

# ✅ Load builds
builds_df = pd.read_csv(LABELED_PATH)
build_ids = set(builds_df["build_id"])

# ✅ Validate ratings
valid_ratings = ratings_df[ratings_df["build_id"].isin(build_ids)]

# ✅ Output
print(f"✅ Total ratings in database: {len(ratings_df)}")
print(f"✅ Valid ratings (build_id exists): {len(valid_ratings)}")
print(f"⚠️ Invalid ratings (missing build_id): {len(ratings_df) - len(valid_ratings)}")

if len(valid_ratings) == len(ratings_df):
    print("🎯 All ratings are valid!")
else:
    print("⚠️ Some ratings are invalid. You may need to reseed your ratings.")