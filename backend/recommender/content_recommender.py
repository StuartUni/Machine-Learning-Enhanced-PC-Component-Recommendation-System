# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-07
# Description:
# Loads and runs a content-based recommendation model using cosine similarity
# on a set of labeled builds (generated combinations of compatible components).
# Supports both: (1) feature-based cosine similarity, and (2) use-case budget filtering.
# Automatically downgrades optional parts if build exceeds user budget.

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
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "storage": "preprocessed_filtered_storage.csv"
}

def auto_downgrade_if_needed(build, budget, component_data):
    optional_parts = ["case", "cpu_cooler", "motherboard", "gpu"]
    total_cost = round(build["price"] * budget, 2)

    for part in optional_parts:
        key = f"{part}_name"
        if key not in build or total_cost <= budget:
            continue

        df = component_data.get(part, pd.DataFrame())
        current_name = build[key]
        current_price = df[df["name"] == current_name]["original_price"].values
        if len(current_price) == 0:
            continue

        cheaper_options = df[df["original_price"] < current_price[0]].sort_values("original_price")
        for _, row in cheaper_options.iterrows():
            new_total = total_cost - current_price[0] + row["original_price"]
            if new_total <= budget:
                print(f"⬇️ Downgraded {part} to {row['name']}")
                build[key] = row["name"]
                total_cost = new_total
                break

    build["price"] = round(total_cost / budget, 2)
    return build, total_cost

def recommend_build_from_features(user_features=None, use_case=None, budget=None, allocation=None, top_k=1):
    if user_features:
        input_df = pd.DataFrame([user_features])
        scaled_input = scaler.transform(input_df)
        filtered_builds = build_df[build_df["price"] <= user_features["price"]]
        if filtered_builds.empty:
            print("⚠️ No builds under budget found — using full list as fallback.")
            filtered_builds = build_df

        scaled_builds = scaler.transform(filtered_builds[FEATURE_COLUMNS])
        distances = np.linalg.norm(scaled_builds - scaled_input, axis=1)
        filtered_builds["similarity"] = -distances
        top_builds = filtered_builds.sort_values("similarity", ascending=False).head(top_k)
        return top_builds.to_dict(orient="records")

    if use_case and budget and allocation:
        component_data = {}
        for key, file in component_files.items():
            path = os.path.join(DATA_DIR, file)
            if os.path.exists(path):
                df = pd.read_csv(path)
                component_data[key] = df[df["original_price"] <= budget * allocation.get(key, 0.1)]
            else:
                component_data[key] = pd.DataFrame()

        if not component_data["motherboard"].empty:
            memory_type = component_data["motherboard"].iloc[0]["memory_type"]
            ram_type = "ram_ddr5" if "DDR5" in memory_type else "ram_ddr4"
            component_data["ram"] = component_data.get(ram_type, pd.DataFrame())
        else:
            component_data["ram"] = component_data.get("ram_ddr4", pd.DataFrame())

        build = {}
        total = 0
        for part, df in component_data.items():
            if not df.empty:
                best = df.sort_values("original_price", ascending=False).iloc[0]
                build[f"{part}_name"] = best["name"]
                total += best["original_price"]
                if "performance_score" in best:
                    build[f"{part}_score"] = best["performance_score"]
                if "capacity_gb" in best:
                    if "ram" in part:
                        build["ram_gb"] = best["capacity_gb"]
                    if "storage" in part:
                        build["storage_gb"] = best["capacity_gb"]

        # 🎯 Clean up RAM naming
        build["ram_name"] = build.get("ram_ddr4_name") or build.get("ram_ddr5_name")
        build.pop("ram_ddr4_name", None)
        build.pop("ram_ddr5_name", None)

        build["price"] = round(total / budget, 2)

        if total > budget:
            print(f"⚠️ Build over budget by ${total - budget:.2f}. Attempting to downgrade optional parts...")
            build, total = auto_downgrade_if_needed(build, budget, component_data)

        build["price"] = round(total / budget, 2)
        return {"build": build, "total": round(total, 2)}

    raise ValueError("❌ Invalid arguments. Provide either user_features or (use_case + budget + allocation).")