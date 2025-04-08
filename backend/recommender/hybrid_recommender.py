# # Created by: Stuart Smith
# # Student ID: S2336002
# # Date Created: 2025-04-07
# # Description:
# # This script handles hybrid PC component recommendations.
# # For non-gaming queries (e.g., general, work, school), it uses a trained ML model.
# # For gaming queries, it optionally uses TF-IDF + Steam API to estimate requirements,
# # which are passed to a compatibility matcher to generate a feature vector.
# # If a user_id is provided, it also returns collaborative recommendations using TFRS.
# # Supports modes: "content", "collaborative", or "hybrid".

# import os
# import sys
# import json
# import pandas as pd
# import tensorflow as tf
# from tensorflow.keras.models import load_model



# # ✅ Set up paths for backend imports
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
# sys.path.append(BACKEND_DIR)


# # ✅ Check if TFRS model exists and train if needed
# from models.train_tfrs_check import train_if_needed
# train_if_needed()



# from recommender.tfidf_game_matcher import find_best_matching_game, update_tfidf_model
# from recommender.budget_allocator import get_budget_allocation
# from recommender.content_recommender import recommend_build_from_features
# from utils.component_matcher import match_requirements_to_components
# from utils.steam_api_fetcher import get_game_system_requirements, save_game_requirements
# from models.train_tfrs_model import BuildRankingModel

# # ✅ Load labeled builds and TFRS model
# LABELED_PATH = os.path.join(BACKEND_DIR, "data", "builds", "labeled_builds.csv")
# build_df = pd.read_csv(LABELED_PATH)
# TFRS_MODEL_PATH = os.path.join(BACKEND_DIR, "models", "tfrs_model.keras")
# tfrs_model = load_model(TFRS_MODEL_PATH, custom_objects={"BuildRankingModel": BuildRankingModel})


# def clean_and_finalize_recommendation(build: dict, budget: float) -> dict:
#     if "ram_ddr5_name" in build:
#         build["ram_name"] = build["ram_ddr5_name"]
#     elif "ram_ddr4_name" in build:
#         build["ram_name"] = build["ram_ddr4_name"]
#     build.pop("ram_ddr4_name", None)
#     build.pop("ram_ddr5_name", None)

#     total = budget * build.get("price", 0)
#     if total > budget:
#         print(f"⚠️ Build over budget by ${total - budget:.2f}. Consider downgrading optional parts.")
#     return {
#         "recommended_build": build,
#         "total_cost": round(total, 2)
#     }


# def get_top_k_collab_builds(user_id: str, budget: float, k=3):
#     try:
#         _, top_build_ids_tensor = tfrs_model.recommend(tf.constant([user_id]), k=k)
#         top_build_ids = [b.decode() for b in top_build_ids_tensor[0].numpy()]

#         collab_builds = []
#         for bid in top_build_ids:
#             row = build_df[build_df["build_id"] == bid]
#             if not row.empty:
#                 collab_builds.append({
#                     "build_id": bid,
#                     "cpu": row.iloc[0]["cpu_name"],
#                     "gpu": row.iloc[0]["gpu_name"],
#                     "price": round(float(row.iloc[0]["price"]) * budget, 2)
#                 })
#         print(f"🧠 TFRS Top Collaborative Builds for {user_id}: {collab_builds}")
#         return collab_builds
#     except Exception as e:
#         print(f"⚠️ TFRS collaborative filtering failed: {e}")
#         return []


# def get_hybrid_recommendation(user_input: dict) -> dict:
#     budget = user_input.get("budget", 1000)
#     query = user_input.get("query", "general").lower()
#     user_id = str(user_input.get("user_id", "guest"))
#     mode = user_input.get("mode", "hybrid")

#     print(f"📥 Request received: budget={budget}, query={query}, mode={mode}")

#     if mode == "collaborative":
#         return {
#             "use_case": query,
#             "mode": "collaborative",
#             "collaborative_top_k": get_top_k_collab_builds(user_id, budget)
#         }

#     NON_GAMING_QUERIES = ["general", "work", "school"]
#     if query in NON_GAMING_QUERIES:
#         allocation = get_budget_allocation(query)
#         print(f"🛠 Using content-based filtering for non-gaming use case: {query}")
#         build = recommend_build_from_features(use_case=query, budget=budget, allocation=allocation)
#         cleaned = clean_and_finalize_recommendation(build["build"], budget)

#         result = {
#             "use_case": query,
#             "mode": mode,
#             "budget_allocation": allocation,
#             **cleaned
#         }

#         if mode == "hybrid":
#             result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)

#         return result

