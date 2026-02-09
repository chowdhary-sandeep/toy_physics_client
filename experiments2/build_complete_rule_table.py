"""Build complete rule lookup table and test it."""
import requests
import json

BASE = "http://localhost:9001"

def get_neighborhood_tuple(grid, i, j):
    """Get neighbors as a tuple (for hashing)."""
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

# Build rule table from many episodes with different seeds
print("Building complete rule table...")

rule_table = {}  # (parity, cell_state, neighbors_tuple) -> next_state

for seed in [42, 123, 456, 789, 1001, 2023, 3141, 5555]:
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    ep_id = resp.json()["episode_id"]
    actual_state = resp.json()["state"]

    for step in range(20):
        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        actual_next = resp.json()["state"]

        for i in range(9):
            for j in range(9):
                cell_state = actual_state[i][j]
                parity = (i + j) % 2
                neighbors = get_neighborhood_tuple(actual_state, i, j)
                next_state = actual_next[i][j]

                key = (parity, cell_state, neighbors)

                # Check consistency
                if key in rule_table:
                    if rule_table[key] != next_state:
                        print(f"WARNING: Inconsistent rule at {key}")
                else:
                    rule_table[key] = next_state

        actual_state = actual_next

print(f"Collected {len(rule_table)} unique rule entries")

# Save rule table
with open("e:/toy-physics discovery/experiments2/rule_table.json", "w") as f:
    # Convert keys to strings for JSON
    json_table = {}
    for key, value in rule_table.items():
        parity, cell_state, neighbors = key
        key_str = f"{parity},{cell_state},{neighbors}"
        json_table[key_str] = value
    json.dump(json_table, f, indent=2)

print("Rule table saved to rule_table.json")

# Test the rule table
print("\nTesting rule table accuracy...")

def apply_rule_table(grid, rule_table):
    """Apply the learned rule table."""
    new_grid = [[0]*9 for _ in range(9)]
    unknown_count = 0

    for i in range(9):
        for j in range(9):
            cell_state = grid[i][j]
            parity = (i + j) % 2
            neighbors = get_neighborhood_tuple(grid, i, j)
            key = (parity, cell_state, neighbors)

            if key in rule_table:
                new_grid[i][j] = rule_table[key]
            else:
                # Unknown pattern - use default (majority vote?)
                neighbor_sum = sum(neighbors)
                new_grid[i][j] = 1 if neighbor_sum >= 4 else 0
                unknown_count += 1

    return new_grid, unknown_count

# Test on a fresh seed
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 9999, "init_state": None})
ep_id = resp.json()["episode_id"]
test_state = resp.json()["state"]

total_cells = 0
correct_cells = 0
total_unknown = 0

for step in range(20):
    predicted, unknown = apply_rule_table(test_state, rule_table)

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    for i in range(9):
        for j in range(9):
            total_cells += 1
            if predicted[i][j] == actual_next[i][j]:
                correct_cells += 1

    total_unknown += unknown
    test_state = actual_next

accuracy = correct_cells / total_cells * 100
print(f"Accuracy: {accuracy:.1f}%")
print(f"Unknown patterns encountered: {total_unknown} out of {total_cells}")

if accuracy > 99:
    print("\nSUCCESS! Rule table captures the system with high accuracy!")
elif accuracy > 95:
    print("\nGood! Rule table mostly captures the system.")
    print("Remaining errors likely from unseen patterns.")
else:
    print("\nRule table is incomplete or system has additional complexity.")
