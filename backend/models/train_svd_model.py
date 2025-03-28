# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 28/03/2025
# Description:
# Trains an SVD collaborative filtering model using user ratings from the database.
# Evaluates model performance using RMSE, Precision@K, and Recall@K.
# Saves the trained model for future recommendation use.

import os
import sqlite3
import pandas as pd
import pickle
from collections import defaultdict
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

# ✅ Load ratings from SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "users.db")

def load_ratings():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT user_id, build_id, rating FROM ratings"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ✅ Precision@K and Recall@K calculation
def get_top_n(predictions, n=5):
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n

def precision_recall_at_k(predictions, k=5, threshold=3.5):
    top_n = get_top_n(predictions, n=k)

    precisions = {}
    recalls = {}

    for uid, user_ratings in top_n.items():
        n_rel = sum((true_r >= threshold) for (_, iid_, true_r, _, _) in predictions if uid == _[0])
        n_rec_k = len(user_ratings)
        n_rel_and_rec_k = sum((true_r >= threshold) for (iid, _) in user_ratings for (_, iid_, true_r, _, _) in predictions if uid == _[0] and iid_ == iid)

        precision = n_rel_and_rec_k / n_rec_k if n_rec_k else 0
        recall = n_rel_and_rec_k / n_rel if n_rel else 0

        precisions[uid] = precision
        recalls[uid] = recall

    avg_precision = sum(precisions.values()) / len(precisions)
    avg_recall = sum(recalls.values()) / len(recalls)

    return avg_precision, avg_recall

# ✅ Load and prepare dataset
df = load_ratings()
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[["user_id", "build_id", "rating"]], reader)

# ✅ Train/test split
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# ✅ Train SVD model
model = SVD()
model.fit(trainset)

# ✅ Evaluate performance
predictions = model.test(testset)
rmse = accuracy.rmse(predictions)
precision, recall = precision_recall_at_k(predictions, k=5, threshold=3.5)

print(f"\n📊 Evaluation Results:")
print(f"📈 RMSE: {rmse:.4f}")
print(f"📈 Precision@5: {precision:.4f}")
print(f"📈 Recall@5: {recall:.4f}\n")

# ✅ Save model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "svd_model.pkl")
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"✅ SVD model trained and saved to: {MODEL_PATH}")