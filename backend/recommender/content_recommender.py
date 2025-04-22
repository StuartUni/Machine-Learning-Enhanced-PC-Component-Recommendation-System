"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-07
Description:
This module generates content-based PC build recommendations.
Features:
- Uses cosine similarity on labeled builds to recommend based on user features
- Assembles manual builds under budget constraints for non-gaming use cases
- Ensures CPU-Motherboard-RAM compatibility when building manually
"""

import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCALER_PATH = os.path.join(BASE_DIR, "models", "content_scaler.pkl")
BUILD_DATA_PATH = os.path.join(BASE_DIR, "data", "builds", "labeled_builds.csv")
DATA_DIR = os.path.join(BASE_DIR, "data")

scaler = joblib.load(SCALER_PATH)
build_df = pd.read_csv(BUILD_DATA_PATH)

FEATURE_COLUMNS = ["cpu_score", "gpu_score", "ram_gb", "storage_gb", "price"]

component_files = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "case": "preprocessed_filtered_case.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "storage": "preprocessed_filtered_storage.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
}

PART_MAPPING = {
    "cpu": "CPU",
    "gpu": "GPU",
    "motherboard": "Motherboard",
    "power_supply": "PSU",
    "case": "Case",
    "ram_ddr4": "RAM",
    "ram_ddr5": "RAM",
    "storage": "Storage",
}

def recommend_build_from_features(user_features=None, use_case=None, budget=None, allocation=None, top_k=1):
    if user_features:
        input_df = pd.DataFrame([user_features])
        scaled_input = scaler.transform(input_df)
        filtered_builds = build_df[build_df["price"] <= user_features["price"]]
        if filtered_builds.empty:
            print(" No builds under budget found — using full list as fallback.")
            filtered_builds = build_df

        scaled_builds = scaler.transform(filtered_builds[FEATURE_COLUMNS])
        distances = np.linalg.norm(scaled_builds - scaled_input, axis=1)
        filtered_builds["similarity"] = -distances
        top_builds = filtered_builds.sort_values("similarity", ascending=False).head(top_k)
        return top_builds.to_dict(orient="records")

    if use_case and budget and allocation:
        #  Load component datasets
        component_data = {}
        for key, file in component_files.items():
            path = os.path.join(DATA_DIR, file)
            if os.path.exists(path):
                df = pd.read_csv(path)
                component_data[key] = df[df["original_price"] <= budget * allocation.get(key, 0.1)]
            else:
                component_data[key] = pd.DataFrame()

        build = {}
        total = 0.0
        

        #  1. Pick best CPU first
        #  Exclude LGA1851 CPUs before selection
        if not component_data["cpu"].empty:
            cpu_df = component_data["cpu"]
            cpu_df = cpu_df[~cpu_df["socket"].str.replace(" ", "").str.upper().str.contains("LGA1851")]
            if not cpu_df.empty:
                best_cpu = cpu_df.sort_values("original_price", ascending=False).iloc[0]
                build["CPU"] = best_cpu.to_dict()
                total += best_cpu["original_price"]
                cpu_socket = best_cpu.get("socket", "").replace("FCLGA", "LGA").replace(" ", "").upper()
            else:
                print(" No CPUs available after filtering out LGA1851!")

        #  2. Pick compatible Motherboard based on CPU socket
        if not component_data["motherboard"].empty:
            compatible_mobos = component_data["motherboard"]
            compatible_mobos["socket_clean"] = compatible_mobos["socket"].str.replace(" ", "").str.upper()

            matched_mobos = compatible_mobos[compatible_mobos["socket_clean"] == cpu_socket]

            if not matched_mobos.empty:
                best_mobo = matched_mobos.sort_values("original_price", ascending=False).iloc[0]
                build["Motherboard"] = best_mobo.to_dict()
                total += best_mobo["original_price"]
            else:
                print(f" No compatible motherboard found for CPU socket {cpu_socket}!")

        #  3. Pick GPU
        if not component_data["gpu"].empty:
            best_gpu = component_data["gpu"].sort_values("original_price", ascending=False).iloc[0]
            build["GPU"] = best_gpu.to_dict()
            total += best_gpu["original_price"]

        #  4. RAM - Match DDR4 or DDR5 based on Motherboard
        ram_type = "ram_ddr4"
        if build.get("Motherboard") and "memory_type" in build["Motherboard"]:
            if "DDR5" in str(build["Motherboard"]["memory_type"]).upper():
                ram_type = "ram_ddr5"

        ram_df = component_data.get(ram_type, pd.DataFrame())
        if not ram_df.empty:
            best_ram = ram_df.sort_values("original_price", ascending=False).iloc[0]
            build["RAM"] = best_ram.to_dict()
            total += best_ram["original_price"]

        #  5. PSU
        if not component_data["power_supply"].empty:
            best_psu = component_data["power_supply"].sort_values("original_price", ascending=False).iloc[0]
            build["PSU"] = best_psu.to_dict()
            total += best_psu["original_price"]

        #  6. Case
        if not component_data["case"].empty:
            best_case = component_data["case"].sort_values("original_price", ascending=False).iloc[0]
            build["Case"] = best_case.to_dict()
            total += best_case["original_price"]

        #  7. Manual add Storage and CPU Cooler
        build["Storage_fixed"] = {"name": "500GB SSD", "original_price": 50.00}
        build["CpuCooler_fixed"] = {"name": "Stock Cooler", "original_price": 30.00}
        total += 50.00
        total += 30.00

        #  Return
        return {"build": build, "total": round(total, 2)}

    raise ValueError(" Invalid arguments. Provide either user_features or (use_case + budget + allocation).")