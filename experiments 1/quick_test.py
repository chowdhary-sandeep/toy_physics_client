"""Quick test to verify API and observe a few transitions."""
import requests
import json

BASE = "http://localhost:9000"

# Create one episode
resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": 42, "init_state": None})
data = resp.json()
ep_id = data["episode_id"]

print("Initial state (t=0):")
for row in data["state"]:
    print("".join(str(x) for x in row))

# Step once
resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
data = resp.json()

print("\nNext state (t=1):")
for row in data["state"]:
    print("".join(str(x) for x in row))

# Step again
resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
data = resp.json()

print("\nNext state (t=2):")
for row in data["state"]:
    print("".join(str(x) for x in row))
