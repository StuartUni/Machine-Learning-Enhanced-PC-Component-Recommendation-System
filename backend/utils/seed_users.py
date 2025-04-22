"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-18
Description:
This script seeds the users.db database with fake users and dummy builds for testing purposes.
Features:
- Creates 30 fake users with Faker library
- Inserts dummy builds and ratings for each user
- Creates tables if they do not already exist
"""

import os
import sqlite3
import json
import random
import uuid
from faker import Faker

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
faker = Faker()

# Seed users and dummy builds
def seed_users(n_users=30):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
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

    # Create ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id TEXT,
            build_id TEXT,
            rating REAL
        )
    """)

    # Insert fake users
    for _ in range(n_users):
        username = faker.user_name()
        email = faker.email()
        password = "fake_hashed_password"
        role = "user"

        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, saved_builds)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, role, json.dumps([])))

        user_id = cursor.lastrowid

        # Insert 5 dummy ratings
        for _ in range(5):
            build_id = str(uuid.uuid4())
            rating = round(random.uniform(3.0, 5.0), 1)
            cursor.execute('''
                INSERT INTO ratings (user_id, build_id, rating)
                VALUES (?, ?, ?)
            ''', (user_id, build_id, rating))

    # Commit changes and close
    conn.commit()
    conn.close()

# CLI entry point
if __name__ == "__main__":
    seed_users()