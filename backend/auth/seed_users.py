"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025
Description:
This script seeds test users into the SQLite database for development and testing purposes.
Each user is added with:
- Unique username and email
- Hashed password using bcrypt
- A generated PC build pulled from real datasets using compatibility logic
- A random rating inserted into the ratings table (for SVD training)
"""

import sys
import os
import sqlite3
import json
import random
import uuid

from backend.auth.hashing import Hasher
from backend.utils.component_matcher import get_compatible_build

# ✅ Define DB path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")

# ✅ Generate dynamic test users with realistic builds
usernames = ["alice", "bob", "charlie", "david", "eve", "frank", "grace", "heidi", "ivan", "judy"]
test_users = []

for i, username in enumerate(usernames):
    build = get_compatible_build()
    if not build:
        print(f"❌ Skipping build for {username} due to compatibility issues.")
        continue

    build_id = str(uuid.uuid4())  # 🔐 Generate unique build ID for rating table

    test_users.append({
        "username": username,
        "email": f"{username}@example.com",
        "password": f"{username}123",
        "role": "admin" if username == "charlie" else "user",
        "saved_builds": build,
        "build_id": build_id
    })

def seed_users():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for user in test_users:
        # ✅ Check if user exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user["username"], user["email"]))
        if cursor.fetchone():
            print(f"⚠️ User '{user['username']}' already exists, skipping.")
            continue

        # ✅ Insert user
        hashed_pw = Hasher.hash_password(user["password"])
        saved_builds = json.dumps(user["saved_builds"])

        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, saved_builds)
            VALUES (?, ?, ?, ?, ?)
        ''', (user["username"], user["email"], hashed_pw, user["role"], saved_builds))
        
        user_id = cursor.lastrowid  # 🔍 Get user ID for rating

        # ✅ Insert associated rating
        rating_value = random.randint(3, 5)
        comment = random.choice([
            "Great balance for 1080p gaming",
            "Strong CPU, bit weak on GPU",
            "Impressive value for the price",
            "Overkill cooler but solid setup",
            "Perfect for office + light gaming"
        ])
        cursor.execute('''
            INSERT INTO ratings (user_id, build_id, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, user["build_id"], rating_value, comment))

        print(f"✅ User '{user['username']}' added with compatible build and rating.")

    conn.commit()
    conn.close()
    print("🎉 User + build + rating seeding complete!")

# ✅ Run if executed directly
if __name__ == "__main__":
    seed_users()