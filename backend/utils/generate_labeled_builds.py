# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-07
# Description:
# Generates a labeled_builds.csv file containing example builds with normalized prices
# for training or testing collaborative and content-based recommendation models.

import os
import uuid
import pandas as pd

# ✅ Example component data
cpus = [
    {"name": "Intel Core i5-12400F", "performance_score": 0.65},
    {"name": "Intel Core i7-14700K", "performance_score": 0.85}
]
gpus = [
    {"name": "GeForce GTX 1650 SUPER", "performance_score": 0.55},
    {"name": "GeForce RTX 3060", "performance_score": 0.75}
]
rams = [
    {"name": "Corsair Vengeance LPX 16GB", "ram_gb": 16},
    {"name": "Crucial Ballistix 32GB", "ram_gb": 32}
]
storages = [
    {"name": "Samsung 970 EVO 1TB", "storage_gb": 1000},
    {"name": "CT500P2SSD8", "storage_gb": 500}
]

# ✅ Generate combinations
builds = []
for cpu in cpus:
    for gpu in gpus:
        for ram in rams:
            for storage in storages:
                builds.append({
                    "build_id": str(uuid.uuid4()),
                    "cpu_name": cpu["name"],
                    "gpu_name": gpu["name"],
                    "ram_name": ram["name"],
                    "storage_name": storage["name"],
                    "cpu_score": cpu["performance_score"],
                    "gpu_score": gpu["performance_score"],
                    "ram_gb": ram["ram_gb"],
                    "storage_gb": storage["storage_gb"],
                    "price": 1.0  # Normalized for training purposes
                })

# ✅ Save to CSV
df = pd.DataFrame(builds)
os.makedirs("backend/data/builds", exist_ok=True)
df.to_csv("backend/data/builds/labeled_builds.csv", index=False)
print("✅ labeled_builds.csv has been created.")