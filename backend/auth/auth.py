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
- Allows authenticated users to save, retrieve and delete multiple PC builds.
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

from pydantic import BaseModel

# ✅ Create a simple Pydantic model
class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter(tags=["Authentication"])

# ✅ REGISTER ROUTE
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (user.username, user.email))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    hashed_pw = Hasher.hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role, saved_builds) VALUES (?, ?, ?, ?, ?)",
        (user.username, user.email, hashed_pw, user.role or "user", json.dumps([]))
    )
    conn.commit()
    conn.close()

    user_id = cursor.lastrowid
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role or "user"
    }

# ✅ LOGIN ROUTE
@router.post("/login")
def login(form_data: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not Hasher.verify_password(form_data.password, user[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={"sub": user[1]})
    return {"access_token": token, "token_type": "bearer"}

# ✅ UPDATE PROFILE ROUTE
@router.patch("/auth/update-profile")
def update_profile(updates: UserUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    updated_fields = []
    params = []

    if updates.username:
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (updates.username, current_user["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken by another user.")
        updated_fields.append("username = ?")
        params.append(updates.username)

    if updates.email:
        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (updates.email, current_user["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered by another user.")
        updated_fields.append("email = ?")
        params.append(updates.email)

    if updates.new_password:
        if not updates.current_password:
            raise HTTPException(status_code=400, detail="Current password is required.")
        cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (current_user["id"],))
        hashed_pw = cursor.fetchone()[0]
        if not Hasher.verify_password(updates.current_password, hashed_pw):
            raise HTTPException(status_code=401, detail="Current password is incorrect.")
        new_hashed = Hasher.hash_password(updates.new_password)
        updated_fields.append("hashed_password = ?")
        params.append(new_hashed)

    if not updated_fields:
        raise HTTPException(status_code=400, detail="No updates provided.")

    params.append(current_user["id"])
    update_query = f"UPDATE users SET {', '.join(updated_fields)} WHERE id = ?"
    cursor.execute(update_query, tuple(params))

    conn.commit()
    conn.close()

    return {"message": "✅ Profile updated successfully."}

# ✅ DELETE OWN ACCOUNT
@router.delete("/auth/delete-account")
def delete_own_account(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ratings WHERE user_id = ?", (current_user["id"],))
    cursor.execute("DELETE FROM users WHERE id = ?", (current_user["id"],))
    conn.commit()
    conn.close()

    return {"message": f"✅ Your account '{current_user['username']}' has been deleted."}

# ✅ GET PROFILE ROUTE
@router.get("/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()
    conn.close()

    saved_builds = json.loads(result[0]) if result and result[0] else []

    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"],
        "saved_builds": saved_builds
    }

# ✅ SAVE MULTIPLE BUILDS
@router.post("/save_build")
def save_build(build: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()

    existing_builds = []
    if result and result[0]:
        try:
            existing_builds = json.loads(result[0])
            if isinstance(existing_builds, dict):
                existing_builds = [existing_builds]
        except:
            existing_builds = []

    existing_builds.append(build)

    cursor.execute("UPDATE users SET saved_builds = ? WHERE username = ?", (json.dumps(existing_builds), current_user["username"]))
    conn.commit()
    conn.close()

    return {"message": "✅ Build saved successfully!"}

# ✅ GET MULTIPLE SAVED BUILDS
@router.get("/my_builds")
def get_saved_builds(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()
    conn.close()

    if not result or not result[0]:
        return {"saved_builds": []}

    try:
        builds = json.loads(result[0])
        if isinstance(builds, dict):
            builds = [builds]
    except:
        builds = []

    return {"saved_builds": builds}

# ✅ DELETE SAVED BUILD
@router.delete("/delete_build/{build_id}")
def delete_saved_build(build_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saved_builds FROM users WHERE username = ?", (current_user["username"],))
    result = cursor.fetchone()

    if not result or not result[0]:
        conn.close()
        raise HTTPException(status_code=404, detail="No saved builds found.")

    saved_builds = json.loads(result[0])
    if isinstance(saved_builds, dict):
        saved_builds = [saved_builds]

    updated_builds = [b for b in saved_builds if b.get("build_id") != build_id]

    if len(updated_builds) == len(saved_builds):
        conn.close()
        raise HTTPException(status_code=404, detail="Build not found.")

    cursor.execute("UPDATE users SET saved_builds = ? WHERE username = ?", (json.dumps(updated_builds), current_user["username"]))
    conn.commit()
    conn.close()

    return {"message": f"✅ Build '{build_id}' deleted successfully."}

# ✅ RATE BUILD
@router.post("/rate-build")
def rate_build(rating: BuildRating, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM ratings WHERE user_id = ? AND build_id = ?', (current_user["id"], rating.build_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('''
            UPDATE ratings
            SET rating = ?, timestamp = ?
            WHERE user_id = ? AND build_id = ?
        ''', (rating.rating, datetime.utcnow().isoformat(), current_user["id"], rating.build_id))
        message = f"✅ Updated rating for build {rating.build_id}."
    else:
        cursor.execute('''
            INSERT INTO ratings (user_id, build_id, rating, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (current_user["id"], rating.build_id, rating.rating, datetime.utcnow().isoformat()))
        message = f"✅ New rating submitted for build {rating.build_id}."

    conn.commit()
    conn.close()

    return {"message": message}

# ✅ GET USER RATINGS
@router.get("/get-ratings")
def get_user_ratings(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT build_id, rating, comment, timestamp
        FROM ratings
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (current_user["id"],))

    rows = cursor.fetchall()
    conn.close()

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

# ✅ Export router
auth_router = router