#     # 🎮 Gaming logic...
#     matched_game = find_best_matching_game(query)
#     if not matched_game:
#         print("🔍 No TF-IDF match — checking Steam API...")
#         game_requirements = get_game_system_requirements(query, budget)
#         if "error" in game_requirements:
#             print(f"❌ Game not found: {game_requirements['error']}")
#             fallback_build = build_best_pc_under_budget(budget)
#             return {
#                 "use_case": query,
#                 "mode": mode,
#                 "budget_allocation": get_budget_allocation("gaming"),
#                 "recommended_build": fallback_build["build"],
#                 "total_cost": fallback_build["total"]
#             }
#         matched_game = game_requirements["game"]
#         save_game_requirements(matched_game, game_requirements)
#         update_tfidf_model()

#     print(f"🎮 Matched Game: {matched_game} — retrieving requirements...")
#     game_requirements = get_game_system_requirements(matched_game, budget)
#     allocation = get_budget_allocation("gaming")

#     if "error" in game_requirements:
#         print(f"❌ Steam error after match: {game_requirements['error']}")
#         fallback_build = build_best_pc_under_budget(budget)
#         return {
#             "use_case": matched_game,
#             "mode": mode,
#             "budget_allocation": allocation,
#             "recommended_build": fallback_build["build"],
#             "total_cost": fallback_build["total"]
#         }

#     print("⚙️ Matching components from requirements...")
#     compatible_parts, raw_total = match_requirements_to_components(
#         game_requirements.get("minimum_requirements", {}), budget
#     )

#     if compatible_parts["CPU"] and compatible_parts["GPU"]:
#         raw_price = sum(v["original_price"] for v in compatible_parts.values() if isinstance(v, dict))
#         normalized_price = raw_price / budget
#         user_features = {
#             "cpu_score": compatible_parts["CPU"]["performance_score"],
#             "gpu_score": compatible_parts["GPU"]["performance_score"],
#             "ram_gb": int(compatible_parts["RAM"].replace(" GB", "")) if isinstance(compatible_parts["RAM"], str) else 16,
#             "storage_gb": 512,
#             "price": normalized_price
#         }

#         top_builds = recommend_build_from_features(user_features=user_features, top_k=1)
#         if top_builds:
#             cleaned = clean_and_finalize_recommendation(top_builds[0], budget)
#             result = {
#                 "use_case": matched_game,
#                 "mode": mode,
#                 "budget_allocation": allocation,
#                 **cleaned
#             }
#             if mode == "hybrid":
#                 result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)
#             return result

#     return {
#         "use_case": matched_game,
#         "mode": mode,
#         "budget_allocation": allocation,
#         "recommended_build": compatible_parts,
#         "total_cost": round(raw_total, 2)
#     }


# # ✅ CLI Test Entry Point
# if __name__ == "__main__":
#     test_input = {
#         "budget": 900,
#         "query": "general",
#         "user_id": "9",  # ✅ existing user_id from ratings
#         "mode": "hybrid"
#     }

#     result = get_hybrid_recommendation(test_input)
#     print("✅ Recommendation Result:")
#     print(json.dumps(result, indent=2))



# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-07
# Description:
# This script handles hybrid PC component recommendations.
# For non-gaming queries (e.g., general, work, school), it uses a trained ML model.
# For gaming queries, it optionally uses TF-IDF + Steam API to estimate requirements,
# which are passed to a compatibility matcher to generate a feature vector.
# If a user_id is provided, it also returns collaborative recommendations using TFRS.
# Supports modes: "content", "collaborative", or "hybrid".

import os
import sys
import json
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model

# ✅ Set up paths for backend imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(BACKEND_DIR)

# ✅ Check if TFRS model exists and train if needed
from models.train_tfrs_check import train_if_needed
train_if_needed()

from recommender.tfidf_game_matcher import find_best_matching_game, update_tfidf_model
from recommender.budget_allocator import get_budget_allocation
from recommender.content_recommender import recommend_build_from_features
from utils.component_matcher import match_requirements_to_components
from utils.steam_api_fetcher import get_game_system_requirements, save_game_requirements
from models.train_tfrs_model import BuildRankingModel

# ✅ Load labeled builds and TFRS model
LABELED_PATH = os.path.join(BACKEND_DIR, "data", "builds", "labeled_builds.csv")
build_df = pd.read_csv(LABELED_PATH)
TFRS_MODEL_PATH = os.path.join(BACKEND_DIR, "models", "tfrs_model.keras")
tfrs_model = load_model(TFRS_MODEL_PATH, custom_objects={"BuildRankingModel": BuildRankingModel})


