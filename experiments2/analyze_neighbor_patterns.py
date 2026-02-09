"""Analyze if rule depends on specific neighbor configurations."""
import requests
from collections import defaultdict

BASE = "http://localhost:9001"

def get_neighborhood_code(grid, i, j):
    """Get a code representing the 3x3 neighborhood pattern."""
    n, m = len(grid), len(grid[0])
    code = 0
    bit = 0
    # Encode 8 neighbors as a binary number (skip center)
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            if grid[ni][nj] == 1:
                code |= (1 << bit)
            bit += 1
    return code

# Collect transitions with full neighborhood info
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
ep_id = resp.json()["episode_id"]
actual_state = resp.json()["state"]

# Rule with full pattern: (cell_state, parity, neighborhood_code) -> [next_states]
full_rule = defaultdict(list)

print("Collecting transitions with full neighborhood patterns...")

for step in range(30):
    resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
    actual_next = resp.json()["state"]

    for i in range(9):
        for j in range(9):
            cell_state = actual_state[i][j]
            parity = (i + j) % 2
            neighborhood = get_neighborhood_code(actual_state, i, j)
            next_state = actual_next[i][j]

            key = (cell_state, parity, neighborhood)
            full_rule[key].append(next_state)

    actual_state = actual_next

print(f"\nFound {len(full_rule)} unique (cell_state, parity, neighborhood) combinations")

# Check if this makes it deterministic
deterministic = True
stochastic_cases = []

for key, outcomes in full_rule.items():
    if len(set(outcomes)) > 1:
        deterministic = False
        stochastic_cases.append((key, outcomes))

if deterministic:
    print("SUCCESS! Rule is fully deterministic with (cell_state, parity, neighborhood)")
    print("\nThis means the rule is a 2-state cellular automaton with:")
    print("  - Separate rules for even and odd cells (based on (i+j)%2)")
    print("  - Depends on full 8-neighbor configuration")
else:
    print(f"Still {len(stochastic_cases)} non-deterministic cases:")
    for key, outcomes in stochastic_cases[:10]:
        cell_state, parity, neighborhood = key
        prob = sum(outcomes) / len(outcomes)
        print(f"  State={cell_state}, Parity={parity}, Pattern={neighborhood:08b}: {prob:.0%} alive (n={len(outcomes)})")

# Look for simpler pattern
print("\n" + "="*70)
print("Checking alternative hypothesis: specific neighbor pattern rules...")

# Maybe it's based on specific simple patterns (like "neighbors form a line")
# Or maybe it's based on row/column position, not just parity
