"""Analyze specific cells where the system differs from Game of Life."""
import requests

BASE = "http://localhost:9000"

def count_neighbors_toroidal(grid, i, j):
    """Count neighbors with toroidal boundary."""
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
    """Apply standard Game of Life."""
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

# Run to step where difference occurs
seed = 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]

states = [data["state"]]

# Get to step 4
for _ in range(4):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    data = resp.json()
    states.append(data["state"])

# Now analyze the transition from state[3] to state[4]
state_t3 = states[3]
state_t4_actual = states[4]
state_t4_predicted = apply_gol(state_t3)

print("State at t=3:")
for i, row in enumerate(state_t3):
    print(f"{i}: " + "".join(str(x) for x in row))

print("\nPredicted (GoL) at t=4:")
for i, row in enumerate(state_t4_predicted):
    print(f"{i}: " + "".join(str(x) for x in row))

print("\nActual at t=4:")
for i, row in enumerate(state_t4_actual):
    print(f"{i}: " + "".join(str(x) for x in row))

print("\nDifferences:")
for i in range(9):
    for j in range(9):
        if state_t4_predicted[i][j] != state_t4_actual[i][j]:
            neighbors = count_neighbors_toroidal(state_t3, i, j)
            cell_t3 = state_t3[i][j]
            pred = state_t4_predicted[i][j]
            actual = state_t4_actual[i][j]
            print(f"  Cell [{i},{j}]: was {cell_t3}, had {neighbors} neighbors")
            print(f"    GoL predicts: {pred}, Actual: {actual}")

            # Show neighborhood at t=3
            print(f"    Neighborhood at t=3:")
            for di in [-1, 0, 1]:
                ni = (i + di) % 9
                neighborhood_row = ""
                for dj in [-1, 0, 1]:
                    nj = (j + dj) % 9
                    neighborhood_row += str(state_t3[ni][nj])
                print(f"      {neighborhood_row}")
