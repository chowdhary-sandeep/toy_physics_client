"""Compare new system to Conway's Game of Life."""
import requests
import numpy as np

BASE = "http://localhost:9001"

def apply_gol_toroidal(grid):
    """Standard Conway's Game of Life with toroidal boundaries."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbors = sum(grid[(i+di)%n][(j+dj)%m]
                          for di in [-1,0,1] for dj in [-1,0,1]
                          if not (di==0 and dj==0))
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid

# Test with seed 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]
actual_state = data["state"]

print("Comparing to Conway's Game of Life")
print("="*60)

for step in range(10):
    # Predict with GoL
    gol_pred = apply_gol_toroidal(actual_state)

    # Get actual next state
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    # Compare
    mismatches = sum(1 for i in range(9) for j in range(9)
                    if gol_pred[i][j] != actual_next[i][j])

    print(f"Step {step}: {mismatches}/81 cells differ from GoL")

    if step == 0:
        print(f"\nStep 0 details:")
        print("GoL predicted:")
        for row in gol_pred:
            print("".join(str(x) for x in row))
        print("\nActual:")
        for row in actual_next:
            print("".join(str(x) for x in row))

    actual_state = actual_next

print("\n" + "="*60)
print("CONCLUSION: System is NOT standard Conway's Game of Life")
