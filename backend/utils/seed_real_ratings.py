"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-18
Description:
This script seeds random valid ratings into the database using builds from labeled_builds.csv.
Features:
- Loads existing user IDs
- Randomly assigns 5 ratings per user
- Saves ratings into the 'ratings' table for training purposes
"""

import sqlite3
import pandas as pd
import os
import random

# Define paths
DB_PATH = os.path.join("database", "users.db")
LABELED_PATH = os.path.join("data", "builds", "labeled_builds.csv")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Load labeled builds
if not os.path.exists(LABELED_PATH):
    conn.close()
    raise FileNotFoundError(f"Missing labeled_builds.csv at {LABELED_PATH}")

labeled_df = pd.read_csv(LABELED_PATH)
build_ids = labeled_df["build_id"].tolist()

# Clear existing ratings
cursor.execute("DELETE FROM ratings")

# Get all user IDs
cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

# Insert random ratings
for user_id in user_ids:
    sampled_builds = random.sample(build_ids, k=min(5, len(build_ids)))
    for build_id in sampled_builds:
        rating = round(random.uniform(3.0, 5.0), 1)  # Rating between 3.0 and 5.0
        cursor.execute("""
            INSERT INTO ratings (user_id, build_id, rating)
            VALUES (?, ?, ?)
        """, (user_id, build_id, rating))

# Commit and close
conn.commit()
conn.close()