# """
# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 27/03/2025
# Description:
# This script seeds test users into the SQLite database for development and testing purposes.
# Each user is added with:
# - Unique username and email
# - Hashed password using bcrypt
# - A generated PC build pulled from real datasets using compatibility logic
# - A random rating inserted into the ratings table (for SVD training)
# """

# import sys
# import os
# import sqlite3
# import json
# import random
# import uuid

# from backend.auth.hashing import Hasher
# from backend.utils.component_matcher import get_compatible_build

# # ✅ Define DB path
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DB_PATH = os.path.join(BASE_DIR, "database", "users.db")

# # ✅ Generate dynamic test users with realistic builds
# usernames = ["alice", "bob", "charlie", "david", "eve", "frank", "grace", "heidi", "ivan", "judy"]
# test_users = []

# for i, username in enumerate(usernames):
#     build = get_compatible_build()
#     if not build:
#         print(f"❌ Skipping build for {username} due to compatibility issues.")
#         continue

#     build_id = str(uuid.uuid4())  # 🔐 Generate unique build ID for rating table

#     test_users.append({
#         "username": username,
#         "email": f"{username}@example.com",
#         "password": f"{username}123",
#         "role": "admin" if username == "charlie" else "user",
#         "saved_builds": build,
#         "build_id": build_id
#     })

# def seed_users():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     for user in test_users:
#         # ✅ Check if user exists
#         cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user["username"], user["email"]))
#         if cursor.fetchone():
#             print(f"⚠️ User '{user['username']}' already exists, skipping.")
#             continue

#         # ✅ Insert user
#         hashed_pw = Hasher.hash_password(user["password"])
#         saved_builds = json.dumps(user["saved_builds"])

#         cursor.execute('''
#             INSERT INTO users (username, email, hashed_password, role, saved_builds)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (user["username"], user["email"], hashed_pw, user["role"], saved_builds))
        
#         user_id = cursor.lastrowid  # 🔍 Get user ID for rating

#         # ✅ Insert associated rating
#         rating_value = random.randint(3, 5)
#         comment = random.choice([
#             "Great balance for 1080p gaming",
#             "Strong CPU, bit weak on GPU",
#             "Impressive value for the price",
#             "Overkill cooler but solid setup",
#             "Perfect for office + light gaming"
#         ])
#         cursor.execute('''
#             INSERT INTO ratings (user_id, build_id, rating, comment)
#             VALUES (?, ?, ?, ?)
#         ''', (user_id, user["build_id"], rating_value, comment))

#         print(f"✅ User '{user['username']}' added with compatible build and rating.")

#     conn.commit()
#     conn.close()
#     print("🎉 User + build + rating seeding complete!")

# # ✅ Run if executed directly
# if __name__ == "__main__":
#     seed_users()

"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025 (Updated 31/03/2025)
Description:
Seeds 30 users into the SQLite database with 5–10 compatible builds each.
Each build is inserted into the ratings table with a random score and comment.
"""

import os
import sqlite3
import json
import random
import uuid
from faker import Faker

from backend.auth.hashing import Hasher
from backend.utils.component_matcher import get_compatible_build

# ✅ Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
faker = Faker()

# ✅ Define comments
COMMENTS = [
    "Great balance for 1080p gaming",
    "Strong CPU, bit weak on GPU",
    "Impressive value for the price",
    "Overkill cooler but solid setup",
    "Perfect for office + light gaming",
    "Beast for 1440p editing",
    "Tight on budget, but runs well",
    "Quiet build with solid airflow"
]

# ✅ Generate 30 users
def seed_users(n_users=30):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _ in range(n_users):
        username = faker.user_name()
        email = faker.email()
        password = Hasher.hash_password("test123")
        role = "user"
        saved_builds = []

        # Check for existing user
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            continue

        # Insert user
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, saved_builds)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, role, json.dumps([])))

        user_id = cursor.lastrowid

        # Generate 5–10 builds
        for _ in range(random.randint(5, 10)):
            build = get_compatible_build()
            if not build:
                continue

            build_id = str(uuid.uuid4())
            rating = random.randint(3, 5)
            comment = random.choice(COMMENTS)

            # Insert rating
            cursor.execute('''
                INSERT INTO ratings (user_id, build_id, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, build_id, rating, comment))

            # Append to user's saved builds (optional)
            saved_builds.append(build)

        # Update saved builds JSON
        cursor.execute("UPDATE users SET saved_builds = ? WHERE id = ?", (json.dumps(saved_builds), user_id))
        print(f"✅ Seeded user '{username}' with {len(saved_builds)} builds.")

    conn.commit()
    conn.close()
    print("🎉 Seeding complete: 30 users with builds + ratings.")

# ✅ Run
if __name__ == "__main__":
    seed_users()