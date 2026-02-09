"""
Experiment 2: Controlled Patterns
Test specific initial patterns to understand update rules.
"""
import requests
import json
import numpy as np

BASE = "http://localhost:9000"

def create_pattern(pattern_type):
    """Create specific 9x9 patterns."""
    grid = [[0]*9 for _ in range(9)]

    if pattern_type == "single_cell":
        grid[4][4] = 1
    elif pattern_type == "horizontal_line":
        for j in range(9):
            grid[4][j] = 1
    elif pattern_type == "vertical_line":
        for i in range(9):
            grid[i][4] = 1
    elif pattern_type == "checkerboard":
        for i in range(9):
            for j in range(9):
                grid[i][j] = (i + j) % 2
    elif pattern_type == "block_2x2":
        grid[4][4] = 1
        grid[4][5] = 1
        grid[5][4] = 1
        grid[5][5] = 1
    elif pattern_type == "glider_like":
        # Classic glider pattern from Game of Life
        grid[3][4] = 1
        grid[4][5] = 1
        grid[5][3] = 1
        grid[5][4] = 1
        grid[5][5] = 1
    elif pattern_type == "blinker_like":
        # Blinker from Game of Life
        grid[4][3] = 1
        grid[4][4] = 1
        grid[4][5] = 1

    return grid

def run_pattern_episode(pattern_type, n_steps=10):
    """Run episode with controlled initial pattern."""
    init_state = create_pattern(pattern_type)

    # Reset
    resp = requests.post(f"{BASE}/reset", json={
        "mode": "set",
        "seed": None,
        "init_state": init_state
    })
    data = resp.json()
    episode_id = data["episode_id"]

    states = [data["state"]]

    # Step forward
    for i in range(n_steps):
        resp = requests.post(f"{BASE}/step", json={
            "episode_id": episode_id,
            "n_steps": 1
        })
        data = resp.json()
        states.append(data["state"])

    return states

if __name__ == "__main__":
    patterns = [
        "single_cell",
        "horizontal_line",
        "vertical_line",
        "checkerboard",
        "block_2x2",
        "glider_like",
        "blinker_like"
    ]

    results = {}

    print("Running controlled pattern experiments...")

    for pattern in patterns:
        print(f"  Testing {pattern}...")
        states = run_pattern_episode(pattern, n_steps=10)
        results[pattern] = states

    # Save results
    with open("e:/toy-physics discovery/experiments/exp2_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to exp2_results.json")
