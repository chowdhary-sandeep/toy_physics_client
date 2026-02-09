"""Test if the rule follows simple mathematical patterns."""
import requests

BASE = "http://localhost:9001"

def get_neighbors(grid, i, j):
    """Get all 8 neighbors as a list."""
    n, m = len(grid), len(grid[0])
    neighbors = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            neighbors.append(grid[ni][nj])
    return neighbors

def test_rule_hypothesis(grid, i, j, rule_func):
    """Test a specific rule hypothesis."""
    cell = grid[i][j]
    parity = (i + j) % 2
    neighbors = get_neighbors(grid, i, j)
    return rule_func(cell, parity, neighbors)

# Hypothesis 1: XOR-based rule
def xor_rule(cell, parity, neighbors):
    neighbor_sum = sum(neighbors)
    if parity == 0:  # EVEN
        # XOR with some pattern?
        return (cell + neighbor_sum) % 2
    else:  # ODD
        return (cell * neighbor_sum) % 2

# Hypothesis 2: Modular arithmetic
def mod_rule(cell, parity, neighbors):
    neighbor_sum = sum(neighbors)
    if parity == 0:
        return 1 if (cell + neighbor_sum) % 3 == 1 else 0
    else:
        return 1 if (cell + neighbor_sum) % 3 == 2 else 0

# Hypothesis 3: Threshold-based with parity offset
def threshold_rule(cell, parity, neighbors):
    neighbor_sum = sum(neighbors)
    if parity == 0:
        if cell == 1:
            return 1 if neighbor_sum in [1, 4, 5] else 0
        else:
            return 1 if neighbor_sum in [2, 4, 5] else 0
    else:
        if cell == 1:
            return 1 if neighbor_sum in [1, 3, 4, 5] else 0
        else:
            return 1 if neighbor_sum in [1, 3] else 0

# Test hypotheses
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

hypotheses = [
    ("XOR-based", xor_rule),
    ("Modular arithmetic", mod_rule),
    ("Threshold with parity", threshold_rule),
]

for name, rule_func in hypotheses:
    correct = 0
    total = 0

    test_state = [row[:] for row in actual_state]

    for step in range(10):
        # Predict next state
        predicted = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                predicted[i][j] = test_rule_hypothesis(test_state, i, j, rule_func)

        # Get actual next state
        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        actual_next = resp.json()["state"]

        # Count matches
        for i in range(9):
            for j in range(9):
                total += 1
                if predicted[i][j] == actual_next[i][j]:
                    correct += 1

        test_state = actual_next

    accuracy = correct / total * 100
    print(f"{name:25s}: {accuracy:5.1f}% accuracy")

print("\n" + "="*70)
print("Need to extract the exact lookup table for the CA rules...")
