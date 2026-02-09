"""Find the common pattern in anomalous neighborhoods."""

# The 7 anomalous neighborhoods
anomalies = [
    # Anomaly #1 - center=0, 3 neighbors
    ((0,1,0), (1,0,0), (0,0,1)),
    # Anomaly #2 - center=1, 3 neighbors
    ((0,0,0), (1,1,0), (1,0,1)),
    # Anomaly #3 - center=0, 3 neighbors
    ((0,1,0), (0,0,0), (0,1,1)),
    # Anomaly #4 - center=1, 3 neighbors
    ((0,0,0), (0,1,1), (1,1,0)),
    # Anomaly #5 - center=0, 3 neighbors
    ((1,1,0), (1,0,0), (0,0,0)),
    # Anomaly #6 - center=1, 2 neighbors
    ((1,1,0), (0,1,0), (0,0,0)),
    # Anomaly #7 - center=0, 3 neighbors
    ((1,0,1), (1,0,0), (0,0,0)),
]

print("Analyzing anomalous neighborhood patterns:\n")

for idx, pattern in enumerate(anomalies, 1):
    print(f"Anomaly #{idx}:")
    for row_idx, row in enumerate(pattern):
        row_str = "  " + "".join(str(x) for x in row)
        if row_idx == 1:
            row_str += " <-- center"
        print(row_str)

    # Count neighbors
    neighbors = sum(sum(row) for row in pattern) - pattern[1][1]
    print(f"  Neighbors: {neighbors}")

    # Check various properties
    # 1. Are all neighbors in one half (top/bottom, left/right)?
    top_half = pattern[0][0] + pattern[0][1] + pattern[0][2]
    bottom_half = pattern[2][0] + pattern[2][1] + pattern[2][2]
    left_half = pattern[0][0] + pattern[1][0] + pattern[2][0]
    right_half = pattern[0][2] + pattern[1][2] + pattern[2][2]

    print(f"  Top:{top_half}, Bottom:{bottom_half}, Left:{left_half}, Right:{right_half}")

    # 2. Are neighbors contiguous (forming a connected component)?
    # 3. Do they form a diagonal?
    diagonal1 = pattern[0][0] + pattern[1][1] + pattern[2][2]  # top-left to bottom-right
    diagonal2 = pattern[0][2] + pattern[1][1] + pattern[2][0]  # top-right to bottom-left

    # Check if neighbors form an L-shape or line
    # For now, just check if all 3 neighbors are connected

    print()

# Let me check a specific hypothesis: maybe the rule is different when
# the 3 neighbors are NOT forming a horizontal or vertical line?

print("\nChecking if neighbors form a line:")
for idx, pattern in enumerate(anomalies, 1):
    # Get positions of live neighbors
    neighbors_pos = []
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue
            if pattern[i][j] == 1:
                neighbors_pos.append((i, j))

    print(f"Anomaly #{idx}: neighbor positions: {neighbors_pos}")

    # Check if they form a horizontal line
    if len(set(pos[0] for pos in neighbors_pos)) == 1:
        print("  Forms HORIZONTAL line")
    # Check if they form a vertical line
    elif len(set(pos[1] for pos in neighbors_pos)) == 1:
        print("  Forms VERTICAL line")
    # Check if diagonal
    elif all(abs(neighbors_pos[i][0] - neighbors_pos[j][0]) == abs(neighbors_pos[i][1] - neighbors_pos[j][1])
             for i in range(len(neighbors_pos)) for j in range(i+1, len(neighbors_pos))):
        print("  Forms DIAGONAL line")
    else:
        print("  Does NOT form a straight line (L-shape or scattered)")
