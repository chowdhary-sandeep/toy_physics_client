"""Test if the system is deterministic."""
import requests

BASE = "http://localhost:9000"

def run_episode(seed, n_steps):
    """Run an episode and return all states."""
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    data = resp.json()
    ep_id = data["episode_id"]

    states = [data["state"]]
    for _ in range(n_steps):
        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        data = resp.json()
        states.append(data["state"])

    return states

# Run same seed multiple times
seed = 42
n_runs = 3
n_steps = 10

print(f"Testing determinism: running seed {seed} {n_runs} times...\n")

all_runs = []
for run in range(n_runs):
    states = run_episode(seed, n_steps)
    all_runs.append(states)
    print(f"Run {run+1} completed")

# Compare all runs
print("\nComparing runs...")
all_match = True
for step in range(n_steps + 1):
    for run in range(1, n_runs):
        if all_runs[run][step] != all_runs[0][step]:
            print(f"Step {step}: MISMATCH between run 0 and run {run}")
            all_match = False

if all_match:
    print("\nCONCLUSION: System is DETERMINISTIC - same seed produces same sequence")
else:
    print("\nCONCLUSION: System is STOCHASTIC - same seed produces different sequences")
