"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 26/03/2025
Description:
This script sets up the SQLite database for user authentication and ratings.
It:
- Creates a `users.db` SQLite database (if not exists)
- Defines a `users` table to store user credentials and saved builds
- Defines a `ratings` table to store user-submitted ratings on builds
- Provides a function to get a database connection
"""

import sqlite3
import os

#  Define database file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "users.db")

#  Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #  Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            saved_builds TEXT
        )
    ''')

    #  Create Ratings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            build_id TEXT NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print(" Database initialized successfully!")

def get_db_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

#  Run database initialization when script is executed
if __name__ == "__main__":
    init_db()