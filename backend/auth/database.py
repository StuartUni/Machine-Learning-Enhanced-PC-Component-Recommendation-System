"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 26/03/2025
Description:
This script sets up the SQLite database for user authentication.
It:
- Creates a `users.db` SQLite database (if not exists)
- Defines a `users` table to store `id`, `username`, and `hashed_password`
- Provides a function to get a database connection
"""

import sqlite3
import os

# ✅ Define database file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "users.db")

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def get_db_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

# ✅ Run database initialization when script is executed
if __name__ == "__main__":
    init_db()