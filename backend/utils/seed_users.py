# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-18
# Description:
# Seeds the users.db with 30 fake users and simple dummy builds for testing.

import os
import sqlite3
import json
import random
import uuid
from faker import Faker

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
faker = Faker()

# ✅ Setup
def seed_users(n_users=30):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            hashed_password TEXT,
            role TEXT,
            saved_builds TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id TEXT,
            build_id TEXT,
            rating REAL
        )
    """)

    for _ in range(n_users):
        username = faker.user_name()
        email = faker.email()
        password = "fake_hashed_password"  # You can improve later if needed
        role = "user"
        saved_builds = []

        # Insert user
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, saved_builds)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, role, json.dumps([])))

        user_id = cursor.lastrowid

        # Insert 5 dummy ratings per user
        for _ in range(5):
            build_id = str(uuid.uuid4())
            rating = round(random.uniform(3.0, 5.0), 1)
            cursor.execute('''
                INSERT INTO ratings (user_id, build_id, rating)
                VALUES (?, ?, ?)
            ''', (user_id, build_id, rating))

    conn.commit()
    conn.close()
    print(f"🎉 Seeded {n_users} users with fake builds and ratings.")

# 🔁 CLI
if __name__ == "__main__":
    seed_users()