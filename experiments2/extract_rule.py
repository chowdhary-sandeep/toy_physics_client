"""Extract the update rule by analyzing cell neighborhoods."""
import requests
from collections import defaultdict

BASE = "http://localhost:9001"

def count_neighbors_toroidal(grid, i, j):
    """Count live neighbors with toroidal boundaries."""
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

# Collect transitions
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

# Store rule observations: (current_state, num_neighbors) -> [next_states]
rule_observations = defaultdict(list)

print("Collecting rule observations...")

for step in range(20):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    # For each cell, record (state, neighbors) -> next_state
    for i in range(9):
        for j in range(9):
            cell_state = actual_state[i][j]
            neighbors = count_neighbors_toroidal(actual_state, i, j)
            next_state = actual_next[i][j]

            key = (cell_state, neighbors)
            rule_observations[key].append(next_state)

    actual_state = actual_next

print("\nExtracted Rule:")
print("="*60)

for key in sorted(rule_observations.keys()):
    cell_state, neighbors = key
    outcomes = rule_observations[key]
    n_total = len(outcomes)
    n_alive = sum(outcomes)
    n_dead = n_total - n_alive

    state_str = "ALIVE" if cell_state == 1 else "DEAD"

    if n_dead == 0:
        result = "-> ALIVE (always)"
    elif n_alive == 0:
        result = "-> DEAD (always)"
    else:
        prob = n_alive / n_total
        result = f"-> ALIVE {prob:.1%} of time (stochastic?)"

    print(f"Cell {state_str:5s} with {neighbors} neighbors {result:30s} (n={n_total})")

print("\n" + "="*60)
print("Checking if rule is deterministic...")

deterministic = True
for key, outcomes in rule_observations.items():
    if len(set(outcomes)) > 1:
        deterministic = False
        cell_state, neighbors = key
        state_str = "ALIVE" if cell_state == 1 else "DEAD"
        n_alive = sum(outcomes)
        prob = n_alive / len(outcomes)
        print(f"  {state_str} with {neighbors} neighbors: varies ({prob:.1%} alive, n={len(outcomes)})")

if deterministic:
    print("  System appears DETERMINISTIC")
else:
    print("  System appears STOCHASTIC or has additional dependencies")
