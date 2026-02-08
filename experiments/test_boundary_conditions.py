"""Test different boundary condition strategies."""
import requests
import numpy as np

BASE = "http://localhost:9000"

def count_neighbors_toroidal(grid, i, j):
    """Count neighbors with toroidal (wrapping) boundary."""
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

def count_neighbors_fixed(grid, i, j):
    """Count neighbors with fixed (dead cells outside) boundary."""
    n, m = len(grid), len(grid[0])
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = i + di
            nj = j + dj
            if 0 <= ni < n and 0 <= nj < m:
                count += grid[ni][nj]
    return count

def apply_gol(grid, boundary='toroidal'):
    """Apply Game of Life with specified boundary conditions."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    count_func = count_neighbors_toroidal if boundary == 'toroidal' else count_neighbors_fixed

    for i in range(n):
        for j in range(m):
            neighbors = count_func(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid

# Test both boundary conditions
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]
actual_state = data["state"]

print("Testing boundary conditions with seed 42...\n")

for step in range(10):
    # Predict with both methods
    pred_toroidal = apply_gol(actual_state, 'toroidal')
    pred_fixed = apply_gol(actual_state, 'fixed')

    # Get actual
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    data = resp.json()
    actual_next = data["state"]

    # Compare
    match_toroidal = (pred_toroidal == actual_next)
    match_fixed = (pred_fixed == actual_next)

    if match_toroidal:
        print(f"Step {step}: TOROIDAL boundary matches")
    elif match_fixed:
        print(f"Step {step}: FIXED boundary matches")
    else:
        # Count differences
        diff_toroidal = sum(1 for i in range(9) for j in range(9) if pred_toroidal[i][j] != actual_next[i][j])
        diff_fixed = sum(1 for i in range(9) for j in range(9) if pred_fixed[i][j] != actual_next[i][j])
        print(f"Step {step}: NO MATCH (toroidal diff={diff_toroidal}, fixed diff={diff_fixed})")

        if diff_toroidal < 5 or diff_fixed < 5:
            print("  Showing differences...")
            print("  Actual:")
            for row in actual_next:
                print("    " + "".join(str(x) for x in row))
            print("  Toroidal predicted:")
            for row in pred_toroidal:
                print("    " + "".join(str(x) for x in row))
            print("  Fixed predicted:")
            for row in pred_fixed:
                print("    " + "".join(str(x) for x in row))

    actual_state = actual_next
