"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script trains the Sklearn-based recommendation model for PC component selection.
It:
- Loads the fully preprocessed component datasets.
- Normalizes feature data using MinMaxScaler.
- Trains a RandomForestRegressor for predicting the best component configurations.
- Saves the trained model and scaler for future predictions.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import os

#  Define dataset paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

#  Load preprocessed data
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

#  Load datasets into a dictionary
dataframes = {}
for key, filename in component_files.items():
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        dataframes[key] = pd.read_csv(file_path)
        print(f" Loaded {filename}")
    else:
        print(f" Warning: Missing {filename}. Skipping {key}")

#  Ensure all datasets have a `price` column
for key, df in dataframes.items():
    if "price" not in df.columns:
        raise ValueError(f" Dataset {key} is missing a 'price' column!")

#  Define relevant features for model training
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

#  Ensure all datasets have the required length
min_length = min(len(df) for df in dataframes.values())
for key in dataframes:
    dataframes[key] = dataframes[key].sample(min_length, random_state=42).reset_index(drop=True)

#  Feature Selection and Combination
model_data = pd.DataFrame()

for key, features in feature_map.items():
    for feature in features:
        if feature in dataframes[key].columns:
            model_data[f"{key}_{feature}"] = dataframes[key][feature]

#  Add budget as a feature (simulate budget range for training)
model_data["budget"] = np.random.randint(500, 5000, size=min_length)

#  Normalize data using MinMaxScaler
scaler = MinMaxScaler()
model_data_scaled = pd.DataFrame(scaler.fit_transform(model_data), columns=model_data.columns)

#  Save the scaler
joblib.dump(scaler, os.path.join(BASE_DIR, "models/scaler.pkl"))

#  Define the target variable (user score based on component performance)
model_data_scaled["user_score"] = (
    model_data_scaled["cpu_performance_score"] * 0.35 +
    model_data_scaled["gpu_performance_score"] * 0.5 +
    model_data_scaled["budget"] * 0.15
)

#  Train model
X = model_data_scaled.drop(columns=["user_score"])
y = model_data_scaled["user_score"]
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

#  Save model
joblib.dump(model, os.path.join(BASE_DIR, "models/sklearn_recommendation_model.pkl"))

print(" Model training complete and saved!")