def clean_and_finalize_recommendation(build: dict, budget: float) -> dict:
    if "ram_ddr5_name" in build:
        build["ram_name"] = build["ram_ddr5_name"]
    elif "ram_ddr4_name" in build:
        build["ram_name"] = build["ram_ddr4_name"]
    build.pop("ram_ddr4_name", None)
    build.pop("ram_ddr5_name", None)

    total = budget * build.get("price", 0)
    if total > budget:
        print(f"⚠️ Build over budget by ${total - budget:.2f}. Consider downgrading optional parts.")
    return {
        "recommended_build": build,
        "total_cost": round(total, 2)
    }


def get_top_k_collab_builds(user_id: str, budget: float, k=3):
    try:
        _, top_build_ids_tensor = tfrs_model.recommend(tf.constant([user_id]), k=k)
        top_build_ids = [b.decode() for b in top_build_ids_tensor[0].numpy()]
        # 🔍 Debug: Check if all build IDs are present in labeled_builds.csv
        missing = [bid for bid in top_build_ids if bid not in build_df["build_id"].values]
        print(f"🚫 Missing from labeled_builds.csv: {missing}")

        # 🔍 Debug: Show raw build IDs returned by model
        print(f"🔍 Raw collaborative build IDs returned: {top_build_ids}")

        collab_builds = []
        for bid in top_build_ids:
            row = build_df[build_df["build_id"] == bid]
            if not row.empty:
                collab_builds.append({
                    "build_id": bid,
                    "cpu": row.iloc[0]["cpu_name"],
                    "gpu": row.iloc[0]["gpu_name"],
                    "price": round(float(row.iloc[0]["price"]) * budget, 2)
                })
        print(f"🧠 TFRS Top Collaborative Builds for {user_id}: {collab_builds}")
        return collab_builds
    except Exception as e:
        print(f"⚠️ TFRS collaborative filtering failed: {e}")
        return []


def get_hybrid_recommendation(user_input: dict) -> dict:
    budget = user_input.get("budget", 1000)
    query = user_input.get("query", "general").lower()
    user_id = str(user_input.get("user_id", "guest"))
    mode = user_input.get("mode", "hybrid")

    print(f"📥 Request received: budget={budget}, query={query}, mode={mode}")

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
        build = recommend_build_from_features(use_case=query, budget=budget, allocation=allocation)
        cleaned = clean_and_finalize_recommendation(build["build"], budget)

        result = {
            "use_case": query,
            "mode": mode,
            "budget_allocation": allocation,
            **cleaned
        }

        if mode == "hybrid":
            result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)

        return result

    # 🎮 Gaming logic...
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

    if "error" in game_requirements:
        print(f"❌ Steam error after match: {game_requirements['error']}")
        return {
            "use_case": matched_game,
            "mode": mode,
            "budget_allocation": allocation,
            "recommended_build": {},
            "total_cost": 0
        }

    print("⚙️ Matching components from requirements...")
    compatible_parts, raw_total = match_requirements_to_components(
        game_requirements.get("minimum_requirements", {}), budget
    )

    if compatible_parts["CPU"] and compatible_parts["GPU"]:
        raw_price = sum(v["original_price"] for v in compatible_parts.values() if isinstance(v, dict))
        normalized_price = raw_price / budget
        user_features = {
            "cpu_score": compatible_parts["CPU"]["performance_score"],
            "gpu_score": compatible_parts["GPU"]["performance_score"],
            "ram_gb": int(compatible_parts["RAM"].replace(" GB", "")) if isinstance(compatible_parts["RAM"], str) else 16,
            "storage_gb": 512,
            "price": normalized_price
        }

        top_builds = recommend_build_from_features(user_features=user_features, top_k=1)
        if top_builds:
            cleaned = clean_and_finalize_recommendation(top_builds[0], budget)
            result = {
                "use_case": matched_game,
                "mode": mode,
                "budget_allocation": allocation,
                **cleaned
            }
            if mode == "hybrid":
                result["collaborative_top_k"] = get_top_k_collab_builds(user_id, budget)
            return result

    return {
        "use_case": matched_game,
        "mode": mode,
        "budget_allocation": allocation,
        "recommended_build": compatible_parts,
        "total_cost": round(raw_total, 2)
    }


# ✅ CLI Test Entry Point
if __name__ == "__main__":
    test_input = {
        "budget": 900,
        "query": "general",
        "user_id": "9",  # ✅ existing user_id from ratings
        "mode": "hybrid"
    }

    result = get_hybrid_recommendation(test_input)
    print("✅ Recommendation Result:")
    print(json.dumps(result, indent=2))