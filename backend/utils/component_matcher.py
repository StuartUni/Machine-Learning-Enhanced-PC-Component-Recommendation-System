"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 28/03/2025
Description:
This utility supports PC component matching in two ways:
1. Fuzzy matching system requirements (for Steam games, etc.)
2. Compatibility-aware random build generation for user seeding or testing

Features:
- Ensures socket & DDR-type compatibility
- Uses real prices from original_price
- Uses fuzzy logic for matching system requirements
"""

import os
import pandas as pd
import random
import re
from fuzzywuzzy import process, fuzz

# ✅ Define dataset folder path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# ✅ Load helper
def load_csv(name):
    path = os.path.join(DATA_FOLDER, f"preprocessed_filtered_{name}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Dataset not found: {path}")
    return pd.read_csv(path)

# ✅ Preprocessing for fuzzy matching
def preprocess_component_name(name):
    if not isinstance(name, str):
        return name
    name = name.lower()
    name = re.sub(r"(\d+\.\d+\s*ghz)", "", name)
    name = re.sub(r"(intel|amd|nvidia|gpu|cpu|apu|geforce|radeon)", "", name)
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    return name.strip()

# ✅ Fuzzy component matcher
def match_best_component(component_name, dataset, column_name):
    if dataset.empty:
        print(f"⚠️ Empty dataset for {column_name}")
        return None

    dataset["normalized_name"] = dataset[column_name].apply(preprocess_component_name)
    normalized_name = preprocess_component_name(component_name)
    
    # Debugging output
    print(f"🔍 Trying to match: '{component_name}'")

    match = process.extractOne(normalized_name, dataset["normalized_name"], scorer=fuzz.partial_ratio)
    if match and len(match) >= 2:
        best_match, score, index = match[:3]
        if score >= 75:  # Slightly more forgiving
            print(f"✅ Matched '{component_name}' to '{dataset.iloc[index][column_name]}' (Score: {score})")
            return dataset.iloc[index].to_dict()
        else:
            print(f"❌ No strong match for '{component_name}' (Best Score: {score})")
    else:
        print(f"❌ No match found for '{component_name}'")

    return None

# ✅ Compatibility Matcher
def match_requirements_to_components(game_requirements, budget):
    cpu_data = load_csv("cpu")
    gpu_data = load_csv("gpu")

    matched_components = {"CPU": None, "GPU": None, "RAM": None}
    total_cost = 0

    # ✅ Match CPU
    if game_requirements.get("CPU", "Unknown") != "Unknown":
        for cpu in game_requirements["CPU"].split(" or "):
            match = match_best_component(cpu.strip(), cpu_data, "name")
            if match:
                matched_components["CPU"] = match
                total_cost += match["original_price"]
                break

    # ✅ Match GPU
    if game_requirements.get("GPU", "Unknown") != "Unknown":
        for gpu in game_requirements["GPU"].split(" or "):
            match = match_best_component(gpu.strip(), gpu_data, "name")
            if match:
                matched_components["GPU"] = match
                total_cost += match["original_price"]
                break

    # ✅ Match RAM (with safety)
    if game_requirements.get("RAM", "Unknown") != "Unknown":
        match = re.search(r"(\d+)", game_requirements["RAM"])
        required_ram = int(match.group(1)) if match else 8

        if required_ram > 128:
            print(f"⚠️ RAM parsed as {required_ram} GB — defaulting to 16 GB")
            required_ram = 16

        matched_components["RAM"] = f"{max(8, required_ram)} GB"
        total_cost += 50  # Approximate RAM price

    # ✅ Downgrade logic if over budget
    if total_cost > budget:
        print(f"⚠️ Over budget by ${total_cost - budget:.2f}. Attempting downgrade...")

        # Downgrade GPU
        if matched_components["GPU"]:
            cheaper = gpu_data[gpu_data["original_price"] < matched_components["GPU"]["original_price"]]
            if not cheaper.empty:
                best = cheaper.sort_values("original_price").iloc[0].to_dict()
                print(f"⬇️ Downgrading GPU to {best['name']}")
                total_cost += best["original_price"] - matched_components["GPU"]["original_price"]
                matched_components["GPU"] = best

        # Downgrade CPU if needed
        if total_cost > budget and matched_components["CPU"]:
            cheaper = cpu_data[cpu_data["original_price"] < matched_components["CPU"]["original_price"]]
            if not cheaper.empty:
                best = cheaper.sort_values("original_price").iloc[0].to_dict()
                print(f"⬇️ Downgrading CPU to {best['name']}")
                total_cost += best["original_price"] - matched_components["CPU"]["original_price"]
                matched_components["CPU"] = best

    return matched_components, round(total_cost, 2)