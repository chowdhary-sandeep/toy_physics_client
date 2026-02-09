"""Extract and simplify the rules for even and odd cells."""
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

# Collect lots of data
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

rule_by_parity = {0: defaultdict(list), 1: defaultdict(list)}

for step in range(50):
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

print("Simplified Rules by Parity (with large sample):")
print("="*70)

for parity in [0, 1]:
    parity_name = "EVEN cells (i+j even)" if parity == 0 else "ODD cells (i+j odd)"
    print(f"\n{parity_name}:")
    print("-"*70)

    rule = rule_by_parity[parity]
    deterministic_rule = {}

    for key in sorted(rule.keys()):
        cell_state, neighbors = key
        outcomes = rule[key]
        n_total = len(outcomes)
        n_alive = sum(outcomes)

        state_str = "ALIVE" if cell_state == 1 else "DEAD"

        # Determine the rule
        if n_alive == 0:
            result = "DEAD"
            deterministic_rule[key] = 0
        elif n_alive == n_total:
            result = "ALIVE"
            deterministic_rule[key] = 1
        else:
            prob = n_alive / n_total
            # This shouldn't happen if we identified the rule correctly
            result = f"MIXED ({prob:.1%})"

        print(f"  {state_str:5s} + {neighbors} neighbors -> {result:12s} (n={n_total})")

# Now express as simple rule
print("\n" + "="*70)
print("Compact Rule Expression:")
print("="*70)

for parity in [0, 1]:
    parity_name = "EVEN" if parity == 0 else "ODD"
    print(f"\n{parity_name} cells:")

    rule = rule_by_parity[parity]

    # For alive cells
    alive_survive = [n for (state, n), outcomes in rule.items()
                     if state == 1 and all(o == 1 for o in outcomes)]
    alive_die = [n for (state, n), outcomes in rule.items()
                 if state == 1 and all(o == 0 for o in outcomes)]

    # For dead cells
    dead_birth = [n for (state, n), outcomes in rule.items()
                  if state == 0 and all(o == 1 for o in outcomes)]
    dead_stay = [n for (state, n), outcomes in rule.items()
                 if state == 0 and all(o == 0 for o in outcomes)]

    if alive_survive:
        print(f"  Alive cell survives with {sorted(alive_survive)} neighbors")
    if alive_die:
        print(f"  Alive cell dies with {sorted(alive_die)} neighbors")
    if dead_birth:
        print(f"  Dead cell births with {sorted(dead_birth)} neighbors")
    if dead_stay:
        print(f"  Dead cell stays dead with {sorted(dead_stay)} neighbors")
