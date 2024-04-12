# Define the initial liquidity ratios for each token pair
liquidity_data = {
    ("tokenA", "tokenB"): (17, 10),
    ("tokenA", "tokenC"): (11, 7),
    ("tokenA", "tokenD"): (15, 9),
    ("tokenA", "tokenE"): (21, 5),
    ("tokenB", "tokenC"): (36, 4),
    ("tokenB", "tokenD"): (13, 6),
    ("tokenB", "tokenE"): (25, 3),
    ("tokenC", "tokenD"): (30, 12),
    ("tokenC", "tokenE"): (10, 8),
    ("tokenD", "tokenE"): (60, 25),
}

# Expand liquidity data to include reverse pairs
updated_liquidity = {}
for pair, reserves in liquidity_data.items():
    updated_liquidity[pair] = reserves
    updated_liquidity[(pair[1], pair[0])] = (reserves[1], reserves[0])


def calculateOutput(amount, reserve_input, reserve_output):
    """Calculates the output amount with a trading fee."""
    input_fee = amount * 997
    numerator = input_fee * reserve_output
    denominator = reserve_input * 1000 + input_fee
    return numerator / denominator


def executeTrade(token_from, token_to, amount, liquidity):
    """Executes a trade between two tokens and updates liquidity."""
    if token_from == token_to:
        return amount
    reserves = liquidity[(token_from, token_to)]
    output_amount = calculateOutput(amount, reserves[0], reserves[1])
    new_input_reserve = reserves[0] + amount
    new_output_reserve = reserves[1] - output_amount
    liquidity[(token_from, token_to)] = (new_input_reserve, new_output_reserve)
    liquidity[(token_to, token_from)] = (new_output_reserve, new_input_reserve)
    return output_amount


def exploreRoutes(token, amount, visited, liquidity_snapshot, results):
    """Explore all possible trading routes from the given token to 'tokenB'."""
    if token == "tokenB" and visited:
        results.append((["tokenB"] + visited, amount))
        return
    for (src, dst) in liquidity_snapshot:
        if src == token and not visited.count(dst):
            new_visited = visited.copy()
            new_liquidity = liquidity_snapshot.copy()
            new_visited.append(dst)
            traded_amount = executeTrade(src, dst, amount, new_liquidity)
            exploreRoutes(dst, traded_amount, new_visited, new_liquidity, results)


def simulateTrades(route, initial_amount, liquidity):
    """Simulate trades along a specified route and print each step."""
    print(f"Starting with {initial_amount} {route[0]}")
    current_amount = initial_amount
    for i in range(len(route)-1):
        prev_amount = current_amount
        current_amount = executeTrade(route[i], route[i+1], current_amount, liquidity)
        print(f"Swapped {prev_amount} {route[i]} for {current_amount} {route[i+1]}")

# Find the best route starting from 'tokenB' with an initial amount
results = []
exploreRoutes("tokenB", 5, [], updated_liquidity, results)
results.sort(key=lambda x: x[1], reverse=True)
optimal_route, optimal_output = results[0]

print(f"Optimal path: {'->'.join(optimal_route)}, tokenB ending balance={optimal_output}")

# Optionally simulate the trades along the best route
# simulateTrades(optimal_route, 5, updated_liquidity.copy())
