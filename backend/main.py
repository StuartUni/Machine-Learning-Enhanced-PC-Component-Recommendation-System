"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script initializes the FastAPI backend for the PC Component Recommendation System.
It:
- Sets up CORS middleware for frontend communication.
- Includes API routes for recommendations and authentication.
- Runs the FastAPI server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.hybrid import hybrid_router 
from auth.auth import auth_router  
app = FastAPI(
    title="PC Component Recommendation API",
    description="A machine learning-enhanced system for recommending PC components.",
    version="1.0"
)

#  Enable CORS (Adjust frontend URLs in future config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://machine-learning-enhanced-pc-component-iyr1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Include API routes
app.include_router(hybrid_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")  

@app.get("/")
def root():
    """
    Root endpoint to verify that the API is running.
    """
    return {"message": "Welcome to the PC Component Recommendation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)