"""Test if the rule depends on cell position (checkerboard parity)."""
import requests
from collections import defaultdict

BASE = "http://localhost:9001"

def count_neighbors_toroidal(grid, i, j):
    n, m = len(grid), len(grid[0])
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            count += grid[ni][nj]
    return count

# Collect transitions with position info
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

# Rule with position: (cell_state, neighbors, parity) -> [next_states]
# Parity: (i+j)%2 gives checkerboard pattern (0 or 1)
rule_by_parity = defaultdict(lambda: defaultdict(list))

print("Collecting transitions with position info...")

for step in range(30):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    for i in range(9):
        for j in range(9):
            cell_state = actual_state[i][j]
            neighbors = count_neighbors_toroidal(actual_state, i, j)
            next_state = actual_next[i][j]
            parity = (i + j) % 2

            key = (cell_state, neighbors)
            rule_by_parity[parity][key].append(next_state)

    actual_state = actual_next

print("\nRule Analysis by Checkerboard Parity:")
print("="*70)

# Check if rule differs by parity
for parity in [0, 1]:
    parity_name = "EVEN (i+j even)" if parity == 0 else "ODD (i+j odd)"
    print(f"\n{parity_name}:")
    print("-" * 70)

    rule = rule_by_parity[parity]
    for key in sorted(rule.keys()):
        cell_state, neighbors = key
        outcomes = rule[key]
        n_total = len(outcomes)
        n_alive = sum(outcomes)

        state_str = "ALIVE" if cell_state == 1 else "DEAD"

        if n_alive == 0:
            result = "-> DEAD"
        elif n_alive == n_total:
            result = "-> ALIVE"
        else:
            prob = n_alive / n_total
            result = f"-> ALIVE {prob:.0%}"

        print(f"  {state_str:5s} + {neighbors}n {result:12s} (n={n_total})")

# Check if parity makes the rule deterministic
print("\n" + "="*70)
print("Checking if parity explains the variations...")

still_stochastic = False
for parity in [0, 1]:
    for key, outcomes in rule_by_parity[parity].items():
        if len(set(outcomes)) > 1:
            still_stochastic = True
            cell_state, neighbors = key
            state_str = "ALIVE" if cell_state == 1 else "DEAD"
            parity_name = "EVEN" if parity == 0 else "ODD"
            prob = sum(outcomes) / len(outcomes)
            print(f"  {parity_name}, {state_str}, {neighbors}n: still varies ({prob:.0%}, n={len(outcomes)})")

if not still_stochastic:
    print("  SUCCESS! Parity makes the rule fully deterministic!")
else:
    print("  Parity helps but doesn't fully explain the rule")
