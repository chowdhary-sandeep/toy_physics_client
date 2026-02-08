"""Analyze cases where cells with 3 neighbors behave differently from GoL."""
import requests

BASE = "http://localhost:9000"

def count_neighbors_toroidal(grid, i, j):
    n, m = len(grid), len(grid[0])
    count = 0
    neighbors_list = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            count += grid[ni][nj]
            neighbors_list.append((ni, nj, grid[ni][nj]))
    return count, neighbors_list

def apply_gol_toroidal(grid):
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            neighbors, _ = count_neighbors_toroidal(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0
    return new_grid

# Run many steps and collect anomalies
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

anomalies = []

for step in range(50):
    predicted = apply_gol_toroidal(actual_state)

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    # Find differences
    for i in range(9):
        for j in range(9):
            if predicted[i][j] != actual_next[i][j]:
                neighbors, _ = count_neighbors_toroidal(actual_state, i, j)
                anomalies.append({
                    'step': step,
                    'pos': (i, j),
                    'was_alive': actual_state[i][j] == 1,
                    'neighbors': neighbors,
                    'predicted': predicted[i][j],
                    'actual': actual_next[i][j]
                })

    actual_state = actual_next

print(f"Found {len(anomalies)} anomalies in 50 steps\n")

# Analyze patterns
print("Anomaly patterns:")
from collections import Counter

# Group by (was_alive, neighbors)
patterns = Counter()
for a in anomalies:
    key = ('alive' if a['was_alive'] else 'dead', a['neighbors'])
    patterns[key] += 1

for key, count in sorted(patterns.items()):
    state, neighbors = key
    print(f"  {state} cell with {neighbors} neighbors: {count} anomalies")

# Show first few anomalies
print("\nFirst 10 anomalies in detail:")
for a in anomalies[:10]:
    state = 'alive' if a['was_alive'] else 'dead'
    print(f"  Step {a['step']}, pos {a['pos']}: {state}, {a['neighbors']} neighbors, "
          f"GoL predicts {a['predicted']}, actual {a['actual']}")
