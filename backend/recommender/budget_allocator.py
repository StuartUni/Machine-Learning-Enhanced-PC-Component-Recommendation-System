"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 2025-04-02
Description:
This utility function defines budget allocation strategies for different PC build use cases.
Features:
- Provides default budget percentages for CPU, GPU, RAM, motherboard, etc.
- Supports use cases: gaming, general, work, and school
- Defaults to 'gaming' allocation if use case is unknown
"""

def get_budget_allocation(use_case: str) -> dict:
    """
    Returns a dictionary of budget percentages for each component
    based on the specified use case (e.g., gaming, work, school).
    """
    #  Default to gaming if unknown
    use_case = use_case.lower()

    allocations = {
        "gaming": {
            "cpu": 0.25,
            "gpu": 0.40,
            "ram": 0.10,
            "motherboard": 0.10,
            "power_supply": 0.05,
            "case": 0.025,
            "cpu_cooler": 0.025,
        },
        "general": {
            "cpu": 0.40,
            "gpu": 0.25,
            "ram": 0.15,
            "motherboard": 0.10,
            "power_supply": 0.05,
            "cpu_cooler": 0.05,
        },
        "work": {
            "cpu": 0.42,
            "gpu": 0.22,
            "ram": 0.15,
            "motherboard": 0.10,
            "power_supply": 0.06,
            "cpu_cooler": 0.05,
        },
        "school": {
            "cpu": 0.42,
            "gpu": 0.17,
            "ram": 0.20,
            "motherboard": 0.10,
            "power_supply": 0.06,
            "cpu_cooler": 0.05,
        },
    }

    return allocations.get(use_case, allocations["gaming"])