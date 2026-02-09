"""Compare system against both toroidal and fixed GoL."""
import requests

BASE = "http://localhost:9000"

def count_neighbors(grid, i, j, boundary='toroidal'):
    """Count neighbors with specified boundary conditions."""
    n, m = len(grid), len(grid[0])
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue

            if boundary == 'toroidal':
                ni = (i + di) % n
                nj = (j + dj) % m
                count += grid[ni][nj]
            else:  # fixed
                ni = i + di
                nj = j + dj
                if 0 <= ni < n and 0 <= nj < m:
                    count += grid[ni][nj]
    return count

def apply_gol(grid, boundary='toroidal'):
    """Apply Game of Life."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors(grid, i, j, boundary)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid

# Test seed 42
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]
actual_state = data["state"]

print("Comparing system with GoL (toroidal vs fixed boundaries)\n")

for step in range(10):
    pred_toroidal = apply_gol(actual_state, 'toroidal')
    pred_fixed = apply_gol(actual_state, 'fixed')

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    data = resp.json()
    actual_next = data["state"]

    match_toroidal = (pred_toroidal == actual_next)
    match_fixed = (pred_fixed == actual_next)

    # Count mismatches
    mismatch_toroidal = sum(1 for i in range(9) for j in range(9)
                            if pred_toroidal[i][j] != actual_next[i][j])
    mismatch_fixed = sum(1 for i in range(9) for j in range(9)
                         if pred_fixed[i][j] != actual_next[i][j])

    print(f"Step {step}: Toroidal mismatches={mismatch_toroidal}, Fixed mismatches={mismatch_fixed}")

    if mismatch_toroidal > 0 and mismatch_fixed > 0:
        print(f"  Neither matches perfectly - showing first few differences")
        count = 0
        for i in range(9):
            for j in range(9):
                if pred_toroidal[i][j] != actual_next[i][j] or pred_fixed[i][j] != actual_next[i][j]:
                    n_tor = count_neighbors(actual_state, i, j, 'toroidal')
                    n_fix = count_neighbors(actual_state, i, j, 'fixed')
                    print(f"    [{i},{j}]: val={actual_state[i][j]}, n_tor={n_tor}, n_fix={n_fix}, " +
                          f"pred_tor={pred_toroidal[i][j]}, pred_fix={pred_fixed[i][j]}, actual={actual_next[i][j]}")
                    count += 1
                    if count >= 5:
                        break
            if count >= 5:
                break

    actual_state = actual_next
