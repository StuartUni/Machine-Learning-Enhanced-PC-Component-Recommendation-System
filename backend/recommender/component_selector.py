# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-02
# Description: Contains logic to select components based on allocated budgets and filtered component data.

import pandas as pd
import os

# Load preprocessed component datasets from the data/preprocessed_filtered directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "preprocessed_filtered")

COMPONENT_FILES = {
    "cpu": "preprocessed_filtered_cpu.csv",
    "gpu": "preprocessed_filtered_gpu.csv",
    "ram_ddr4": "preprocessed_filtered_ram_ddr4.csv",
    "ram_ddr5": "preprocessed_filtered_ram_ddr5.csv",
    "motherboard": "preprocessed_filtered_motherboard.csv",
    "power_supply": "preprocessed_filtered_power_supply.csv",
    "cpu_cooler": "preprocessed_filtered_cpu_cooler.csv",
}

component_data = {}
for key, filename in COMPONENT_FILES.items():
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "original_price" in df.columns:
            df["price"] = df["original_price"]  # Ensure price consistency
        component_data[key] = df
    else:
        component_data[key] = pd.DataFrame()


def select_components(budget: float, allocation: dict) -> dict:
    """
    Selects best component per category under the given budget allocation.
    """
    selected = {}

    for category, percent in allocation.items():
        max_price = budget * percent
        if category in component_data and not component_data[category].empty:
            df = component_data[category]
            selected_df = df.query(f"price <= {max_price}").nlargest(1, "price")
            if not selected_df.empty:
                selected[category] = {
                    "name": selected_df.iloc[0]["name"],
                    "price": float(selected_df.iloc[0]["price"])
                }

    # RAM selection based on motherboard memory type
    if "motherboard" in selected:
        mem_type = selected["motherboard"]["name"]
        ram_key = "ram_ddr5" if "DDR5" in mem_type else "ram_ddr4"
        if ram_key in component_data and not component_data[ram_key].empty:
            max_price = budget * allocation.get("ram", 0.1)
            df = component_data[ram_key].query(f"price <= {max_price}").nlargest(1, "price")
            if not df.empty:
                selected["ram"] = {
                    "name": df.iloc[0]["name"],
                    "price": float(df.iloc[0]["price"])
                }

    return selected