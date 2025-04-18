# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-10
# Description:
# This FastAPI router connects the frontend to the hybrid_recommender system.
# It processes POST requests and returns hybrid model recommendations.

from fastapi import APIRouter
from recommender.hybrid_recommender import get_hybrid_recommendation

hybrid_router = APIRouter()

@hybrid_router.post("/recommend")
def hybrid_recommendation_handler(user_input: dict):
    return get_hybrid_recommendation(user_input)