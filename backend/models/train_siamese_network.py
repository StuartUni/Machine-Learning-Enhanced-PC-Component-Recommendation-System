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

# import os
# import numpy as np
# import pandas as pd
# import tensorflow as tf
# from tensorflow.keras.layers import Input, Dense, Lambda
# from tensorflow.keras.models import Model
# from tensorflow.keras.optimizers import Adam
# from sklearn.model_selection import train_test_split

# # ✅ Define dataset paths
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(BASE_DIR, "data")

# # ✅ Load preprocessed data
# component_files = {
#     "cpu": "preprocessed_filtered_cpu.csv",
#     "gpu": "preprocessed_filtered_gpu.csv",
#     "motherboard": "preprocessed_filtered_motherboard.csv",
#     "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
#     "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
#     "storage": "preprocessed_filtered_storage.csv",
#     "power_supply": "preprocessed_filtered_power_supply.csv",
#     "case": "preprocessed_filtered_case.csv",
# }

# # ✅ Load datasets
# dataframes = {}
# for key, filename in component_files.items():
#     file_path = os.path.join(DATA_DIR, filename)
#     if os.path.exists(file_path):
#         dataframes[key] = pd.read_csv(file_path)
#         print(f"✅ Loaded {filename} ({len(dataframes[key])} entries)")
#     else:
#         print(f"⚠️ Warning: Missing {filename}. Skipping {key}")

# # ✅ Define compatibility rules
# def check_compatibility(component1, component2, category1, category2):
#     """ Determines compatibility between two components based on category. """
#     try:
#         if category1 == "cpu" and category2 == "motherboard":
#             return component1["socket"] == component2["socket"]
#         if category1 in ["ram_ddr4", "ram_ddr5"] and category2 == "motherboard":
#             return component1["memory_size_gb"] <= component2["max_memory_gb"] and component1["memory_type"] in component2["memory_type"]
#         if category1 == "gpu" and category2 == "motherboard":
#             return component1["bus_interface"] in component2["storage_support"]
#         if category1 == "storage" and category2 == "motherboard":
#             return component1["interface_type"] in component2["storage_support"]
#         if category1 == "power_supply" and category2 in ["cpu", "gpu"]:
#             return component1["wattage_w"] >= (component2.get("tdp", 0) or component2.get("tdp_w", 0))
#         return False
#     except KeyError as e:
#         print(f"❌ KeyError: {e} - Check if column names match in dataset")
#         return False

# # ✅ Generate compatibility pairs
# pairs = []
# labels = []
# categories = list(dataframes.keys())

# print("🔄 Generating compatibility pairs...")
# for i, category1 in enumerate(categories):
#     for j, category2 in enumerate(categories):
#         if i >= j:
#             continue  # Avoid duplicate and self-pairing

#         df1, df2 = dataframes[category1], dataframes[category2]
#         print(f"🔍 Matching {category1} ({len(df1)}) with {category2} ({len(df2)})")

#         count = 0  # Track pair generation progress
#         for _, comp1 in df1.iterrows():
#             for _, comp2 in df2.iterrows():
#                 pairs.append((comp1.to_numpy(), comp2.to_numpy()))
#                 labels.append(1 if check_compatibility(comp1, comp2, category1, category2) else 0)
#                 count += 1
#                 if count % 5000 == 0:
#                     print(f"✅ {count} pairs processed...")

# print(f"✅ Total compatibility pairs generated: {len(pairs)}")

# # ✅ Convert to NumPy arrays
# try:
#     X = np.array(pairs, dtype=object)
#     y = np.array(labels)
#     print("✅ Data successfully converted to NumPy arrays")
# except Exception as e:
#     print(f"❌ Error converting to NumPy: {e}")

# # ✅ Train-test split
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# print(f"✅ Training size: {len(X_train)}, Testing size: {len(X_test)}")

# # ✅ Define Siamese Neural Network
# def build_siamese_network(input_shape):
#     print("🛠 Building Siamese Network...")
#     input_a = Input(shape=input_shape)
#     input_b = Input(shape=input_shape)

#     shared_network = tf.keras.Sequential([
#         Dense(128, activation="relu"),
#         Dense(64, activation="relu"),
#         Dense(32, activation="relu"),
#     ])

#     encoded_a = shared_network(input_a)
#     encoded_b = shared_network(input_b)

#     # Compute absolute difference
#     L1_layer = Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))
#     L1_distance = L1_layer([encoded_a, encoded_b])

#     # Final output layer
#     output_layer = Dense(1, activation="sigmoid")(L1_distance)

#     model = Model(inputs=[input_a, input_b], outputs=output_layer)
#     return model

# # ✅ Compile model
# print("🔄 Compiling model...")
# input_shape = X_train[0][0].shape
# siamese_model = build_siamese_network(input_shape)
# siamese_model.compile(loss="binary_crossentropy", optimizer=Adam(learning_rate=0.001), metrics=["accuracy"])
# print("✅ Model compiled successfully")

# # ✅ Train model with progress updates
# print("🚀 Training model...")
# history = siamese_model.fit(
#     [X_train[:, 0], X_train[:, 1]], y_train,
#     validation_data=([X_test[:, 0], X_test[:, 1]], y_test),
#     epochs=10, batch_size=32
# )
# print("✅ Training complete!")

# # ✅ Save model
# MODEL_PATH = os.path.join(BASE_DIR, "models/siamese_network_model.h5")
# siamese_model.save(MODEL_PATH)
# print(f"✅ Model saved at {MODEL_PATH}")


import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# ✅ Define dataset paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Load preprocessed data (🔼 Expanded to include RAM, Storage, and Power Supply)
component_files = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "storage": "preprocessed_filtered_storage.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
}

