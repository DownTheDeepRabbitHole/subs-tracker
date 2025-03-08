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
DEFAULT_ICON_URL: str = (
    "https://icons.veryicon.com/png/o/business/settlement-platform-icon/default-16.png"
)


def get_icon_url(name):
    print(quote(name))
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


def knapsack_max_value(processed_plans, budget):
    """
    Compute maximum achievable usage score using top-down dynamic programming.
    
    Args:
        processed_plans: Plans sorted by value density descending
        budget: Total available budget in whole dollars
        
    Returns:
        Tuple of (max_score, memoization_table)
    """
    memo = {}
    
    def dp(i: int, remaining: int) -> int:
        """Recursive helper with memoization"""
        if remaining < 0:
            return -float('inf')
        if i >= len(processed_plans) or remaining == 0:
            return 0
        if (i, remaining) in memo:
            return memo[(i, remaining)]
        
        current = processed_plans[i]
        exclude = dp(i + 1, remaining)
        include = current['usage_score'] + dp(i + 1, remaining - current['scaled_cost'])
        
        memo[(i, remaining)] = max(exclude, include) if current['scaled_cost'] <= remaining else exclude
        return memo[(i, remaining)]
    
    max_score = dp(0, budget)
    return max_score, memo


def backtrack_selected_items(processed_plans, budget, memo):
    """
    Reconstruct selected items from DP memoization table.
    
    Args:
        processed_plans: Plans sorted by value density descending
        budget: Original budget used in DP
        memo: Memoization table from knapsack_max_value
        
    Returns:
        List of selected plan IDs in selection order
    """
    selected = []
    remaining = budget
    
    for i, plan in enumerate(processed_plans):
        cost = plan['scaled_cost']
        if remaining < cost:
            continue
            
        # Check if current plan was included
        score_with = memo.get((i + 1, remaining - cost), 0) + plan['usage_score']
        if memo.get((i, remaining), 0) == score_with:
            selected.append(plan['id'])
            remaining -= cost
            
    return selected


def budget_plans(user_plans, original_budget):
    """
    Optimal subscription planner using 0/1 knapsack algorithm.
    
    Args:
        user_plans: List of dictionaries with:
            - id: Plan identifier
            - usage_score: Non-negative integer value
            - cost: Positive dollar amount
        original_budget: Total available budget
        
    Returns:
        List of selected plan IDs that maximize usage score
    """
    # Preprocess and sort plans
    processed = sorted(
        (
            {
                'id': p['id'],
                'usage_score': p['usage_score'],
                'scaled_cost': round(p['cost']),
                'value_density': p['usage_score'] / max(p['cost'], 1e-9)
            }
            for p in user_plans
        ),
        key=lambda x: (-x['value_density'], x['scaled_cost'])
    )
    
    # Calculate optimal score and memoization table
    budget = round(original_budget)
    max_score, memo = knapsack_max_value(processed, budget)
    
    # Reconstruct selected items
    return backtrack_selected_items(processed, budget, memo)