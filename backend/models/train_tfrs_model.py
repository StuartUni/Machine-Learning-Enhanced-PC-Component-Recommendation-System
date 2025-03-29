# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 28/03/2025
# Description:
# Trains a TensorFlow Recommenders (TFRS) model to learn build preferences from user ratings.

import os
import sqlite3
import pandas as pd
import tensorflow as tf
import tensorflow_recommenders as tfrs
from tensorflow.keras import layers

# ✅ Load data from SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# NEW ✅ Absolute safe path from project root
DB_PATH = os.path.abspath("backend/database/users.db")
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT user_id, build_id, rating FROM ratings", conn)
conn.close()

# ✅ Prepare unique vocabularies
user_ids = df["user_id"].astype(str).unique()
build_ids = df["build_id"].unique()

# ✅ TensorFlow Datasets
ratings = tf.data.Dataset.from_tensor_slices({
    "user_id": df["user_id"].astype(str),
    "build_id": df["build_id"],
    "rating": df["rating"]
})

# ✅ Shuffle + batch
ratings = ratings.shuffle(1000).batch(32)

# ✅ User and Build Embedding Models
user_model = tf.keras.Sequential([
    layers.StringLookup(vocabulary=user_ids, mask_token=None),
    layers.Embedding(len(user_ids) + 1, 32)
])

build_model = tf.keras.Sequential([
    layers.StringLookup(vocabulary=build_ids, mask_token=None),
    layers.Embedding(len(build_ids) + 1, 32)
])

# ✅ Rating Prediction Task
rating_model = tf.keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(1)
])

# ✅ Custom TFRS model
class BuildRankingModel(tfrs.models.Model):
    def __init__(self, user_model, build_model, rating_model):
        super().__init__()
        self.user_model = user_model
        self.build_model = build_model
        self.rating_model = rating_model
        self.task = tfrs.tasks.Ranking(
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=[tf.keras.metrics.RootMeanSquaredError()]
        )

    def call(self, features):
        user_embeddings = self.user_model(features["user_id"])
        build_embeddings = self.build_model(features["build_id"])
        return self.rating_model(tf.concat([user_embeddings, build_embeddings], axis=1))

    def compute_loss(self, features, training=False):
        labels = features["rating"]
        predictions = self(features)
        return self.task(labels=labels, predictions=predictions)

# ✅ Compile + Train
model = BuildRankingModel(user_model, build_model, rating_model)
model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))
model.fit(ratings, epochs=10)

# ✅ Save model
model_path = os.path.abspath("backend/models/tfrs_model.keras")
model.save(model_path)
print(f"✅ TFRS model saved to: {model_path}")