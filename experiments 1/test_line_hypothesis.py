"""Test hypothesis: system modifies GoL when 3 neighbors don't form a line."""
import requests

BASE = "http://localhost:9000"

def get_neighbor_positions(grid, i, j):
    """Get positions of live neighbors."""
    n, m = len(grid), len(grid[0])
    positions = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = (i + di) % n
            nj = (j + dj) % m
            if grid[ni][nj] == 1:
                # Store relative position
                positions.append((di+1, dj+1))  # Convert to 0-2 range
    return positions

def neighbors_form_line(positions):
    """Check if neighbor positions form a straight line."""
    if len(positions) < 2:
        return True  # 0 or 1 neighbor always forms a "line"
    if len(positions) == 2:
        return True  # 2 neighbors always form a line

    # For 3+ neighbors, check if they're collinear
    # Horizontal line: all same row
    if len(set(pos[0] for pos in positions)) == 1:
        return True
    # Vertical line: all same column
    if len(set(pos[1] for pos in positions)) == 1:
        return True
    # Diagonal line: check if slope is consistent
    if len(positions) == 3:
        p0, p1, p2 = sorted(positions)
        # Check if they form a diagonal
        # For a diagonal in 3x3 grid with 3 points, they should be (0,0), (1,1), (2,2) or similar
        if (p1[0] - p0[0] == p2[0] - p1[0] and
            p1[1] - p0[1] == p2[1] - p1[1]):
            return True

    return False

def apply_modified_gol(grid):
    """Apply GoL with modification: ignore 3-neighbor rule when neighbors don't form a line."""
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbor_positions = get_neighbor_positions(grid, i, j)
            num_neighbors = len(neighbor_positions)
            forms_line = neighbors_form_line(neighbor_positions)

            cell = grid[i][j]

            if cell == 1:
                # Live cell
                if num_neighbors in [2, 3]:
                    # Standard GoL: survive with 2 or 3 neighbors
                    # But if 3 neighbors don't form a line, die
                    if num_neighbors == 3 and not forms_line:
                        new_grid[i][j] = 0
                    else:
                        new_grid[i][j] = 1
                else:
                    new_grid[i][j] = 0
            else:
                # Dead cell
                if num_neighbors == 3:
                    # Standard GoL: born with 3 neighbors
                    # But if neighbors don't form a line, stay dead
                    if forms_line:
                        new_grid[i][j] = 1
                    else:
                        new_grid[i][j] = 0
                else:
                    new_grid[i][j] = 0

    return new_grid

# Test this hypothesis
seeds = [42, 123, 456]
all_match = True

for seed in seeds:
    resp = requests.post(f"{BASE}/reset", json={"mode": "random", "seed": seed, "init_state": None})
    data = resp.json()
    ep_id = data["episode_id"]
    actual_state = data["state"]

    print(f"Testing seed {seed}...")

    for step in range(50):
        predicted = apply_modified_gol(actual_state)

        resp = requests.post(f"{BASE}/step", json={"episode_id": ep_id, "n_steps": 1})
        data = resp.json()
        actual_next = data["state"]

        if predicted != actual_next:
            mismatches = sum(1 for i in range(9) for j in range(9)
                           if predicted[i][j] != actual_next[i][j])
            print(f"  Step {step}: MISMATCH ({mismatches} cells)")
            all_match = False
            break

        actual_state = actual_next

    if all_match:
        print(f"  All 50 steps match!")
    else:
        break

print("\n" + "="*70)
if all_match:
    print("SUCCESS! System follows modified GoL:")
    print("  - Standard GoL rules apply EXCEPT")
    print("  - When 3 neighbors don't form a straight line:")
    print("    * Dead cells stay dead (no birth)")
    print("    * Alive cells die")
    print("="*70)
else:
    print("Hypothesis does not fully explain the system")
    print("="*70)
