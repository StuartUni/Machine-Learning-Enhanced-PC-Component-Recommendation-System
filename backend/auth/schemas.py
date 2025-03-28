"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 27/03/2025
Description:
This module defines Pydantic models for validating and structuring
user-related data in the authentication system.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

# ✅ Base User schema (shared fields)
class UserBase(BaseModel):
    username: str
    email: EmailStr

# ✅ Request schema for registration
class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"  # Default role is 'user'

# ✅ Request schema for login
class UserLogin(BaseModel):
    username: str
    password: str

# ✅ Response schema for API (excludes password)
class UserResponse(UserBase):
    id: int
    role: str
    saved_builds: Optional[Dict[str, Any]] = None  # Optional field for saved builds

    class Config:
        orm_mode = True
        
# ✅ Request schema for submitting a build rating
class BuildRating(BaseModel):
    build_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None
    

# ✅ Request schema for updating user profile
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None  # Required only if updating password