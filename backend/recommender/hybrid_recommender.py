
import os
import sys
import json
import pandas as pd
import tensorflow as tf
import uuid
from tensorflow.keras.models import load_model

# ✅ Set up paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(BACKEND_DIR)

# ✅ Imports
from models.train_tfrs_check import train_if_needed
from recommender.tfidf_game_matcher import find_best_matching_game, update_tfidf_model
from recommender.budget_allocator import get_budget_allocation
from recommender.content_recommender import recommend_build_from_features
from utils.component_matcher import match_requirements_to_components
from utils.steam_api_fetcher import get_game_system_requirements, save_game_requirements
from utils.fallback_filler import fill_missing_components, component_data
from models.train_tfrs_model import BuildRankingModel

# ✅ Load models and builds
train_if_needed()
LABELED_PATH = os.path.join(BACKEND_DIR, "data", "builds", "labeled_builds.csv")
build_df = pd.read_csv(LABELED_PATH)
TFRS_MODEL_PATH = os.path.join(BACKEND_DIR, "models", "tfrs_model.keras")
tfrs_model = load_model(TFRS_MODEL_PATH, custom_objects={"BuildRankingModel": BuildRankingModel})

# ✅ Calculate real-world total cost
def calculate_real_total_cost(build: dict) -> float:
    total = 0.0
    for part_key in ["CPU", "GPU", "Motherboard", "RAM", "PSU", "Case"]:
        part = build.get(part_key)
        if part and "original_price" in part:
            total += part["original_price"]
    return round(total, 2)


def clean_and_finalize_recommendation(build: dict, budget: float, allocation: dict) -> dict:
    build["build_id"] = str(uuid.uuid4())

    total_cost = calculate_real_total_cost(build)
    
    # ✅ Manually add Storage and Cooler fixed prices
    total_cost += 50.00  # storage_price
    total_cost += 30.00  # cpu_cooler_price

    recommended_build = {
        "build_id": build["build_id"],
        "cpu_name": build.get("CPU", {}).get("name", "Unknown"),
        "cpu_price": build.get("CPU", {}).get("original_price", 0),
        "gpu_name": build.get("GPU", {}).get("name", "Unknown"),
        "gpu_price": build.get("GPU", {}).get("original_price", 0),
        "motherboard_name": build.get("Motherboard", {}).get("name", "Unknown"),
        "motherboard_price": build.get("Motherboard", {}).get("original_price", 0),
        "ram_name": build.get("RAM", {}).get("name", "Unknown"),
        "ram_price": build.get("RAM", {}).get("original_price", 0),
        "storage_name": "500GB SSD",
        "storage_price": 50.00,  # fallback
        "psu_name": build.get("PSU", {}).get("name", "Unknown"),
        "psu_price": build.get("PSU", {}).get("original_price", 0),
        "case_name": build.get("Case", {}).get("name", "Unknown"),
        "case_price": build.get("Case", {}).get("original_price", 0),
        "cpu_cooler_name": "Stock Cooler",
        "cpu_cooler_price": 30.00,
    }

    return {
        "recommended_build": recommended_build,
        "total_cost": round(total_cost, 2)
    }

# ✅ Collaborative recommendations
def get_top_k_collab_builds(user_id: str, budget: float, k=3):
    try:
        _, top_build_ids_tensor = tfrs_model.recommend(tf.constant([user_id]), k=k)
        top_build_ids = [b.decode().strip() for b in top_build_ids_tensor[0].numpy()]
        
        collab_builds = []
        for bid in top_build_ids:
            row = build_df[build_df["build_id"] == bid]
            if not row.empty:
                collab_builds.append({
                    "build_id": bid,
                    "cpu": row.iloc[0]["cpu_name"],
                    "gpu": row.iloc[0]["gpu_name"],
                    "price": round(row.iloc[0]["price"], 2)
                })
        return collab_builds
    except Exception as e:
        print(f"⚠️ Collaborative filtering failed: {e}")
        return []

# ✅ Hybrid recommender main logic
def get_hybrid_recommendation(user_input: dict) -> dict:
    budget = user_input.get("budget", 1000)
    query = user_input.get("query", "general").lower()
    user_id = str(user_input.get("user_id", "guest"))
    mode = user_input.get("mode", "hybrid")

    print(f"🔍 Normalized query = {query}")

    if mode == "collaborative":
        return {
            "use_case": query,
            "mode": "collaborative",
            "collaborative_top_k": get_top_k_collab_builds(user_id, budget)
        }

    NON_GAMING_QUERIES = ["general", "work", "school"]
    if query in NON_GAMING_QUERIES:
        allocation = get_budget_allocation(query)
        print(f"🛠 Using content-based filtering for non-gaming use case: {query}")
        print(f"🔍 Budget Allocation for {query}: {allocation}")

        
        build_response = recommend_build_from_features(use_case=query, budget=budget, allocation=allocation)

        build = build_response["build"]  # ✅ Extract the actual build
        cleaned = clean_and_finalize_recommendation(build, budget, allocation)

        result = {
            "use_case": query,
            "mode": mode,
            "budget_allocation": allocation,
            **cleaned
        }

        if mode == "hybrid":
            result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)

        return result

    # 🎮 Gaming flow
    matched_game = find_best_matching_game(query)
    if not matched_game:
        print("🔍 No TF-IDF match — checking Steam API...")
        game_requirements = get_game_system_requirements(query, budget)
        if "error" in game_requirements:
            print(f"❌ Game not found: {game_requirements['error']}")
            return {
                "use_case": query,
                "mode": mode,
                "budget_allocation": get_budget_allocation("gaming"),
                "recommended_build": {},
                "total_cost": 0
            }
        matched_game = game_requirements["game"]
        save_game_requirements(matched_game, game_requirements)
        update_tfidf_model()

    print(f"🎮 Matched Game: {matched_game} — retrieving requirements...")
    game_requirements = get_game_system_requirements(matched_game, budget)
    allocation = get_budget_allocation("gaming")
    print(f"🔍 Budget Allocation for {matched_game}: {allocation}")

    if "error" in game_requirements:
        print(f"❌ Steam API error after match: {game_requirements['error']}")
        return {
            "use_case": matched_game,
            "mode": mode,
            "budget_allocation": allocation,
            "recommended_build": {},
            "total_cost": 0
        }

    print("⚙️ Matching components from requirements...")
    compatible_parts, raw_total = match_requirements_to_components(
        game_requirements.get("recommended_requirements", {}), budget
    )

    print(f"🔍 Selected Compatible Parts: {compatible_parts}")
    print(f"🔍 Raw Total Price: {raw_total}")


    build = compatible_parts

    final_cleaned = clean_and_finalize_recommendation(build, budget, allocation)

    # ✅ Final Result
    result = {
        "use_case": matched_game,
        "mode": mode,
        "budget_allocation": allocation,
        **final_cleaned
    }

    if mode == "hybrid":
        result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)

    return result