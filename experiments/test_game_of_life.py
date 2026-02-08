"""Test if the system follows Conway's Game of Life rules."""
import requests
import numpy as np

BASE = "http://localhost:9000"

def count_neighbors(grid, i, j):
    """Count live neighbors (with wrapping/toroidal boundary)."""
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

def apply_game_of_life(grid):
    """Apply Game of Life rules."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors(grid, i, j)
            if grid[i][j] == 1:
                # Live cell
                if neighbors in [2, 3]:
                    new_grid[i][j] = 1
                else:
                    new_grid[i][j] = 0
            else:
                # Dead cell
                if neighbors == 3:
                    new_grid[i][j] = 1
                else:
                    new_grid[i][j] = 0

    return new_grid

# Test with several seeds
seeds = [42, 123, 456]
perfect_match = True

for seed in seeds:
    # Get initial state from API
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    data = resp.json()
    ep_id = data["episode_id"]
    actual_state = data["state"]

    # Test 5 steps
    for step in range(5):
        # Predict next state with Game of Life
        predicted = apply_game_of_life(actual_state)

        # Get actual next state from API
        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        data = resp.json()
        actual_next = data["state"]

        # Compare
        match = (predicted == actual_next)
        if not match:
            print(f"Seed {seed}, step {step}: MISMATCH")
            print("Predicted:")
            for row in predicted:
                print("".join(str(x) for x in row))
            print("Actual:")
            for row in actual_next:
                print("".join(str(x) for x in row))
            perfect_match = False
            break
        else:
            print(f"Seed {seed}, step {step}: MATCH")

        actual_state = actual_next

    if not perfect_match:
        break

if perfect_match:
    print("\n" + "="*60)
    print("CONCLUSION: System perfectly matches Conway's Game of Life!")
    print("="*60)
else:
    print("\n" + "="*60)
    print("CONCLUSION: System does NOT match Game of Life")
    print("="*60)
