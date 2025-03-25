"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script tests the trained Sklearn model for PC component recommendations.
It:
- Loads the trained model and scaler.
- Simulates a user budget.
- Selects components based on price-performance ratio.
- Predicts a recommendation score.
"""

import joblib
import numpy as np
import pandas as pd
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

# ✅ Load Model & Scaler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models/sklearn_recommendation_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models/scaler.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ✅ Define Data Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
component_files = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "storage": "preprocessed_filtered_storage.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "case": "preprocessed_filtered_case.csv",
    "case_fan": "preprocessed_filtered_case_fan.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
}

# ✅ Load Datasets
dataframes = {}
for key, filename in component_files.items():
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        dataframes[key] = pd.read_csv(file_path)
    else:
        print(f"⚠️ Missing {filename}, skipping.")

# ✅ Feature Selection
feature_map = {
    "cpu": ["performance_score", "price"],
    "gpu": ["performance_score", "price"],  
    "ram_ddr4": ["price"],
    "ram_ddr5": ["price"],
    "motherboard": ["price"],
    "storage": ["price"],
    "power_supply": ["price"],
    "case": ["price"],
    "case_fan": ["price"],
    "cpu_cooler": ["price"],
}

# ✅ Prepare Data for Testing
model_data = pd.DataFrame()
for key, features in feature_map.items():
    for feature in features:
        if feature in dataframes[key].columns:
            model_data[f"{key}_{feature}"] = dataframes[key][feature]

# ✅ Add budget column for testing
model_data["budget"] = np.random.randint(500, 5000, size=len(model_data))

# ✅ Normalize Features
model_data_scaled = pd.DataFrame(scaler.transform(model_data), columns=model_data.columns)

# ✅ Define Target Variable
model_data_scaled["user_score"] = (
    model_data_scaled["cpu_performance_score"] * 0.35 +
    model_data_scaled["gpu_performance_score"] * 0.5 +  
    model_data_scaled["budget"] * 0.15
)

# ✅ Train-Test Split
X = model_data_scaled.drop(columns=["user_score"])
y = model_data_scaled["user_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Model Predictions
y_pred = model.predict(X_test)

# ✅ Compute Evaluation Metrics
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

# ✅ Print Performance Metrics
print(f"\n🔹 **Model Evaluation Results**")
print(f"📉 Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"📈 Mean Absolute Error (MAE): {mae:.4f}")