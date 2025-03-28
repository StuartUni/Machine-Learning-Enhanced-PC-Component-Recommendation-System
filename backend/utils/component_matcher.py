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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # e.g. backend/
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# ✅ Load helper
def load_csv(name):
    path = os.path.join(DATA_FOLDER, f"preprocessed_filtered_{name}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Dataset not found: {path}")
    return pd.read_csv(path)

# ✅ Compatibility-aware build generator
def get_compatible_build(cpu_choice=None):
    cpus = load_csv("cpu")
    motherboards = load_csv("motherboard")
    ram_ddr4 = load_csv("ram_ddr4")
    ram_ddr5 = load_csv("ram_ddr5")
    coolers = load_csv("cpu_cooler")
    gpus = load_csv("gpu")
    psus = load_csv("power_supply")

    # ✅ Select a CPU (random or fixed)
    cpu = cpu_choice or cpus.sample(1).iloc[0]

    # ✅ Match motherboard by socket
    compatible_mobos = motherboards[motherboards["socket"] == cpu["socket"]]
    if compatible_mobos.empty:
        return None
    motherboard = compatible_mobos.sample(1).iloc[0]

    # ✅ Match RAM by DDR type
    ddr_type = str(motherboard["memory_type"]).strip().upper()
    compatible_ram = ram_ddr5 if ddr_type == "DDR5" else ram_ddr4
    if compatible_ram.empty:
        return None
    ram = compatible_ram.sample(1).iloc[0]

    # ✅ Select other components randomly
    cpu_cooler = coolers.sample(1).iloc[0]
    gpu = gpus.sample(1).iloc[0]
    psu = psus.sample(1).iloc[0]

    return {
        "cpu": {"name": cpu["name"], "price": cpu["original_price"]},
        "motherboard": {"name": motherboard["name"], "price": motherboard["original_price"]},
        "ram": {"name": ram["name"], "price": ram["original_price"]},
        "cpu_cooler": {"name": cpu_cooler["name"], "price": cpu_cooler["original_price"]},
        "gpu": {"name": gpu["name"], "price": gpu["original_price"]},
        "power_supply": {"name": psu["name"], "price": psu["original_price"]},
    }

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
        return None

    dataset["normalized_name"] = dataset[column_name].apply(preprocess_component_name)
    normalized_name = preprocess_component_name(component_name)

    match = process.extractOne(normalized_name, dataset["normalized_name"], scorer=fuzz.partial_ratio)
    if match and len(match) >= 2:
        best_match, score, index = match[:3]
        if score >= 80:
            return dataset.iloc[index].to_dict()
    return None

# ✅ Match system requirements to real components
def match_requirements_to_components(game_requirements, budget):
    cpu_data = load_csv("cpu")
    gpu_data = load_csv("gpu")

    matched_components = {"CPU": None, "GPU": None, "RAM": None}
    total_cost = 0

    # Match CPU
    if game_requirements.get("CPU", "Unknown") != "Unknown":
        for cpu in game_requirements["CPU"].split(" or "):
            match = match_best_component(cpu.strip(), cpu_data, "name")
            if match:
                matched_components["CPU"] = match
                total_cost += match["original_price"]
                break

    # Match GPU
    if game_requirements.get("GPU", "Unknown") != "Unknown":
        for gpu in game_requirements["GPU"].split(" or "):
            match = match_best_component(gpu.strip(), gpu_data, "name")
            if match:
                matched_components["GPU"] = match
                total_cost += match["original_price"]
                break

    # RAM handling
    if game_requirements.get("RAM", "Unknown") != "Unknown":
        required_ram = int("".join(filter(str.isdigit, game_requirements["RAM"])))
        matched_components["RAM"] = f"{max(8, required_ram)} GB"
        total_cost += 50  # Approx. RAM price

    # Budget Check + Downgrade Logic
    if total_cost > budget:
        print(f"⚠️ Over budget by ${total_cost - budget}. Downgrading...")

        # Downgrade GPU
        if matched_components["GPU"]:
            cheaper = gpu_data[gpu_data["original_price"] < matched_components["GPU"]["original_price"]]
            if not cheaper.empty:
                best = cheaper.sort_values("original_price").iloc[0].to_dict()
                total_cost += best["original_price"] - matched_components["GPU"]["original_price"]
                matched_components["GPU"] = best

        # Downgrade CPU if needed
        if total_cost > budget and matched_components["CPU"]:
            cheaper = cpu_data[cpu_data["original_price"] < matched_components["CPU"]["original_price"]]
            if not cheaper.empty:
                best = cheaper.sort_values("original_price").iloc[0].to_dict()
                total_cost += best["original_price"] - matched_components["CPU"]["original_price"]
                matched_components["CPU"] = best

    return matched_components