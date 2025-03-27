"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025
Description:
This script handles JWT (JSON Web Token) creation and verification for user authentication.
It:
- Generates a secure access token with an expiry time
- Decodes and verifies tokens for protected route access
- Provides a get_current_user dependency to protect private API endpoints
"""

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # ✅ Using python-jose for FastAPI integration
from .database import get_db_connection

# ✅ Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key_here"  # Consider loading from env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ✅ OAuth2 scheme for extracting token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict):
    """Generates a JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Decodes and validates a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates JWT token and returns current user data from the DB"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ Fetch user from DB by username
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[4]
    }