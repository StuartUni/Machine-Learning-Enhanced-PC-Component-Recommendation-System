"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 25/03/2025
Description:
This script matches game system requirements to the best available PC components.
It:
- Loads preprocessed component datasets.
- Uses fuzzy matching to identify the best-matching hardware.
- Ensures recommendations fit within budget constraints.
"""

import os
import pandas as pd
from fuzzywuzzy import process, fuzz
import re

# ✅ Define dataset folder paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Gets the 'backend/' directory
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# ✅ Define dataset file paths
CPU_DATA_PATH = os.path.join(DATA_FOLDER, "preprocessed_filtered_cpu.csv")
GPU_DATA_PATH = os.path.join(DATA_FOLDER, "preprocessed_filtered_gpu.csv")

# ✅ Ensure datasets exist before loading
if not os.path.exists(CPU_DATA_PATH):
    raise FileNotFoundError(f"❌ Dataset not found: {CPU_DATA_PATH}")
if not os.path.exists(GPU_DATA_PATH):
    raise FileNotFoundError(f"❌ Dataset not found: {GPU_DATA_PATH}")

# ✅ Load component datasets
cpu_data = pd.read_csv(CPU_DATA_PATH)
gpu_data = pd.read_csv(GPU_DATA_PATH)

def preprocess_component_name(name):
    """
    Normalize component names by:
    - Removing brand prefixes (Intel, AMD, Nvidia)
    - Removing GHz values and special characters
    - Converting to lowercase
    """
    if not isinstance(name, str):
        return name  

    name = name.lower()
    name = re.sub(r"(\d+\.\d+\s*ghz)", "", name)  # Remove GHz values
    name = re.sub(r"(intel|amd|nvidia|gpu|cpu|apu|geforce|radeon)", "", name)  # Remove brand names
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)  # Remove special characters
    return name.strip()

def match_best_component(component_name, dataset, column_name):
    """
    Finds the best matching component using fuzzy matching.
    - Uses `fuzz.partial_ratio` for name similarity.
    - Ensures dataset is not empty before processing.
    """
    if dataset.empty:
        return None

    dataset["normalized_name"] = dataset[column_name].apply(preprocess_component_name)
    normalized_component_name = preprocess_component_name(component_name)

    match = process.extractOne(normalized_component_name, dataset["normalized_name"], scorer=fuzz.partial_ratio)
    
    if match and len(match) >= 2:
        best_match, score, index = match[:3]
        if score >= 80:
            return dataset.iloc[index].to_dict()
    return None

def match_requirements_to_components(game_requirements, budget):
    """
    Matches game system requirements to the best available PC components within budget.
    - Uses fuzzy matching for CPU & GPU.
    - Ensures RAM meets or exceeds game requirements.
    - Performs budget validation and downgrades components if needed.
    """
    matched_components = {"CPU": None, "GPU": None, "RAM": None}
    total_cost = 0

    # ✅ Match CPU
    if game_requirements.get("CPU", "Unknown") != "Unknown":
        cpu_candidates = game_requirements["CPU"].split(" or ")
        best_cpu = None

        for cpu in cpu_candidates:
            match = match_best_component(cpu.strip(), cpu_data, "name")
            if match:
                best_cpu = match
                total_cost += match["price"]
                break

        matched_components["CPU"] = best_cpu

    # ✅ Match GPU
    if game_requirements.get("GPU", "Unknown") != "Unknown":
        gpu_candidates = game_requirements["GPU"].split(" or ")
        best_gpu = None

        for gpu in gpu_candidates:
            match = match_best_component(gpu.strip(), gpu_data, "name")
            if match:
                best_gpu = match
                total_cost += match["price"]
                break

        matched_components["GPU"] = best_gpu

    # ✅ Ensure RAM meets/exceeds the requirement
    if game_requirements.get("RAM", "Unknown") != "Unknown":
        required_ram = int("".join(filter(str.isdigit, game_requirements["RAM"])))
        matched_components["RAM"] = f"{max(8, required_ram)} GB"
        total_cost += 50  # Approximate cost of RAM

    # ✅ Budget Validation & Component Downgrade Logic
    if total_cost > budget:
        print(f"⚠️ Budget exceeded by ${total_cost - budget}. Attempting downgrade...")

        # ✅ Try downgrading GPU first
        if matched_components["GPU"]:
            cheaper_gpu = gpu_data[gpu_data["price"] < matched_components["GPU"]["price"]].sort_values(by="price").iloc[0].to_dict()
            if cheaper_gpu:
                total_cost -= matched_components["GPU"]["price"]
                total_cost += cheaper_gpu["price"]
                matched_components["GPU"] = cheaper_gpu

        # ✅ Try downgrading CPU
        if total_cost > budget and matched_components["CPU"]:
            cheaper_cpu = cpu_data[cpu_data["price"] < matched_components["CPU"]["price"]].sort_values(by="price").iloc[0].to_dict()
            if cheaper_cpu:
                total_cost -= matched_components["CPU"]["price"]
                total_cost += cheaper_cpu["price"]
                matched_components["CPU"] = cheaper_cpu

    return matched_components