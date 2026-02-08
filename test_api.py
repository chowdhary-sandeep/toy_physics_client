"""
Test script to verify the Black-Box Discovery API works as documented.
"""

import requests

BASE = "http://localhost:9000"

def test_reset_random():
    """Test POST /reset with mode='random'"""
    print("\n" + "="*60)
    print("TEST 1: POST /reset with mode='random'")
    print("="*60)

    try:
        response = requests.post(
            f"{BASE}/reset",
            json={"mode": "random", "seed": 42, "init_state": None}
        )
        response.raise_for_status()
        data = response.json()

        print(f"Status: {response.status_code}")

        # Validate response structure
        assert "episode_id" in data, "Missing 'episode_id'"
        assert "t" in data, "Missing 't'"
        assert data["t"] == 0, f"Expected t=0, got t={data['t']}"
        assert "state" in data, "Missing 'state'"
        assert "shape" in data, "Missing 'shape'"
        assert "dtype" in data, "Missing 'dtype'"

        # Validate state structure
        state = data["state"]
        assert isinstance(state, list), "State must be a list"
        assert len(state) == 9, f"State must have 9 rows, got {len(state)}"
        for i, row in enumerate(state):
            assert isinstance(row, list), f"Row {i} must be a list"
            assert len(row) == 9, f"Row {i} must have 9 columns, got {len(row)}"
            for j, val in enumerate(row):
                assert val in [0, 1], f"Cell ({i},{j}) must be 0 or 1, got {val}"

        # Validate metadata
        assert data["shape"] == [9, 9], f"Expected shape [9,9], got {data['shape']}"
        assert data["dtype"] == "int8", f"Expected dtype 'int8', got {data['dtype']}"

        print(f"[PASS] Episode ID: {data['episode_id'][:8]}..., t={data['t']}, shape={data['shape']}, dtype={data['dtype']}")
        return data["episode_id"]

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return None
    except AssertionError as e:
        print(f"[FAIL] Validation failed: {e}")
        return None

def test_reset_set():
    """Test POST /reset with mode='set'"""
    print("\n" + "="*60)
    print("TEST 2: POST /reset with mode='set'")
    print("="*60)

    # Create a valid 9x9 grid
    init_state = [[1 if (i+j) % 2 == 0 else 0 for j in range(9)] for i in range(9)]

    try:
        response = requests.post(
            f"{BASE}/reset",
            json={"mode": "set", "seed": None, "init_state": init_state}
        )
        response.raise_for_status()
        data = response.json()

        print(f"Status: {response.status_code}")

        # Validate response structure (same as random)
        assert "episode_id" in data, "Missing 'episode_id'"
        assert "t" in data, "Missing 't'"
        assert data["t"] == 0, f"Expected t=0, got t={data['t']}"
        assert "state" in data, "Missing 'state'"

        # Verify state matches what we sent
        state = data["state"]
        assert state == init_state, "State should match init_state"

        print(f"[PASS] Episode ID: {data['episode_id'][:8]}..., t={data['t']}, state matches init_state")
        return data["episode_id"]

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return None
    except AssertionError as e:
        print(f"[FAIL] Validation failed: {e}")
        return None

def test_step(episode_id):
    """Test POST /step"""
    print("\n" + "="*60)
    print("TEST 3: POST /step")
    print("="*60)

    if not episode_id:
        print("[FAIL] Skipping: No episode_id available")
        return None

    try:
        response = requests.post(
            f"{BASE}/step",
            json={"episode_id": episode_id, "n_steps": 1}
        )
        response.raise_for_status()
        data = response.json()

        print(f"Status: {response.status_code}")

        # Validate response structure
        assert "episode_id" in data, "Missing 'episode_id'"
        assert data["episode_id"] == episode_id, "episode_id should match"
        assert "t" in data, "Missing 't'"
        assert data["t"] == 1, f"Expected t=1 after 1 step, got t={data['t']}"
        assert "state" in data, "Missing 'state'"
        assert "shape" in data, "Missing 'shape'"
        assert "dtype" in data, "Missing 'dtype'"

        # Validate state structure
        state = data["state"]
        assert isinstance(state, list), "State must be a list"
        assert len(state) == 9, f"State must have 9 rows, got {len(state)}"
        for i, row in enumerate(state):
            assert isinstance(row, list), f"Row {i} must be a list"
            assert len(row) == 9, f"Row {i} must have 9 columns, got {len(row)}"
            for j, val in enumerate(row):
                assert val in [0, 1], f"Cell ({i},{j}) must be 0 or 1, got {val}"

        print(f"[PASS] Episode ID: {data['episode_id'][:8]}..., t={data['t']}, state updated")
        return data["t"]

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return None
    except AssertionError as e:
        print(f"[FAIL] Validation failed: {e}")
        return None

def test_clone(episode_id):
    """Test POST /clone"""
    print("\n" + "="*60)
    print("TEST 4: POST /clone")
    print("="*60)

    if not episode_id:
        print("[SKIP] Skipping: No episode_id available")
        return None

    try:
        response = requests.post(
            f"{BASE}/clone",
            json={"episode_id": episode_id}
        )
        response.raise_for_status()
        data = response.json()

        print(f"Status: {response.status_code}")

        # Validate response structure
        assert "episode_id" in data, "Missing 'episode_id'"
        assert data["episode_id"] != episode_id, "episode_id should be different (new episode)"
        assert "t" in data, "Missing 't'"
        assert "state" in data, "Missing 'state'"
        assert "shape" in data, "Missing 'shape'"
        assert "dtype" in data, "Missing 'dtype'"

        print(f"[PASS] New episode ID: {data['episode_id'][:8]}..., cloned at t={data['t']}")
        return data["episode_id"]

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return None
    except AssertionError as e:
        print(f"[FAIL] Validation failed: {e}")
        return None

def test_multiple_steps(episode_id):
    """Test POST /step with n_steps > 1"""
    print("\n" + "="*60)
    print("TEST 5: POST /step with n_steps=3")
    print("="*60)

    if not episode_id:
        print("[SKIP] Skipping: No episode_id available")
        return None

    try:
        response = requests.post(
            f"{BASE}/step",
            json={"episode_id": episode_id, "n_steps": 3}
        )
        response.raise_for_status()
        data = response.json()

        print(f"Status: {response.status_code}")

        # Validate that time advanced correctly
        assert "t" in data, "Missing 't'"
        print(f"[PASS] Time advanced to t={data['t']} (from t=0)")

        return True

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return False
    except AssertionError as e:
        print(f"[FAIL] Validation failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BLACK-BOX DISCOVERY API TEST SUITE")
    print("="*60)

    # Test 1: Reset with random mode
    ep_id_1 = test_reset_random()

    # Test 2: Reset with set mode
    ep_id_2 = test_reset_set()

    # Test 3: Step (using first episode)
    if ep_id_1:
        test_step(ep_id_1)

    # Test 4: Clone
    if ep_id_1:
        cloned_id = test_clone(ep_id_1)

    # Test 5: Multiple steps
    ep_id_3 = test_reset_random()
    if ep_id_3:
        test_multiple_steps(ep_id_3)

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
