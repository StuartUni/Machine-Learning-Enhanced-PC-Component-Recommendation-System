# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-17
# Description:
# Utility module for ensuring that all recommended PC builds are complete.
# This fallback system fills missing parts (motherboard, PSU, case, cooler, RAM)
# using preprocessed_filtered component datasets. It ensures real component names
# are used by selecting the most expensive option under the allocated budget for each category.
# This supports content-based and hybrid recommendation flows where the ML model
# may not include all parts in its prediction.

import os
import pandas as pd

# ✅ Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ✅ Component dataset files
COMPONENT_FILES = {
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "case": "preprocessed_filtered_case.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
}

# ✅ Load all component data into memory once
component_data = {}
for key, file in COMPONENT_FILES.items():
    path = os.path.join(DATA_DIR, file)
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "original_price" in df.columns:
            df["price"] = df["original_price"]
        component_data[key] = df
    else:
        component_data[key] = pd.DataFrame()
        
# Log the first few rows of each dataframe to inspect the data
for key, df in component_data.items():
    print(f"Component: {key}")
    print(df.head())  # Log the first 5 rows

def fill_missing_components(build: dict, budget: float, allocation: dict) -> dict:
    """
    Fills missing components in the recommended build using best real options under budget.
    Only updates fields that are missing or marked as 'Unknown'.
    """

    def pick_best(part, alloc_key):
        df = component_data.get(part, pd.DataFrame())
        max_price = budget * allocation.get(alloc_key, 0.1)
        best = df[df["price"] <= max_price].sort_values("price", ascending=False).head(1)
        return best.iloc[0]["name"] if not best.empty else "Unknown"

    # Motherboard
    if "motherboard_name" not in build or build["motherboard_name"] in ["Unknown", None, ""]:
        build["motherboard_name"] = pick_best("motherboard", "motherboard")

    # PSU
    if "psu_name" not in build or build["psu_name"] in ["Unknown", None, ""]:
        build["psu_name"] = pick_best("power_supply", "power_supply")

    # Case
    if "case_name" not in build or build["case_name"] in ["Unknown", None, ""]:
        build["case_name"] = pick_best("case", "case")

    # CPU Cooler
    if "cpu_cooler_name" not in build or build["cpu_cooler_name"] in ["Unknown", None, ""]:
        build["cpu_cooler_name"] = pick_best("cpu_cooler", "cpu_cooler")

    # RAM (fallback always assumes DDR4 if no motherboard data)
    if "ram_name" not in build or build["ram_name"] in ["Unknown", None, ""]:
        build["ram_name"] = pick_best("ram_ddr4", "ram")

    return build