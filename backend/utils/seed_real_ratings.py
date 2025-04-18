# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-18
# Description:
# Seeds valid ratings into the database from labeled_builds.csv for TFRS training.

import sqlite3
import pandas as pd
import os
import random

# ✅ Paths
DB_PATH = os.path.join( "database", "users.db")
LABELED_PATH = os.path.join( "data", "builds", "labeled_builds.csv")

# ✅ Connect
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Load labeled builds
if not os.path.exists(LABELED_PATH):
    print(f"❌ Missing labeled_builds.csv at {LABELED_PATH}")
    exit()

labeled_df = pd.read_csv(LABELED_PATH)
build_ids = labeled_df["build_id"].tolist()

# ✅ Clear old ratings
cursor.execute("DELETE FROM ratings")

# ✅ Get all user_ids
cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

# ✅ Insert ratings
for user_id in user_ids:
    sampled_builds = random.sample(build_ids, k=min(5, len(build_ids)))  # 5 ratings per user
    for build_id in sampled_builds:
        rating = round(random.uniform(3.0, 5.0), 1)  # Random rating between 3.0 and 5.0
        cursor.execute("""
            INSERT INTO ratings (user_id, build_id, rating)
            VALUES (?, ?, ?)
        """, (user_id, build_id, rating))

conn.commit()
conn.close()

print(f"✅ Seeded real ratings for {len(user_ids)} users.")