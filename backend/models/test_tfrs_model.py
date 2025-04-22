"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 30/03/2025
Description:
This script evaluates a trained TensorFlow Recommenders (TFRS) model.
Features:
- Loads the saved TFRS model from disk
- Loads user build ratings from the SQLite database
- Evaluates the model using Precision@10 and NDCG@10 metrics
- Prints key evaluation results to the console
- Helps diagnose prediction quality with batch-level debug output
"""

import sys
import os
import sqlite3
import pandas as pd
import tensorflow as tf
import tensorflow_recommenders as tfrs


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
    
from models.train_tfrs_model import BuildRankingModel

#  Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "tfrs_model.keras")

#  Load ratings
def load_ratings():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT user_id, build_id, rating FROM ratings", conn)
    conn.close()
    return df

df = load_ratings()
df["user_id"] = df["user_id"].astype(str)
df["build_id"] = df["build_id"].astype(str)

#  Load trained model
model = tf.keras.models.load_model(
    MODEL_PATH, custom_objects={"BuildRankingModel": BuildRankingModel}
)

#  Create test dataset
test_data = tf.data.Dataset.from_tensor_slices({
    "user_id": df["user_id"],
    "build_id": df["build_id"],
    "rating": df["rating"]
}).batch(1)

#  Evaluation
def evaluate_model(model, test_data, k=5):
    hits, ndcgs = [], []

    print("\n🔍 Starting evaluation...\n")
    for batch in test_data:
        user_id = batch["user_id"].numpy()[0].decode()
        true_build_id = batch["build_id"].numpy()[0].decode()

        _, build_ids = model.recommend(tf.constant([user_id]), k=k)
        build_ids = [b.decode() for b in build_ids[0].numpy()] 

        print(f" User: {user_id}")
        print(f" True Build ID: {true_build_id}")
        print(f" Predicted Top-{k} Build IDs: {build_ids}\n")

        hit = true_build_id in build_ids
        hits.append(hit)

        if hit:
            rank = list(build_ids).index(true_build_id) + 1
            ndcg = tf.math.log(2.0) / tf.math.log(tf.cast(rank + 1, tf.float32))
        else:
            ndcg = 0.0
        ndcgs.append(ndcg)

    precision_at_k = sum(hits) / len(hits)
    ndcg_at_k = sum(ndcgs) / len(ndcgs)
    return precision_at_k, ndcg_at_k

#  Run and print results
precision, ndcg = evaluate_model(model, test_data, k=10)
print(f"\n Precision@10: {precision:.4f}")
print(f" NDCG@10: {ndcg:.4f}")

