# 📋 Fancy Mini Showcase of Top-10 Recommendations for One User
# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-18
# Description:
# Displays a formatted table of top-10 recommended PC builds for a selected user.

import os
import sys
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tabulate import tabulate  # ✅ NEW: for pretty tables

# ✅ Fix paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.train_tfrs_model import BuildRankingModel

# ✅ Correct model and CSV paths
MODEL_PATH = os.path.join(BACKEND_DIR, "models", "tfrs_model.keras")
BUILDS_CSV_PATH = os.path.join(BACKEND_DIR, "data", "builds", "labeled_builds.csv")

# ✅ Load the model
model = keras.models.load_model(
    MODEL_PATH,
    custom_objects={"BuildRankingModel": BuildRankingModel}
)

# ✅ Load the builds
builds_df = pd.read_csv(BUILDS_CSV_PATH)

# ✅ Choose the user
user_id = "27"  # <-- Adjust if you want another user

# ✅ Recommend top-10 build IDs
_, top_build_ids = model.recommend(tf.constant([user_id]), k=10)
top_build_ids = [b.decode() for b in top_build_ids[0].numpy()]

# ✅ Collect builds for table
rows = []

for build_id in top_build_ids:
    build = builds_df[builds_df["build_id"] == build_id]
    if not build.empty:
        build_info = build.iloc[0]
        rows.append([
            build_info['build_id'],
            build_info['cpu_name'],
            build_info['gpu_name'],
            build_info['ram_name'],
            build_info['storage_name'],
            f"${build_info['price']:.2f}"
        ])

# ✅ Display as a neat table
print(f"\n👤 Top-10 Recommendations for User {user_id}:\n")
headers = ["Build ID", "CPU", "GPU", "RAM", "Storage", "Total Price"]
print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))