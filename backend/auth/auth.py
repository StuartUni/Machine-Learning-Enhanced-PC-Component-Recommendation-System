"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025
Description:
This module handles user authentication and saved build logic using FastAPI.
It:
- Registers users with hashed passwords
- Verifies login credentials
- Generates and returns JWT tokens on successful login
- Provides access to user profile (protected route)
- Allows authenticated users to save and retrieve a PC build
"""

from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
import sqlite3
import json

from .schemas import UserCreate, UserResponse
from .hashing import Hasher  
from .jwt_handler import create_access_token, get_current_user
from .database import get_db_connection
from .schemas import BuildRating
from datetime import datetime
from .schemas import UserUpdate

router = APIRouter(tags=["Authentication"])

# ✅ REGISTER ROUTE
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user.username, user.email))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    # ✅ Hash password and insert new user
    hashed_pw = Hasher.hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role, saved_builds) VALUES (?, ?, ?, ?, ?)",
        (user.username, user.email, hashed_pw, user.role or "user", "")
    )
    conn.commit()
    conn.close()

    user_id = cursor.lastrowid  # Get auto-incremented ID
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role or "user"
    }

# ✅ LOGIN ROUTE
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not Hasher.verify_password(form_data.password, user[3]):  # user[3] is hashed_password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={"sub": user[1]})  # user[1] is username
    return {"access_token": token, "token_type": "bearer"}


# ✅ PATCH: Update profile
@router.patch("/auth/update-profile")
def update_profile(updates: UserUpdate, current_user: dict = Depends(get_current_user)):
    """
    Allows authenticated users to update their profile (username, email, password).
    Checks for uniqueness on username and email updates.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    updated_fields = []
    params = []

    # ✅ Check if new username is already taken
    if updates.username:
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (updates.username, current_user["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken by another user.")
        updated_fields.append("username = ?")
        params.append(updates.username)

    # ✅ Check if new email is already taken
    if updates.email:
        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (updates.email, current_user["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered by another user.")
        updated_fields.append("email = ?")
        params.append(updates.email)

    # ✅ Password update with current password verification
    if updates.new_password:
        if not updates.current_password:
            raise HTTPException(status_code=400, detail="Current password is required to set a new password.")

        cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (current_user["id"],))
        hashed_pw = cursor.fetchone()[0]

        if not Hasher.verify_password(updates.current_password, hashed_pw):
            raise HTTPException(status_code=401, detail="Current password is incorrect.")

        new_hashed = Hasher.hash_password(updates.new_password)
        updated_fields.append("hashed_password = ?")
        params.append(new_hashed)

    if not updated_fields:
        raise HTTPException(status_code=400, detail="No updates provided.")

    # ✅ Finalize update query
    params.append(current_user["id"])
    update_query = f"UPDATE users SET {', '.join(updated_fields)} WHERE id = ?"
    cursor.execute(update_query, tuple(params))

    conn.commit()
    conn.close()

    return {"message": "✅ Profile updated successfully."}

# ✅ DELETE: USER DELETES THEIR OWN ACCOUNT
@router.delete("/auth/delete-account")
def delete_own_account(current_user: dict = Depends(get_current_user)):
    """
    Allows a user to delete their own account and associated data (including ratings).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete user ratings first (if any)
    cursor.execute("DELETE FROM ratings WHERE user_id = ?", (current_user["id"],))

    # Delete user account
    cursor.execute("DELETE FROM users WHERE id = ?", (current_user["id"],))
    conn.commit()
    conn.close()

    return {"message": f"✅ Your account '{current_user['username']}' has been deleted."}



# ✅ PROTECTED TEST ROUTE
@router.get("/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Returns the current logged-in user's information.
    This route is protected and requires a valid JWT token.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()
    conn.close()

    saved_builds = json.loads(result[0]) if result and result[0] else None

    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"],
        "saved_builds": saved_builds
    }
# ✅ SAVE BUILD ROUTE
@router.post("/save_build")
def save_build(build: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Saves a recommended build to the user's account.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Serialize and save build as JSON
    build_json = json.dumps(build)
    cursor.execute("UPDATE users SET saved_builds = ? WHERE username = ?", (build_json, current_user["username"]))
    conn.commit()
    conn.close()

    return {"message": "✅ Build saved successfully!"}

# ✅ GET SAVED BUILDS ROUTE
@router.get("/my_builds")
def get_saved_build(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the saved PC build for the current user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()
    conn.close()

    if not result or not result[0]:
        return {"message": "⚠️ No saved build found."}

    build_data = json.loads(result[0])
    return {"saved_build": build_data}

# ✅ RATE BUILD ENDPOINT
@router.post("/rate-build")
def rate_build(rating: BuildRating, current_user: dict = Depends(get_current_user)):
    """
    Allows a user to rate a build they've interacted with.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Insert new rating into the ratings table
    cursor.execute('''
        INSERT INTO ratings (user_id, build_id, rating, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (
        current_user["id"],
        rating.build_id,
        rating.rating,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return {"message": f"✅ Rating submitted for build {rating.build_id} with score {rating.rating}"}

# ✅ GET USER RATINGS ROUTE
@router.get("/get-ratings")
def get_user_ratings(current_user: dict = Depends(get_current_user)):
    """
    Retrieves all build ratings submitted by the currently authenticated user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT build_id, rating, comment, timestamp
        FROM ratings
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (current_user["id"],))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"message": "⚠️ No ratings found for this user."}

    ratings = [
        {
            "build_id": row[0],
            "rating": row[1],
            "comment": row[2],
            "timestamp": row[3]
        }
        for row in rows
    ]

    return {"user": current_user["username"], "ratings": ratings}

# ✅ DELETE: USER DELETES THEIR OWN RATING
@router.delete("/auth/delete-rating/{build_id}")
def delete_own_rating(build_id: str, current_user: dict = Depends(get_current_user)):
    """
    Allows a user to delete their own rating for a specific build.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ratings WHERE user_id = ? AND build_id = ?",
        (current_user["id"], build_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Rating not found or already deleted.")

    return {"message": f"✅ Rating for build '{build_id}' deleted."}


# ✅ ADMIN: GET ALL RATINGS
@router.get("/admin/ratings")
def get_all_ratings(current_user: dict = Depends(get_current_user)):
    """
    Allows admin users to view all submitted build ratings.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, build_id, rating, comment, timestamp
        FROM ratings
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"message": "⚠️ No ratings have been submitted yet."}

    ratings = [
        {
            "user_id": row[0],
            "build_id": row[1],
            "rating": row[2],
            "comment": row[3],
            "timestamp": row[4]
        }
        for row in rows
    ]

    return {"total_ratings": len(ratings), "ratings": ratings}

# ✅ ADMIN: DELETE ANY RATING
@router.delete("/admin/delete-rating")
def delete_any_rating(user_id: int, build_id: str, current_user: dict = Depends(get_current_user)):
    """
    Allows an admin to delete a specific rating by user_id and build_id.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM ratings WHERE user_id = ? AND build_id = ?",
        (user_id, build_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Rating not found.")

    return {"message": f"✅ Rating for build '{build_id}' by user {user_id} deleted."}

# ✅ ADMIN: DELETE ALL RATINGS
@router.delete("/admin/delete-all-ratings")
def delete_all_ratings(current_user: dict = Depends(get_current_user)):
    """
    Allows an admin to delete all ratings from the database.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ratings")
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return {"message": f"🗑️ All {deleted} rating(s) deleted from the database."}

# ✅ ADMIN: DELETE ANY USER ACCOUNT
@router.delete("/admin/delete-user/{user_id}")
def delete_user_account(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Allows an admin to delete any user account and their ratings.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # First check if the user exists
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")

    username_to_delete = result[0]

    # Delete their ratings
    cursor.execute("DELETE FROM ratings WHERE user_id = ?", (user_id,))

    # Delete user account
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": f"🗑️ User '{username_to_delete}' (ID {user_id}) and their data have been deleted."}

# ✅ Export router for main.py
auth_router = router