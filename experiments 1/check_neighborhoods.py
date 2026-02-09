"""Check the neighborhoods of the mismatched cells in detail."""
import requests

BASE = "http://localhost:9000"

# Get state at t=4
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
ep_id = resp.json()["episode_id"]

for _ in range(4):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})

state_t4 = resp.json()["state"]

print("State at t=4:")
for i, row in enumerate(state_t4):
    print(f"{i}: " + "".join(str(x) for x in row))

def show_neighborhood(grid, i, j, label):
    """Show the 3x3 neighborhood around a cell."""
    n, m = len(grid), len(grid[0])
    print(f"\n{label} - Cell [{i},{j}] (value={grid[i][j]}):")
    print(f"  Position: row {i}, col {j}")
    print("  3x3 neighborhood (toroidal):")
    total = 0
    for di in [-1, 0, 1]:
        ni = (i + di) % n
        row_str = "    "
        for dj in [-1, 0, 1]:
            nj = (j + dj) % m
            val = grid[ni][nj]
            row_str += str(val)
            if not (di == 0 and dj == 0):
                total += val
        if di == 0:
            row_str += " <-- center row"
        print(row_str)
    print(f"  Total neighbors: {total}")

# Check cell [3,6]
show_neighborhood(state_t4, 3, 6, "Cell [3,6]")

# Check cell [8,7]
show_neighborhood(state_t4, 8, 7, "Cell [8,7]")

# Also check if these cells are near edges
print("\n" + "="*60)
print("Edge analysis:")
print("  [3,6] is in middle of grid (not near edge)")
print("  [8,7] is on bottom edge (row 8 is last row)")
