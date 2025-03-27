"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025
Description:
This script seeds test users into the SQLite database for development and testing purposes.
Each user is added with:
- Unique username and email
- Hashed password using bcrypt
- Optional saved PC build (as JSON string) including all major components:
  CPU, GPU, RAM, Motherboard, Power Supply, and CPU Cooler.
"""

import sqlite3
import os
import json
from backend.auth.hashing import Hasher

# ✅ Define DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")

# ✅ Seed user data
test_users = [
    {
        "username": "alice",
        "email": "alice@example.com",
        "password": "alice123",
        "role": "user",
        "saved_builds": {
            "cpu": {"name": "Intel Core i5-12400F", "price": 200.0},
            "gpu": {"name": "NVIDIA GTX 1660 Super", "price": 250.0},
            "ram": {"name": "Corsair Vengeance 16GB DDR4", "price": 60.0},
            "motherboard": {"name": "ASUS Prime B660M-A", "price": 120.0},
            "power_supply": {"name": "EVGA 600W Bronze", "price": 50.0},
            "cpu_cooler": {"name": "Cooler Master Hyper 212", "price": 40.0}
        }
    },
    {
        "username": "bob",
        "email": "bob@example.com",
        "password": "bobpass",
        "role": "user",
        "saved_builds": {
            "cpu": {"name": "Intel Core i3-12100", "price": 120.0},
            "gpu": {"name": "Intel Arc A380", "price": 140.0},
            "ram": {"name": "TeamGroup 8GB DDR4", "price": 30.0},
            "motherboard": {"name": "Gigabyte H610M", "price": 85.0},
            "power_supply": {"name": "Thermaltake 500W", "price": 40.0},
            "cpu_cooler": {"name": "Stock Intel Cooler", "price": 0.0}
        }
    },
    {
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "charlie321",
        "role": "admin",
        "saved_builds": {
            "cpu": {"name": "AMD Ryzen 7 5800X", "price": 300.0},
            "gpu": {"name": "AMD Radeon RX 6700 XT", "price": 400.0},
            "ram": {"name": "G.SKILL Trident Z 32GB DDR4", "price": 120.0},
            "motherboard": {"name": "MSI MAG B550 Tomahawk", "price": 150.0},
            "power_supply": {"name": "Corsair RM750x", "price": 100.0},
            "cpu_cooler": {"name": "Noctua NH-D15", "price": 90.0}
        }
    }
]

def seed_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for user in test_users:
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user["username"], user["email"]))
        if cursor.fetchone():
            print(f"⚠️ User '{user['username']}' already exists, skipping.")
            continue

        hashed_pw = Hasher.hash_password(user["password"])
        saved_builds = json.dumps(user["saved_builds"])

        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, saved_builds)
            VALUES (?, ?, ?, ?, ?)
        ''', (user["username"], user["email"], hashed_pw, user["role"], saved_builds))

        print(f"✅ User '{user['username']}' added.")

    conn.commit()
    conn.close()
    print("🎉 Seeding complete!")

# ✅ Run if executed directly
if __name__ == "__main__":
    seed_users()