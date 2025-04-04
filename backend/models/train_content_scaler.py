# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-04
# Description:
# Trains and saves a MinMaxScaler using the labeled_builds.csv file.
# This scaler is specifically for use in content_recommender.py which uses:
# 'cpu_score', 'gpu_score', 'ram_gb', 'storage_gb', 'price'

import os
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler

# ✅ Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "builds", "labeled_builds.csv")
SCALER_PATH = os.path.join(BASE_DIR, "models", "content_scaler.pkl")

# ✅ Load build data
df = pd.read_csv(DATA_PATH)

# ✅ Select relevant feature columns
FEATURES = ["cpu_score", "gpu_score", "ram_gb", "storage_gb", "price"]
if not all(col in df.columns for col in FEATURES):
    raise ValueError("❌ One or more required columns are missing from labeled_builds.csv")

X = df[FEATURES]

# ✅ Fit scaler
scaler = MinMaxScaler()
scaler.fit(X)

# ✅ Save the scaler
joblib.dump(scaler, SCALER_PATH)
print("✅ Content-based scaler trained and saved to models/content_scaler.pkl")