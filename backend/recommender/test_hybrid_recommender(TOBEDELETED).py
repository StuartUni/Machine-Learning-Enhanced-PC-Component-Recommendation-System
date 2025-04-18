# Created by: Stuart Smith
# Student ID: S2336002
# Date Created: 2025-04-17
# Description:
# CLI Tester for Hybrid Recommender System with collaborative recommendation mini-table.

import json
from hybrid_recommender import get_hybrid_recommendation

def print_separator():
    print("=" * 80)

def print_collaborative_recommendations(collab_recs):
    if not collab_recs:
        print("\nNo collaborative recommendations available.")
        return

    print("\n📋 Top Collaborative Recommendations:")
    print("-" * 80)
    print(f"{'Build ID':<38} | {'CPU':<20} | {'GPU':<20} | {'Price ($)':>10}")
    print("-" * 80)
    for rec in collab_recs:
        print(f"{rec['build_id']:<38} | {rec['cpu']:<20} | {rec['gpu']:<20} | {rec['price']:>10}")
    print("-" * 80)

def run_test(test_name, input_payload):
    print_separator()
    print(f"🧪 Test: {test_name}")
    print_separator()

    result = get_hybrid_recommendation(input_payload)
    print(json.dumps(result, indent=2))

    if "collaborative_top_k" in result:
        print_collaborative_recommendations(result["collaborative_top_k"])

    print_separator()
    print(f"✅ Finished: {test_name}")
    print("\n")

def main():
    tests = [
        {
            "name": "General use case (content-based)",
            "input": {
                "budget": 1000,
                "query": "general",
                "user_id": "27",  # ✅ real user_id
                "mode": "content"
            }
        },
        {
            "name": "Gaming use case (hybrid, known game)",
            "input": {
                "budget": 1500,
                "query": "Cyberpunk 2077",
                "user_id": "27",  # ✅ real user_id
                "mode": "hybrid"
            }
        },
        {
            "name": "Gaming use case (hybrid, unknown game)",
            "input": {
                "budget": 1200,
                "query": "Unknown Super Racing Game",
                "user_id": "27",  # ✅ real user_id
                "mode": "hybrid"
            }
        },
        {
            "name": "Collaborative only mode (school use case)",
            "input": {
                "budget": 900,
                "query": "school",
                "user_id": "27",  # ✅ real user_id
                "mode": "collaborative"
            }
        }
    ]

    for test in tests:
        run_test(test["name"], test["input"])

if __name__ == "__main__":
    main()