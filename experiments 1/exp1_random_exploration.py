"""
Experiment 1: Random Exploration
Observe multiple random initial states and their evolution.
"""
import requests
import json
import numpy as np

BASE = "http://localhost:9000"

def run_random_episode(seed, n_steps=10):
    """Run an episode with random initial state."""
    # Reset
    resp = requests.post(f"{BASE}/reset", json={
        "mode": "random",
        "seed": seed,
        "init_state": None
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
    results = {}
    seeds = [42, 123, 456, 789, 1001]

    print("Running random exploration with seeds:", seeds)

    for seed in seeds:
        print(f"  Seed {seed}...")
        states = run_random_episode(seed, n_steps=10)
        results[seed] = states

    # Save results
    with open("e:/toy-physics discovery/experiments/exp1_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Quick analysis
    print("\nQuick Analysis:")
    for seed in seeds:
        states = results[seed]
        densities = [np.mean(s) for s in states]
        print(f"  Seed {seed}: density evolution = {[f'{d:.3f}' for d in densities]}")

    print("\nResults saved to exp1_results.json")
