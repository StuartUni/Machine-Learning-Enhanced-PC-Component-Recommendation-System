# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-18
# Description:
# Generates a new labeled_builds.csv containing simple, clean builds
# for TFRS or content-based training. Each build includes CPU, GPU, RAM, Storage, and Price.

import os
import pandas as pd
import uuid

# ✅ Define example components
cpus = [
    {"name": "Intel Core i5-12400F", "performance_score": 0.70},
    {"name": "Intel Core i7-13700K", "performance_score": 0.90},
    {"name": "AMD Ryzen 5 7600", "performance_score": 0.75},
    {"name": "AMD Ryzen 7 7700X", "performance_score": 0.85}
]

gpus = [
    {"name": "NVIDIA RTX 4060", "performance_score": 0.70},
    {"name": "NVIDIA RTX 4070", "performance_score": 0.85},
    {"name": "AMD RX 7600", "performance_score": 0.65},
    {"name": "AMD RX 7700 XT", "performance_score": 0.80}
]

rams = [
    {"name": "Corsair Vengeance 16GB DDR5", "ram_gb": 16},
    {"name": "G.Skill Ripjaws 32GB DDR5", "ram_gb": 32}
]

storages = [
    {"name": "Samsung 970 EVO 1TB NVMe", "storage_gb": 1000},
    {"name": "Crucial P3 500GB NVMe", "storage_gb": 500}
]

# ✅ Generate builds
builds = []

for cpu in cpus:
    for gpu in gpus:
        for ram in rams:
            for storage in storages:
                build = {
                    "build_id": str(uuid.uuid4()),
                    "cpu_name": cpu["name"],
                    "gpu_name": gpu["name"],
                    "ram_name": ram["name"],
                    "storage_name": storage["name"],
                    "cpu_score": cpu["performance_score"],
                    "gpu_score": gpu["performance_score"],
                    "ram_gb": ram["ram_gb"],
                    "storage_gb": storage["storage_gb"],
                    "price": round(
                        (cpu["performance_score"] + gpu["performance_score"]) * 300 +
                        ram["ram_gb"] * 3 +
                        storage["storage_gb"] * 0.08, 2
                    )  # Rough simple price formula
                }
                builds.append(build)

# ✅ Save builds
output_dir = os.path.join("data", "builds")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "labeled_builds.csv")
df = pd.DataFrame(builds)
df.to_csv(output_path, index=False)

print(f"✅ {len(builds)} builds saved to {output_path}")