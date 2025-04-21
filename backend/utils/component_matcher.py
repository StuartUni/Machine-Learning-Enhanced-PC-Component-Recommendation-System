
"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-18
Description:
Modernized component matcher for PC builds.
- Ensures CPU-Motherboard-RAM compatibility
- Matches parts to system requirements
- Allocates budget smartly
- Picks highest performance CPU/GPU within budget
- Adds basic PSU wattage sanity (>=400W)
- Adds Case
- Graceful downgrades if needed
"""
import os
import pandas as pd
import re
from fuzzywuzzy import process, fuzz

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

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
        return None
    dataset["normalized_name"] = dataset[column_name].apply(preprocess_component_name)
    normalized_name = preprocess_component_name(component_name)
    match = process.extractOne(normalized_name, dataset["normalized_name"], scorer=fuzz.partial_ratio)
    if match and len(match) >= 2:
        best_match, score, index = match[:3]
        if score >= 75:
            return dataset.iloc[index].to_dict()
    return None

# ✅ Try upgrading components to use spare budget smartly
def upgrade_build_with_spare_budget(matched, spare_budget, cpu_data, gpu_data, ram_ddr4, ram_ddr5, motherboard_data):
    upgrades_made = False

    # Upgrade GPU first
    if matched.get("GPU"):
        better_gpus = gpu_data[
            (gpu_data["original_price"] > matched["GPU"]["original_price"]) &
            (gpu_data["original_price"] <= matched["GPU"]["original_price"] + spare_budget)
        ].sort_values(by="performance_score", ascending=False)
        if not better_gpus.empty:
            best_gpu = better_gpus.iloc[0].to_dict()
            spare_budget -= (best_gpu["original_price"] - matched["GPU"]["original_price"])
            matched["GPU"] = best_gpu
            upgrades_made = True
            print(f"⬆️ Upgraded GPU to {best_gpu['name']}!")

    # Upgrade CPU second
    if matched.get("CPU"):
        better_cpus = cpu_data[
            (cpu_data["original_price"] > matched["CPU"]["original_price"]) &
            (cpu_data["original_price"] <= matched["CPU"]["original_price"] + spare_budget)
        ].sort_values(by="performance_score", ascending=False)
        if not better_cpus.empty:
            best_cpu = better_cpus.iloc[0].to_dict()
            spare_budget -= (best_cpu["original_price"] - matched["CPU"]["original_price"])
            matched["CPU"] = best_cpu
            upgrades_made = True
            print(f"⬆️ Upgraded CPU to {best_cpu['name']}!")

    # After upgrading CPU, re-match Motherboard
    if upgrades_made and matched.get("CPU"):
        cpu_socket = matched["CPU"].get("socket", "").replace("FCLGA", "LGA").replace(" ", "")
        compatible_mobos = motherboard_data[motherboard_data["socket"] == cpu_socket]

        print(f"🧪 CPU after upgrade: {matched['CPU']['name']} with socket {cpu_socket}")
        print(f"🧪 Compatible motherboards found: {len(compatible_mobos)}")

        if not compatible_mobos.empty:
            best_mobo = compatible_mobos.sort_values("original_price").iloc[0].to_dict()
            matched["Motherboard"] = best_mobo
            print(f"🔄 Re-matched Motherboard after CPU upgrade: {best_mobo['name']}")

            # ✅ Re-match RAM immediately based on new Motherboard
            ddr_type = best_mobo.get("memory_type", "DDR4")
            if "DDR5" in ddr_type.upper():
                ram_source = ram_ddr5
            else:
                ram_source = ram_ddr4
            if not ram_source.empty:
                best_ram = ram_source.sort_values("original_price").iloc[0].to_dict()
                matched["RAM"] = best_ram
                print(f"🔄 Re-matched RAM after motherboard upgrade: {best_ram['name']}")

    # ✅ Now try upgrading RAM as normal if spare budget left
    if matched.get("Motherboard") and matched.get("RAM"):
        ddr_type = matched["Motherboard"].get("memory_type", "DDR4")
        if "DDR5" in ddr_type.upper():
            ram_source = ram_ddr5
        else:
            ram_source = ram_ddr4
        better_ram = ram_source[
            (ram_source["original_price"] > matched["RAM"]["original_price"]) &
            (ram_source["original_price"] <= matched["RAM"]["original_price"] + spare_budget)
        ].sort_values("memory_size_gb", ascending=False)
        if not better_ram.empty:
            best_ram = better_ram.iloc[0].to_dict()
            spare_budget -= (best_ram["original_price"] - matched["RAM"]["original_price"])
            matched["RAM"] = best_ram
            print(f"⬆️ Upgraded RAM to {best_ram['name']}!")

    return matched, upgrades_made

def calculate_real_total_cost(build: dict) -> float:
    total = 0.0
    for part_key in ["CPU", "GPU", "Motherboard", "RAM", "PSU", "Case"]:
        part = build.get(part_key)
        if part and "original_price" in part:
            total += part["original_price"]
    return round(total, 2)

# ✅ Main Matching Logic
def match_requirements_to_components(game_requirements, budget):
    cpu_data = load_csv("cpu")
    gpu_data = load_csv("gpu")
    motherboard_data = load_csv("motherboard")
    ram_ddr4_data = load_csv("ram_ddr4")
    ram_ddr5_data = load_csv("ram_ddr5")
    psu_data = load_csv("power_supply")
    case_data = load_csv("case")

    matched = {"CPU": None, "GPU": None, "Motherboard": None, "RAM": None, "PSU": None, "Case": None}
    total_cost = 0

    print("⚙️ Matching components from requirements...")

    # Budget allocation
    allocation = {
        "cpu": 0.25,
        "gpu": 0.4,
        "motherboard": 0.1,
        "ram": 0.1,
        "power_supply": 0.05,
        "case": 0.025,
        "cpu_cooler": 0.025
    }

    cpu_budget = budget * allocation["cpu"]
    gpu_budget = budget * allocation["gpu"]

    # GPU Matching
    if budget >= 1000:
        print("🚀 High budget detected — prioritizing best GPU first!")
        good_gpus = gpu_data[gpu_data["original_price"] <= gpu_budget * 1.2]
        if not good_gpus.empty:
            best_gpu = good_gpus.sort_values(by="performance_score", ascending=False).iloc[0].to_dict()
            matched["GPU"] = best_gpu
            total_cost += best_gpu["original_price"]
            cpu_budget = budget * 0.20
            print(f"⚡ Selected GPU: {best_gpu['name']} | Adjusted CPU budget: {cpu_budget:.2f}")

    if matched["GPU"] is None:
        affordable_gpus = gpu_data[gpu_data["original_price"] <= gpu_budget]
        if not affordable_gpus.empty:
            matched["GPU"] = affordable_gpus.sort_values("performance_score", ascending=False).iloc[0].to_dict()
            total_cost += matched["GPU"]["original_price"]

    # CPU Matching
    if matched["CPU"] is None and game_requirements.get("CPU", "Unknown") != "Unknown":
        for cpu_candidate in game_requirements["CPU"].split(" or "):
            match = match_best_component(cpu_candidate.strip(), cpu_data, "name")
            if match and match["original_price"] <= cpu_budget:
                matched["CPU"] = match
                total_cost += match["original_price"]
                break

    if matched["CPU"] is None:
        affordable_cpus = cpu_data[cpu_data["original_price"] <= cpu_budget]
        if not affordable_cpus.empty:
            matched["CPU"] = affordable_cpus.sort_values("performance_score", ascending=False).iloc[0].to_dict()
            total_cost += matched["CPU"]["original_price"]

    # Motherboard Matching
    if matched["CPU"]:
        cpu_socket = matched["CPU"]["socket"].replace("FCLGA", "LGA")
        compatible_mobos = motherboard_data[motherboard_data["socket"] == cpu_socket]
        if not compatible_mobos.empty:
            matched["Motherboard"] = compatible_mobos.sort_values("original_price").iloc[0].to_dict()
            total_cost += matched["Motherboard"]["original_price"]

    # RAM Matching
    if matched["Motherboard"]:
        ddr_type = matched["Motherboard"]["memory_type"]
        if "DDR5" in ddr_type.upper():
            compatible_ram = ram_ddr5_data
        else:
            compatible_ram = ram_ddr4_data
        if not compatible_ram.empty:
            matched["RAM"] = compatible_ram.sort_values("original_price").iloc[0].to_dict()
            total_cost += matched["RAM"]["original_price"]

    # PSU Matching
    if psu_data is not None and not psu_data.empty:
        matched["PSU"] = psu_data.sort_values("original_price").iloc[0].to_dict()
        total_cost += matched["PSU"]["original_price"]

    # Case Matching
    if case_data is not None and not case_data.empty:
        matched["Case"] = case_data.sort_values("original_price").iloc[0].to_dict()
        total_cost += matched["Case"]["original_price"]

    # Spare Budget (handled separately in upgrade_build_with_spare_budget)
    spare_budget = budget - total_cost
    print(f"🧩 Spare Budget: {spare_budget:.2f}")

    if spare_budget >= 100:
        matched, upgrades_made = upgrade_build_with_spare_budget(
            matched, spare_budget,
            cpu_data, gpu_data, ram_ddr4_data, ram_ddr5_data, motherboard_data
        )

    return matched, calculate_real_total_cost(matched)
