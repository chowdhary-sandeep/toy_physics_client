"""Test if anomalies are consistent across runs."""
import requests

BASE = "http://localhost:9000"

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

def find_anomalies(seed, n_steps):
    """Find all anomalies for a given seed."""
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    ep_id = resp.json()["episode_id"]
    actual_state = resp.json()["state"]

    anomaly_steps = []

    for step in range(n_steps):
        predicted = apply_gol_toroidal(actual_state)

        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        actual_next = resp.json()["state"]

        if predicted != actual_next:
            num_diffs = sum(1 for i in range(9) for j in range(9)
                          if predicted[i][j] != actual_next[i][j])
            anomaly_steps.append((step, num_diffs))

        actual_state = actual_next

    return anomaly_steps

# Run same seed multiple times
seed = 42
n_runs = 3

print(f"Testing consistency: running seed {seed} {n_runs} times\n")

all_anomalies = []
for run in range(n_runs):
    anomalies = find_anomalies(seed, 50)
    all_anomalies.append(anomalies)
    print(f"Run {run+1}: Found {len(anomalies)} anomalies at steps: {[a[0] for a in anomalies]}")

# Check if anomalies are consistent
if all(all_anomalies[i] == all_anomalies[0] for i in range(n_runs)):
    print("\nCONCLUSION: Anomalies are CONSISTENT - always occur at same steps")
else:
    print("\nCONCLUSION: Anomalies are INCONSISTENT - vary between runs")

# Also test with extended run to see anomaly rate
print("\n" + "="*70)
print("Testing longer run to estimate anomaly rate")

anomalies_100 = find_anomalies(42, 100)
total_cells_checked = 100 * 9 * 9
total_anomalies = sum(a[1] for a in anomalies_100)

print(f"In 100 steps: {len(anomalies_100)} steps had anomalies")
print(f"Total anomalous cells: {total_anomalies} out of {total_cells_checked}")
print(f"Anomaly rate: {total_anomalies / total_cells_checked * 100:.2f}%")
