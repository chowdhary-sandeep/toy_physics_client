"""Quick observation of the new system's dynamics."""
import requests

BASE = "http://localhost:9001"

# Test with seed 42
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]

print("New System - Initial Observations")
print("="*60)

states = [data["state"]]

print("\nt=0 (initial):")
for row in data["state"]:
    print("".join(str(x) for x in row))

# Observe 10 steps
for step in range(1, 11):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    data = resp.json()
    states.append(data["state"])

    print(f"\nt={step}:")
    for row in data["state"]:
        print("".join(str(x) for x in row))

# Quick analysis
print("\n" + "="*60)
print("Quick Analysis:")

import numpy as np

densities = [np.mean(s) for s in states]
print(f"\nDensity evolution: {[f'{d:.3f}' for d in densities]}")

# Check if it looks like GoL
changes_per_step = []
for i in range(len(states)-1):
    s0 = np.array(states[i])
    s1 = np.array(states[i+1])
    changes = np.sum(s0 != s1)
    changes_per_step.append(changes)

print(f"\nCells changed per step: {changes_per_step}")
print(f"Average changes per step: {np.mean(changes_per_step):.1f}")

# Check for patterns
if all(d < 0.1 for d in densities):
    print("\nPattern: Rapid die-off (all cells dying)")
elif all(abs(densities[i] - densities[i+1]) < 0.05 for i in range(len(densities)-1)):
    print("\nPattern: Stable density (equilibrium or oscillation)")
elif densities[-1] > densities[0] * 1.5:
    print("\nPattern: Growth (density increasing)")
elif densities[-1] < densities[0] * 0.5:
    print("\nPattern: Decay (density decreasing)")
else:
    print("\nPattern: Complex dynamics")
