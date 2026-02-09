"""Analyze the specific neighborhood patterns of anomalous cells."""
import requests

BASE = "http://localhost:9000"

def get_neighborhood_pattern(grid, i, j):
    """Get the 3x3 neighborhood pattern."""
    n, m = len(grid), len(grid[0])
    pattern = []
    for di in [-1, 0, 1]:
        row = []
        for dj in [-1, 0, 1]:
            ni = (i + di) % n
            nj = (j + dj) % m
            row.append(grid[ni][nj])
        pattern.append(tuple(row))
    return tuple(pattern)

def apply_gol_toroidal(grid):
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

# Run and collect anomaly neighborhoods
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

print("Analyzing neighborhood patterns of anomalous cells\n")

anomaly_count = 0

for step in range(50):
    predicted = apply_gol_toroidal(actual_state)

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    for i in range(9):
        for j in range(9):
            if predicted[i][j] != actual_next[i][j]:
                pattern = get_neighborhood_pattern(actual_state, i, j)
                center = actual_state[i][j]

                anomaly_count += 1
                print(f"Anomaly #{anomaly_count} at step {step}, pos [{i},{j}]:")
                print(f"  Center cell: {center}")
                print(f"  Neighborhood:")
                for row_idx, row in enumerate(pattern):
                    row_str = "    " + "".join(str(x) for x in row)
                    if row_idx == 1:
                        row_str += " <-- center row"
                    print(row_str)
                print(f"  GoL predicts: {predicted[i][j]}, Actual: {actual_next[i][j]}")
                print()

    actual_state = actual_next

print(f"\nTotal anomalies found: {anomaly_count}")
