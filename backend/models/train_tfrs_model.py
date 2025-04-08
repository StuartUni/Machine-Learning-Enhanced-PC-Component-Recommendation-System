# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 28/03/2025
# Description:
# Trains a TensorFlow Recommenders (TFRS) model to learn build preferences from user ratings.
# Can be reused across scripts or executed directly.


import os
import sys
import pandas as pd
import tensorflow as tf
import tensorflow_recommenders as tfrs
from tensorflow.keras import layers
from keras.saving import register_keras_serializable

# ✅ Add backend to sys.path so 'utils' can be resolved when running as standalone
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ✅ This import should now work
from utils.export_ratings_to_csv import export_ratings_to_csv

@register_keras_serializable()
class BuildRankingModel(tfrs.models.Model):
    def __init__(self, user_model=None, build_model=None, rating_model=None, **kwargs):
        super().__init__(**kwargs)
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

    def recommend(self, user_ids, k=5):
        build_ids = tf.convert_to_tensor(self.build_model.layers[0].get_vocabulary())

        user_repeated = tf.repeat(user_ids, len(build_ids))
        build_tiled = tf.tile(build_ids, [len(user_ids)])

        predictions = self({
            "user_id": user_repeated,
            "build_id": build_tiled
        })

        reshaped = tf.reshape(predictions, (len(user_ids), len(build_ids)))
        top_k_values, top_k_indices = tf.math.top_k(reshaped, k=k)
        top_k_build_ids = tf.gather(build_ids, top_k_indices)

        return top_k_values, top_k_build_ids

    def get_config(self):
        return {
            "user_model": tf.keras.utils.serialize_keras_object(self.user_model),
            "build_model": tf.keras.utils.serialize_keras_object(self.build_model),
            "rating_model": tf.keras.utils.serialize_keras_object(self.rating_model)
        }

    @classmethod
    def from_config(cls, config):
        return cls(
            user_model=tf.keras.utils.deserialize_keras_object(config["user_model"]),
            build_model=tf.keras.utils.deserialize_keras_object(config["build_model"]),
            rating_model=tf.keras.utils.deserialize_keras_object(config["rating_model"])
        )


def train_model(csv_path, model_output_path):
    df = pd.read_csv(csv_path)

    user_ids = df["user_id"].astype(str).unique()
    build_ids = df["build_id"].unique()

    ratings = tf.data.Dataset.from_tensor_slices({
        "user_id": df["user_id"].astype(str),
        "build_id": df["build_id"],
        "rating": df["rating"]
    }).shuffle(1000).batch(32)

    user_model = tf.keras.Sequential([
        layers.StringLookup(vocabulary=user_ids, mask_token=None),
        layers.Embedding(len(user_ids) + 1, 32)
    ])

    build_model = tf.keras.Sequential([
        layers.StringLookup(vocabulary=build_ids, mask_token=None),
        layers.Embedding(len(build_ids) + 1, 32)
    ])

    rating_model = tf.keras.Sequential([
        layers.Dense(64, activation="relu"),
        layers.Dense(1)
    ])

    model = BuildRankingModel(user_model, build_model, rating_model)
    model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.05))

    history = model.fit(ratings, epochs=10)

    # Save training plot
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    plt.plot(history.history['loss'])
    plt.title("Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.savefig("backend/models/tfrs_training_loss.png")
    print("📈 Training loss plot saved to: backend/models/tfrs_training_loss.png")

    # Save trained model
    model.save(model_output_path)
    print(f"✅ TFRS model saved to: {model_output_path}")


# ✅ CLI usage support
if __name__ == "__main__":
    DB_PATH = os.path.join("backend", "database", "users.db")
    CSV_PATH = os.path.join("backend", "data", "ratings.csv")
    MODEL_PATH = os.path.join("backend", "models", "tfrs_model.keras")

    LABELED_PATH = os.path.join("backend", "data", "builds", "labeled_builds.csv")
    export_ratings_to_csv(DB_PATH, CSV_PATH, LABELED_PATH)
    train_model(CSV_PATH, MODEL_PATH)