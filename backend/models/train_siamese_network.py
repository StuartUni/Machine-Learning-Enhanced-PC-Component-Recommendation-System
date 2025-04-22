"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script trains a Siamese Neural Network for PC component compatibility prediction.
It:
- Loads preprocessed datasets for CPUs, GPUs, motherboards, RAM, storage, power supplies, and cases.
- Constructs pairs of compatible and incompatible components.
- Trains a Siamese network using TensorFlow/Keras to distinguish compatibility relationships.
- Saves the trained model for integration into the recommendation system.
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

#  Define dataset paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

#  Load preprocessed data 
component_files = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "storage": "preprocessed_filtered_storage.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
}

#  Load datasets with dynamic sampling
dataframes = {}
for key, filename in component_files.items():
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        sample_size = min(len(df), 2000) 
        dataframes[key] = df.sample(sample_size, random_state=42)
        print(f" Loaded {filename} ({len(dataframes[key])} entries)")
    else:
        print(f" Warning: Missing {filename}. Skipping {key}")
        
#  Print column names for each dataset
for key, df in dataframes.items():
    print(f"🔍 Columns in {key}: {df.columns.tolist()}")

#  Adjust Feature Selection to Ensure Uniform Feature Length
def get_features(component, category):
    """Ensures all feature vectors have a uniform length by selecting relevant features and padding missing values."""
    
    if category == "cpu":
        return np.array([component["performance_score"], component["price"], component["tdp"]], dtype=np.float32)
    
    if category == "gpu":
        return np.array([component["performance_score"], component["price"], component["tdp_w"]], dtype=np.float32)
    
    if category == "motherboard":
        return np.array([0, component["price"], 0], dtype=np.float32)  
    
    if category in ["ram_ddr4", "ram_ddr5"]:
        return np.array([component["memory_size_gb"], component["price"], 0], dtype=np.float32) 
    
    if category == "storage":
        return np.array([component["drive_size_gb"], component["price"], 0], dtype=np.float32)  
    
    if category == "power_supply":
        return np.array([component["wattage_w"], component["price"], 0], dtype=np.float32)  
    
    return np.array([0, component["price"], 0], dtype=np.float32) 

#  Define compatibility rules 
def check_compatibility(component1, component2, category1, category2):
    try:
        if category1 == "cpu" and category2 == "motherboard":
            return component1["socket"] == component2["socket"]
        if category1 == "gpu" and category2 == "motherboard":
            return component1["bus_interface"] in component2["storage_support"]
        if category1 in ["cpu", "gpu"] and category2 == "motherboard":
            return component1["performance_score"] >= 0.5  
        if category1 in ["ram_ddr4", "ram_ddr5"] and category2 == "motherboard":
            return component1["memory_type"] in component2["memory_type"] and component1["price"] < component2["price"]
        if category1 == "storage" and category2 == "motherboard":
            return component1["interface_type"] in component2["storage_support"]
        if category1 == "power_supply" and category2 in ["cpu", "gpu"]:
            return component1["wattage_w"] >= (component2.get("tdp", 0) or component2.get("tdp_w", 0))
        return False
    except KeyError:
        return False

#  Generate compatibility pairs 
pairs, labels = [], []
categories = list(dataframes.keys())

print(" Generating compatibility pairs (Expanded)...")
for i, category1 in enumerate(categories):
    for j, category2 in enumerate(categories):
        if i >= j:
            continue  
        
        df1, df2 = dataframes[category1], dataframes[category2]
        df1, df2 = df1.sample(min(len(df1), 800), random_state=42), df2.sample(min(len(df2), 800), random_state=42)  

        for _, comp1 in df1.iterrows():
            for _, comp2 in df2.iterrows():
                pairs.append((get_features(comp1, category1), get_features(comp2, category2)))
                labels.append(1 if check_compatibility(comp1, comp2, category1, category2) else 0)

print(f" Total compatibility pairs generated: {len(pairs)}")

#  Convert to NumPy arrays
X = np.array(pairs, dtype=np.float32)
y = np.array(labels)

#  Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f" Training size: {len(X_train)}, Testing size: {len(X_test)}")

#  Define Siamese Neural Network (
def build_siamese_network(input_shape):
    print(" Building Fully Expanded Siamese Network...")
    input_a, input_b = Input(shape=input_shape), Input(shape=input_shape)

    shared_network = tf.keras.Sequential([
        Dense(256, activation="relu"), 
        Dense(128, activation="relu"),  
        Dense(64, activation="relu"),  
    ])

    encoded_a, encoded_b = shared_network(input_a), shared_network(input_b)

    L1_layer = Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))
    L1_distance = L1_layer([encoded_a, encoded_b])

    output_layer = Dense(1, activation="sigmoid")(L1_distance)
    return Model(inputs=[input_a, input_b], outputs=output_layer)

#  Compile model
print(" Compiling model...")
input_shape = X_train[0][0].shape
siamese_model = build_siamese_network(input_shape)
siamese_model.compile(loss="binary_crossentropy", optimizer=Adam(learning_rate=0.001), metrics=["accuracy"])
print(" Model compiled successfully")

#  Train model 
print(" Training model (Fully Expanded)...")
history = siamese_model.fit(
    [X_train[:, 0], X_train[:, 1]], y_train,
    validation_data=([X_test[:, 0], X_test[:, 1]], y_test),
    epochs=15, batch_size=32  
)
print(" Training complete!")

#  Save model
MODEL_PATH = os.path.join(BASE_DIR, "models/full_siamese_network_model.keras")
siamese_model.save(MODEL_PATH)
print(f" Model saved at {MODEL_PATH}")