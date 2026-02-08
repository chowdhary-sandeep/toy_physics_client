"""Test if system is Game of Life with FIXED boundaries."""
import requests

BASE = "http://localhost:9000"

def count_neighbors_fixed(grid, i, j):
    """Count neighbors with fixed boundaries (dead outside grid)."""
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

def apply_gol_fixed(grid):
    """Apply Game of Life with fixed boundaries."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors_fixed(grid, i, j)
            if grid[i][j] == 1:
                # Live cell: survives with 2 or 3 neighbors
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                # Dead cell: becomes alive with exactly 3 neighbors
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid

# Test with multiple seeds
seeds = [42, 123, 456]
all_match = True

for seed in seeds:
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    data = resp.json()
    ep_id = data["episode_id"]
    actual_state = data["state"]

    print(f"Testing seed {seed}...")

    for step in range(20):
        predicted = apply_gol_fixed(actual_state)

        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        data = resp.json()
        actual_next = data["state"]

        if predicted != actual_next:
            print(f"  Step {step}: MISMATCH")
            all_match = False
            break

        actual_state = actual_next

    if all_match:
        print(f"  All 20 steps match!")
    else:
        break

print("\n" + "="*70)
if all_match:
    print("CONCLUSION: System IS Conway's Game of Life with FIXED boundaries!")
    print("="*70)
else:
    print("CONCLUSION: System does NOT match GoL with fixed boundaries")
    print("="*70)
