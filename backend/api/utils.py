def knapsack(i, budget, user_plans, dp):
    """
    Top-down recursive knapsack using a 2D memoization table.
    
    :param i: Current index in user_plans
    :param budget: Remaining budget
    :param user_plans: List of dicts [{'id': 1, 'usage_score': 8, 'cost': 10}, ...]
    :param dp: 2D memoization table
    :return: Maximum usage score achievable within budget
    """
    if i < 0 or budget == 0:  # Base case: No more items or budget
        return 0

    if dp[i][budget] != -1:  # Return stored result if already computed
        return dp[i][budget]

    cost = user_plans[i]['cost']
    score = user_plans[i]['usage_score']

    # Case 1: Skip this subscription
    best = knapsack(i - 1, budget, user_plans, dp)

    # Case 2: Take this subscription (if within budget)
    if cost <= budget:
        best = max(best, score + knapsack(i - 1, budget - cost, user_plans, dp))

    dp[i][budget] = best  # Store result
    return best


def budget_plans(user_plans, budget):
    """
    Runs the top-down knapsack algorithm with a 2D DP table and backtracks to get selected subscriptions.

    :param user_plans: List of dicts [{'id': 1, 'usage_score': 8, 'cost': 10}, ...]
    :param budget: Integer representing max budget
    :return: List of selected UserPlan IDs
    """
    n = len(user_plans)
    dp = [[-1] * (budget + 1) for _ in range(n)]  # Initialize DP table with -1

    knapsack(n - 1, budget, user_plans, dp)  # Fill DP table

    # Backtrack to find selected subscriptions
    selected = []
    b = budget
    for i in range(n - 1, -1, -1):
        if i == 0 and dp[i][b] > 0:  # Edge case: first item is included
            selected.append(user_plans[i]['id'])
        elif i > 0 and dp[i][b] != dp[i - 1][b]:  # Item included
            selected.append(user_plans[i]['id'])
            b -= user_plans[i]['cost']
            if b <= 0:
                break

    return selected
