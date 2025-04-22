"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-17
Description:
This utility module fills missing components in recommended PC builds using real component datasets.
Features:
- Loads motherboard, PSU, case, CPU cooler, and RAM datasets
- Picks the best available part under budget for missing categories
- Ensures recommended builds are complete for user presentation
"""

import os
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Component dataset files
COMPONENT_FILES = {
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "case": "preprocessed_filtered_case.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
}

# Load all component data into memory
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

def fill_missing_components(build: dict, budget: float, allocation: dict) -> dict:
    """
    Fills missing components in the recommended build using best available options under budget.
    
    Args:
        build (dict): The partially complete build dictionary.
        budget (float): Total budget provided by the user.
        allocation (dict): Budget allocation per component category.
    
    Returns:
        dict: The completed build dictionary.
    """

    def pick_best(part, alloc_key):
        """Selects best component under budget for a part."""
        df = component_data.get(part, pd.DataFrame())
        max_price = budget * allocation.get(alloc_key, 0.1)
        best = df[df["price"] <= max_price].sort_values("price", ascending=False).head(1)
        return best.iloc[0]["name"] if not best.empty else "Unknown"

    # Fill missing motherboard
    if "motherboard_name" not in build or build["motherboard_name"] in ["Unknown", None, ""]:
        build["motherboard_name"] = pick_best("motherboard", "motherboard")

    # Fill missing PSU
    if "psu_name" not in build or build["psu_name"] in ["Unknown", None, ""]:
        build["psu_name"] = pick_best("power_supply", "power_supply")

    # Fill missing case
    if "case_name" not in build or build["case_name"] in ["Unknown", None, ""]:
        build["case_name"] = pick_best("case", "case")

    # Fill missing CPU cooler
    if "cpu_cooler_name" not in build or build["cpu_cooler_name"] in ["Unknown", None, ""]:
        build["cpu_cooler_name"] = pick_best("cpu_cooler", "cpu_cooler")

    # Fill missing RAM (assumes DDR4 fallback if no info)
    if "ram_name" not in build or build["ram_name"] in ["Unknown", None, ""]:
        build["ram_name"] = pick_best("ram_ddr4", "ram")

    return build
