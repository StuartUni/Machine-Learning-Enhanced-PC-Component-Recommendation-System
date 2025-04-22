"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-19
Description:
This script resets the users and ratings tables inside the users.db database.
Features:
- Drops existing 'users' and 'ratings' tables if they exist
- Recreates the 'users' and 'ratings' tables with correct schema
"""

import sqlite3

# Define database path
db_path = r'C:\Users\Stuart\Desktop\Machine Learning-Enhanced PC Component Recommendation System\backend\database\users.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop existing tables
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS ratings")

# Recreate users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        email TEXT,
        hashed_password TEXT,
        role TEXT,
        saved_builds TEXT
    )
""")

# Recreate ratings table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        build_id TEXT,
        rating REAL,
        comment TEXT,
        timestamp TEXT
    )
""")

# Commit and close connection
conn.commit()
conn.close()