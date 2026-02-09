"""Build complete rule lookup table quickly."""
import requests
import json
import pickle

BASE = "http://localhost:9001"

def get_neighborhood_tuple(grid, i, j):
    """Get neighbors as a tuple."""
    n, m = len(grid), len(grid[0])
    neighbors = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            neighbors.append(grid[ni][nj])
    return tuple(neighbors)

print("Building rule table (fast)...")

rule_table = {}

for seed in [42, 123, 456, 789]:
    print(f"  Processing seed {seed}...")
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    ep_id = resp.json()["episode_id"]
    actual_state = resp.json()["state"]

    for step in range(10):
        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        actual_next = resp.json()["state"]

        for i in range(9):
            for j in range(9):
                cell_state = actual_state[i][j]
                parity = (i + j) % 2
                neighbors = get_neighborhood_tuple(actual_state, i, j)
                next_state = actual_next[i][j]

                key = (parity, cell_state, neighbors)
                if key in rule_table and rule_table[key] != next_state:
                    print(f"WARNING: Inconsistent rule!")
                rule_table[key] = next_state

        actual_state = actual_next

print(f"\nCollected {len(rule_table)} unique rules")

# Save as pickle for easy loading
with open("e:/toy-physics discovery/experiments2/rule_table.pkl", "wb") as f:
    pickle.dump(rule_table, f)

print("Saved to rule_table.pkl")

# Test it
def apply_rule(grid, rule_table):
    new_grid = [[0]*9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            cell_state = grid[i][j]
            parity = (i + j) % 2
            neighbors = get_neighborhood_tuple(grid, i, j)
            key = (parity, cell_state, neighbors)

            if key in rule_table:
                new_grid[i][j] = rule_table[key]
            else:
                # Default: keep current state
                new_grid[i][j] = cell_state

    return new_grid

# Test
print("\nTesting on seed 9999...")
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 9999, "init_state": None})
ep_id = resp.json()["episode_id"]
test_state = resp.json()["state"]

correct = 0
total = 0

for step in range(10):
    predicted = apply_rule(test_state, rule_table)

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    for i in range(9):
        for j in range(9):
            total += 1
            if predicted[i][j] == actual_next[i][j]:
                correct += 1

    test_state = actual_next

print(f"Accuracy: {correct/total*100:.1f}%")
