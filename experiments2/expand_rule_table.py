"""Expand rule table with more data to reach 100% accuracy."""
import requests
import pickle

BASE = "http://localhost:9001"

def get_neighborhood_tuple(grid, i, j):
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

# Load existing rule table
with open("e:/toy-physics discovery/experiments2/rule_table.pkl", "rb") as f:
    rule_table = pickle.load(f)

print(f"Starting with {len(rule_table)} rules")

# Add more seeds
new_seeds = [1001, 2023, 3141, 4242, 5555, 6789, 7777, 8888, 9000, 10000]

for seed in new_seeds:
    print(f"  Processing seed {seed}...")
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    ep_id = resp.json()["episode_id"]
    actual_state = resp.json()["state"]

    for step in range(15):
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
                    print(f"WARNING: Inconsistency found!")
                rule_table[key] = next_state

        actual_state = actual_next

print(f"Expanded to {len(rule_table)} rules")

# Save
with open("e:/toy-physics discovery/experiments2/rule_table.pkl", "wb") as f:
    pickle.dump(rule_table, f)

# Test on multiple fresh seeds
def apply_rule(grid, rule_table):
    new_grid = [[0]*9 for _ in range(9)]
    missing = 0
    for i in range(9):
        for j in range(9):
            cell_state = grid[i][j]
            parity = (i + j) % 2
            neighbors = get_neighborhood_tuple(grid, i, j)
            key = (parity, cell_state, neighbors)

            if key in rule_table:
                new_grid[i][j] = rule_table[key]
            else:
                # Default
                new_grid[i][j] = cell_state
                missing += 1

    return new_grid, missing

print("\nTesting on fresh seeds...")

test_seeds = [11111, 22222, 33333]
for test_seed in test_seeds:
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": test_seed, "init_state": None})
    ep_id = resp.json()["episode_id"]
    test_state = resp.json()["state"]

    correct = 0
    total = 0
    total_missing = 0

    for step in range(20):
        predicted, missing = apply_rule(test_state, rule_table)
        total_missing += missing

        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        actual_next = resp.json()["state"]

        for i in range(9):
            for j in range(9):
                total += 1
                if predicted[i][j] == actual_next[i][j]:
                    correct += 1

        test_state = actual_next

    print(f"  Seed {test_seed}: {correct/total*100:.2f}% accuracy, {total_missing} missing patterns")

print("\nRule table complete!")