# ✅ Load datasets with dynamic sampling
dataframes = {}
for key, filename in component_files.items():
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        sample_size = min(len(df), 2000)  # 🔼 Increased sample size from 1000 → 2000
        dataframes[key] = df.sample(sample_size, random_state=42)
        print(f"✅ Loaded {filename} ({len(dataframes[key])} entries)")
    else:
        print(f"⚠️ Warning: Missing {filename}. Skipping {key}")
        
# ✅ Print column names for each dataset
for key, df in dataframes.items():
    print(f"🔍 Columns in {key}: {df.columns.tolist()}")

# ✅ Adjust Feature Selection to Ensure Uniform Feature Length
def get_features(component, category):
    """Ensures all feature vectors have a uniform length by selecting relevant features and padding missing values."""
    
    if category == "cpu":
        return np.array([component["performance_score"], component["price"], component["tdp"]], dtype=np.float32)
    
    if category == "gpu":
        return np.array([component["performance_score"], component["price"], component["tdp_w"]], dtype=np.float32)
    
    if category == "motherboard":
        return np.array([0, component["price"], 0], dtype=np.float32)  # ✅ No performance score, TDP padded with 0
    
    if category in ["ram_ddr4", "ram_ddr5"]:
        return np.array([component["memory_size_gb"], component["price"], 0], dtype=np.float32)  # ✅ No TDP, pad with 0
    
    if category == "storage":
        return np.array([component["drive_size_gb"], component["price"], 0], dtype=np.float32)  # ✅ No TDP, pad with 0
    
    if category == "power_supply":
        return np.array([component["wattage_w"], component["price"], 0], dtype=np.float32)  # ✅ No performance score, pad with 0
    
    return np.array([0, component["price"], 0], dtype=np.float32)  # ✅ Default to padding

# ✅ Define compatibility rules (🔼 Expanded to include RAM, Storage, and PSU)
def check_compatibility(component1, component2, category1, category2):
    try:
        if category1 == "cpu" and category2 == "motherboard":
            return component1["socket"] == component2["socket"]
        if category1 == "gpu" and category2 == "motherboard":
            return component1["bus_interface"] in component2["storage_support"]
        if category1 in ["cpu", "gpu"] and category2 == "motherboard":
            return component1["performance_score"] >= 0.5  # 🔼 Added additional filtering based on performance
        if category1 in ["ram_ddr4", "ram_ddr5"] and category2 == "motherboard":
            return component1["memory_type"] in component2["memory_type"] and component1["price"] < component2["price"]
        if category1 == "storage" and category2 == "motherboard":
            return component1["interface_type"] in component2["storage_support"]
        if category1 == "power_supply" and category2 in ["cpu", "gpu"]:
            return component1["wattage_w"] >= (component2.get("tdp", 0) or component2.get("tdp_w", 0))
        return False
    except KeyError:
        return False

# ✅ Generate compatibility pairs (🔼 Increased to 800 per category)
pairs, labels = [], []
categories = list(dataframes.keys())

print("🔄 Generating compatibility pairs (Expanded)...")
for i, category1 in enumerate(categories):
    for j, category2 in enumerate(categories):
        if i >= j:
            continue  
        
        df1, df2 = dataframes[category1], dataframes[category2]
        df1, df2 = df1.sample(min(len(df1), 800), random_state=42), df2.sample(min(len(df2), 800), random_state=42)  # 🔼 Increased from 400 → 800

        for _, comp1 in df1.iterrows():
            for _, comp2 in df2.iterrows():
                pairs.append((get_features(comp1, category1), get_features(comp2, category2)))
                labels.append(1 if check_compatibility(comp1, comp2, category1, category2) else 0)

print(f"✅ Total compatibility pairs generated: {len(pairs)}")

# ✅ Convert to NumPy arrays
X = np.array(pairs, dtype=np.float32)
y = np.array(labels)

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"✅ Training size: {len(X_train)}, Testing size: {len(X_test)}")

# ✅ Define Siamese Neural Network (🔼 Slightly Increased Complexity)
def build_siamese_network(input_shape):
    print("🛠 Building Fully Expanded Siamese Network...")
    input_a, input_b = Input(shape=input_shape), Input(shape=input_shape)

    shared_network = tf.keras.Sequential([
        Dense(256, activation="relu"),  # 🔼 Increased neurons (128 → 256)
        Dense(128, activation="relu"),  
        Dense(64, activation="relu"),  
    ])

    encoded_a, encoded_b = shared_network(input_a), shared_network(input_b)

    L1_layer = Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))
    L1_distance = L1_layer([encoded_a, encoded_b])

    output_layer = Dense(1, activation="sigmoid")(L1_distance)
    return Model(inputs=[input_a, input_b], outputs=output_layer)

# ✅ Compile model
print("🔄 Compiling model...")
input_shape = X_train[0][0].shape
siamese_model = build_siamese_network(input_shape)
siamese_model.compile(loss="binary_crossentropy", optimizer=Adam(learning_rate=0.001), metrics=["accuracy"])
print("✅ Model compiled successfully")

# ✅ Train model (🔼 Increased epochs to 15 for better generalization)
print("🚀 Training model (Fully Expanded)...")
history = siamese_model.fit(
    [X_train[:, 0], X_train[:, 1]], y_train,
    validation_data=([X_test[:, 0], X_test[:, 1]], y_test),
    epochs=15, batch_size=32  # 🔼 Increased epochs from 10 → 15 & batch size from 16 → 32
)
print("✅ Training complete!")

# ✅ Save model
MODEL_PATH = os.path.join(BASE_DIR, "models/full_siamese_network_model.keras")
siamese_model.save(MODEL_PATH)
print(f"✅ Model saved at {MODEL_PATH}")