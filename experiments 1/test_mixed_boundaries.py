"""Test if system uses fixed boundaries at edges but toroidal in middle."""
import requests

BASE = "http://localhost:9000"

def count_neighbors_fixed(grid, i, j):
    """Count neighbors with fixed (dead outside) boundaries."""
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

# Get state at t=4
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
ep_id = resp.json()["episode_id"]

for _ in range(4):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})

state_t4 = resp.json()["state"]

# Check the two problematic cells with fixed boundaries
print("Checking with FIXED boundaries:\n")

i, j = 3, 6
neighbors = count_neighbors_fixed(state_t4, i, j)
print(f"Cell [3,6]: value={state_t4[i][j]}, neighbors={neighbors}")
print(f"  (This is NOT on edge)")

i, j = 8, 7
neighbors = count_neighbors_fixed(state_t4, i, j)
print(f"Cell [8,7]: value={state_t4[i][j]}, neighbors={neighbors}")
print(f"  (This IS on edge - row 8 is last row)")

# The neighborhood would be different for edge cells with fixed boundaries
print("\nFor [8,7] with fixed boundaries:")
print("  Top row would be row 7 (exists)")
print("  Bottom row would be row 9 (doesn't exist, treated as all 0s)")
print("  So bottom-left and bottom-right neighbors don't count")

# Manual calculation for [8,7] with fixed boundaries:
# Row 7: 000010000, columns 6,7,8 = 000
# Row 8: 000010110, columns 6,7,8 = 110
# Row 9 doesn't exist, so = 000
# Neighbors = 0+0+0 + 1+0 + 0+0+0 = 1 (only the left neighbor)

print("\nActual manual count for [8,7] with fixed boundaries:")
print("  Row 7, cols 6-8: 0,0,0")
print("  Row 8, cols 6,8: 1,0 (skip center col 7)")
print("  Row 9: doesn't exist")
print("  Total: 1 neighbor")
print("  GoL rule: alive with 1 neighbor → dies")
print("  This MATCHES the actual behavior!")
