"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-02
Description:
This module loads a trained TensorFlow Recommenders (TFRS) collaborative filtering model.
Features:
- Loads the trained TFRS model from disk
- Provides top-k build recommendations for a given user ID
- Handles potential errors when rebuilding the model index or making predictions
"""

import os
import tensorflow as tf
import numpy as np
from typing import List

#  Define model path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tfrs_model")  

#  Load TFRS model
def load_tfrs_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f" TFRS model not found at: {MODEL_PATH}")
    return tf.keras.models.load_model(MODEL_PATH)

#  Generate build recommendations for a given user ID
def recommend_builds(user_id: str, model=None, k: int = 10) -> List[str]:
    """
    Generates top-k build recommendations for a user.
    Returns a list of build IDs (strings).
    """
    if model is None:
        model = load_tfrs_model()

    #  Build index if using retrieval model
    try:
        model.index.rebuild()
    except Exception as e:
        print(" Could not rebuild model index:", e)

    try:
        scores, build_ids = model.recommend(user_id, k=k)
        return build_ids.numpy().tolist()
    except Exception as e:
        print(f" Error generating recommendations for user {user_id}: {e}")
        return []