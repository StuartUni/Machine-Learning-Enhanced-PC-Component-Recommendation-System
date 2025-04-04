# Created by: Stuart Smith, Student ID: S2336002
# Date Created: 2025-04-02
# Description: Main entry point for hybrid recommendation logic combining content-based (Sklearn), collaborative (TFRS), and compatibility filtering.

import os
import sys

# ✅ Add the parent directory (backend/) to sys.path so Python can find recommender/ and utils/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(BACKEND_DIR)
from recommender.tfidf_game_matcher import find_best_matching_game, update_tfidf_model
from recommender.budget_allocator import get_budget_allocation
from utils.component_matcher import match_requirements_to_components
from utils.steam_api_fetcher import get_game_system_requirements

# ✅ Main Hybrid Recommendation Function
def get_hybrid_recommendation(user_input: dict) -> dict:
    """
    Handles incoming recommendation request, determines use case or game,
    invokes the appropriate models and returns a hybrid recommendation.
    """
    budget = user_input.get("budget", 1000)
    query = user_input.get("query", "gaming")

    # 🧠 Step 1: Use TF-IDF to check if it's a game
    matched_game = find_best_matching_game(query)
    if not matched_game:
        # TF-IDF failed, try fetching fresh from Steam
        print("🌐 No TF-IDF match found — trying Steam API...")
        from utils.steam_api_fetcher import get_game_system_requirements, save_game_requirements
        game_requirements = get_game_system_requirements(query, budget)

        if "error" in game_requirements:
            print(f"❌ Steam Error: {game_requirements['error']}")
            use_case = query  # treat as non-game
            matched_game = None
        else:
            matched_game = game_requirements["game"]
            save_game_requirements(matched_game, game_requirements)  # 📝 Save to JSON
            update_tfidf_model()  # 🔁 Rebuild TF-IDF
            print(f"✅ Fetched and saved new game: {matched_game}")
            use_case = "gaming"
    else:
        print(f"🎮 Matched Game: {matched_game}")
        use_case = "gaming"

    # 💰 Step 2: Get budget allocation
    allocation = get_budget_allocation(use_case)

    # 🎯 Step 3: If it's a game, try matching system requirements to parts
    if matched_game:
        print("🔍 Fetching system requirements from Steam...")
        game_requirements = get_game_system_requirements(matched_game, budget)

        if "error" not in game_requirements:
            print("⚙️ Matching components...")
            compatible_parts, total = match_requirements_to_components(
                game_requirements.get("minimum_requirements", {}),
                budget
            )

            print("✅ Compatible Parts Found:")
            for k, v in compatible_parts.items():
                print(f"  {k}: {v['name']} - ${v['original_price']:.2f}" if isinstance(v, dict) else f"  {k}: {v}")

            return {
                "use_case": matched_game,
                "budget_allocation": allocation,
                "recommended_build": compatible_parts,
                "total_cost": round(total, 2)
            }
        else:
            print(f"❌ Steam Error: {game_requirements['error']}")

    # 🧯 Step 4: Fallback (no game, no requirements found)
    return {
        "use_case": matched_game if matched_game else query,
        "budget_allocation": allocation,
        "recommended_build": {},
        "total_cost": 0
    }

# 🧪 Local Test Runner
if __name__ == "__main__":
    test_input = {
        "budget": 1200,
        "query": "Cyberpunk 2077"
    }

    result = get_hybrid_recommendation(test_input)
    print("✅ Hybrid Recommendation Result:")
    print(result)