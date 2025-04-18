import sqlite3

# Path to your users.db
db_path = r'C:\Users\Stuart\Desktop\Machine Learning-Enhanced PC Component Recommendation System\backend\database\users.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the tables if they exist
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS ratings")

# Recreate the users table (adjust schema as needed)
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

# Recreate the ratings table
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

# Commit changes and close the connection
conn.commit()
conn.close()

print("✅ Tables wiped and recreated successfully!")
