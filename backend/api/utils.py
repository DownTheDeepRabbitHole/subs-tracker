import os
import requests
from dotenv import load_dotenv
from urllib.parse import (
    quote,
)  # https://stackoverflow.com/questions/21823965/use-20-instead-of-for-space-in-python-query-parameters

# Load environment variables
load_dotenv()

# Constants
LOGODEV_API_SKEY = os.getenv("LOGODEV_API_SKEY")
LOGODEV_API_URL = "https://api.logo.dev"
DEFAULT_ICON_URL = (
    "https://icons.veryicon.com/png/o/business/settlement-platform-icon/default-16.png"
)


def get_icon_url(name):
    api_url = f"{LOGODEV_API_URL}/search?q={quote(name)}"
    headers = {"Authorization": f"Bearer {LOGODEV_API_SKEY}"}

    response = requests.get(api_url, headers=headers)

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        if data:
            logo_url = data[0].get("logo_url")
            if logo_url:
                return f"{logo_url}&format=webp&retina=true"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching icon URL: {e}")

    return DEFAULT_ICON_URL

def get_avatar_url(username):
    return f"https://avatar.iran.liara.run/public?username={username}"


def _knapsack(i, remaining, plans, memo):
    """Recursive 01 knapsack, using 2d dictionary of tuples (pairs) as key to save memory (~O(W) vs O(WV))"""
    if remaining < 0:
        return -float("inf")
    if i >= len(plans) or remaining == 0:
        return 0
    if (i, remaining) in memo:
        return memo[(i, remaining)]

    current = plans[i]
    # Explore exclusion path
    exclude = _knapsack(i + 1, remaining, plans, memo)

    # Explore inclusion path
    include = current["usage_score"] + _knapsack(
        i + 1, remaining - current["scaled_cost"], plans, memo
    )

    # Choose maximum value between the two and store in memo
    max_val = max(exclude, include) if current["scaled_cost"] <= remaining else exclude
    memo[(i, remaining)] = max_val
    return max_val


def budget_plans(user_plans, original_budget):
    """
    Finds optimat set of subscriptions to include w/in a given budget
    Checks combinations of plan costs (weights) while maximizing usage score (value)
    Returns list of plan ids included in the budget
    """
    # Preprocess and sort plans by cost to usage score ratio (can prune suboptimal paths sooner), and rounds costs to use for memo
    processed = sorted(
        (
            {
                "id": p["id"],
                "usage_score": p["usage_score"],
                "scaled_cost": round(p["cost"]),
                "value_density": p["usage_score"] / max(p["cost"], 1e-9),
            }
            for p in user_plans
        ),
        key=lambda x: (-x["value_density"], x["scaled_cost"]),
    )

    # Initialize memoization table and solve (build memo table)
    budget = round(original_budget)
    memo = {}
    max_score = _knapsack(0, budget, processed, memo)

    # Backtracks through memo table to reconstruct optimal selections
    selected = []
    remaining_budget = budget

    for idx, plan in enumerate(processed):
        cost = plan["scaled_cost"]
        if remaining_budget < cost:
            continue

        # Check if current plan was included in optimal solution
        with_current = (
            memo.get((idx + 1, remaining_budget - cost), 0) + plan["usage_score"]
        )
        if memo.get((idx, remaining_budget), 0) == with_current:
            selected.append(plan["id"])
            remaining_budget -= cost

    return selected
