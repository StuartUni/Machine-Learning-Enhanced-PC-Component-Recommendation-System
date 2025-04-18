# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-04
# Description: Generates a labeled CSV of complete, compatible PC builds by combining CPU, GPU, RAM, motherboard, PSU, cooler, and storage from filtered datasets.

import os
import pandas as pd
import random
from itertools import product
import uuid  # for unique build IDs

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "builds")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Load filtered datasets
def load(name):
    path = os.path.join(DATA_DIR, f"preprocessed_filtered_{name}.csv")
    if not os.path.exists(path):
        print(f"❌ Missing {name} file.")
        return pd.DataFrame()
    return pd.read_csv(path)

cpu_df = load("cpu")
gpu_df = load("gpu")
ram4_df = load("ram_ddr4")
ram5_df = load("ram_ddr5")
mb_df = load("motherboard")
psu_df = load("power_supply")
cooler_df = load("cpu_cooler")
storage_df = load("storage")
case_df = load("case")

# ✅ Sanity checks
required_dfs = [cpu_df, gpu_df, mb_df, psu_df, cooler_df, storage_df, case_df]
if any(df.empty for df in required_dfs):
    raise ValueError("❌ One or more required datasets are missing or empty.")

builds = []

# ✅ Generate compatible builds
for _ in range(100):  # Limit to 100 builds for performance
    cpu = cpu_df.sample(1).iloc[0]
    socket = cpu["socket"]

    # Match motherboard by socket
    mobo_matches = mb_df[mb_df["socket"] == socket]
    if mobo_matches.empty:
        continue
    mobo = mobo_matches.sample(1).iloc[0]

    # Match RAM by motherboard memory type
    ddr_type = mobo["memory_type"].strip().upper()
    ram_df = ram5_df if ddr_type == "DDR5" else ram4_df
    if ram_df.empty:
        continue
    ram = ram_df.sample(1).iloc[0]

    # Select other components
    gpu = gpu_df.sample(1).iloc[0]
    psu = psu_df.sample(1).iloc[0]
    cooler = cooler_df.sample(1).iloc[0]
    storage = storage_df.sample(1).iloc[0]
    case = case_df.sample(1).iloc[0]

    total_price = (
        cpu["original_price"] + gpu["original_price"] + ram["original_price"] + mobo["original_price"] +
        psu["original_price"] + cooler["original_price"] + storage["original_price"] + case["original_price"]
    )
    
    # Create a unique build_id using uuid
    build_id = str(uuid.uuid4())

    build = {
        "build_id": build_id,  # Add unique build_id
        "cpu_score": cpu["performance_score"],
        "gpu_score": gpu["performance_score"],
        "ram_gb": ram["capacity_gb"] if "capacity_gb" in ram else 16,
        "storage_gb": storage["capacity_gb"] if "capacity_gb" in storage else 512,
        "price": round(total_price, 2),
        "cpu_name": cpu["name"],
        "gpu_name": gpu["name"],
        "ram_name": ram["name"],
        "mobo_name": mobo["name"],
        "cooler_name": cooler["name"],
        "psu_name": psu["name"],
        "storage_name": storage["name"],
        "case_name": case["name"]
    }

    builds.append(build)

# ✅ Save
df = pd.DataFrame(builds)
if not df.empty:
    out_path = os.path.join(OUTPUT_DIR, "labeled_builds.csv")
    df.to_csv(out_path, index=False)
    print(f"✅ Saved {len(df)} labeled builds to: {out_path}")
else:
    print("❌ No compatible builds generated.")