"""Find the first mismatch and analyze it."""
import requests

BASE = "http://localhost:9000"

def count_neighbors_toroidal(grid, i, j):
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

def apply_gol(grid):
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors_toroidal(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0
    return new_grid

seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]
actual_state = data["state"]

print("Searching for first mismatch...\n")

for step in range(20):
    predicted = apply_gol(actual_state)

    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    data = resp.json()
    actual_next = data["state"]

    if predicted != actual_next:
        print(f"FIRST MISMATCH at t={step} -> t={step+1}\n")

        print(f"State at t={step}:")
        for i, row in enumerate(actual_state):
            print(f"{i}: " + "".join(str(x) for x in row))

        print(f"\nPredicted (GoL) at t={step+1}:")
        for i, row in enumerate(predicted):
            print(f"{i}: " + "".join(str(x) for x in row))

        print(f"\nActual at t={step+1}:")
        for i, row in enumerate(actual_next):
            print(f"{i}: " + "".join(str(x) for x in row))

        print("\nDifferent cells:")
        for i in range(9):
            for j in range(9):
                if predicted[i][j] != actual_next[i][j]:
                    neighbors = count_neighbors_toroidal(actual_state, i, j)
                    cell_val = actual_state[i][j]
                    pred = predicted[i][j]
                    actual = actual_next[i][j]
                    print(f"  [{i},{j}]: was {'alive' if cell_val else 'dead'}, neighbors={neighbors}, GoL={pred}, Actual={actual}")

        break

    actual_state = actual_next
else:
    print("No mismatch found in first 20 steps!")
