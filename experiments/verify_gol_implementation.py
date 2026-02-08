"""Verify our GoL implementation with known patterns."""

def count_neighbors_toroidal(grid, i, j):
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

def apply_gol_toroidal(grid):
    n, m = len(grid), len(grid[0])
    new_grid = [[0]*m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors_toroidal(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid

# Test with known pattern: Blinker (oscillator with period 2)
# Blinker horizontal -> vertical -> horizontal
print("Test 1: Blinker pattern")
grid = [[0]*5 for _ in range(5)]
grid[2][1] = 1
grid[2][2] = 1
grid[2][3] = 1

print("Initial (horizontal):")
for row in grid:
    print("".join(str(x) for x in row))

next_grid = apply_gol_toroidal(grid)
print("\nAfter 1 step (should be vertical):")
for row in next_grid:
    print("".join(str(x) for x in row))

next_next = apply_gol_toroidal(next_grid)
print("\nAfter 2 steps (should be horizontal again):")
for row in next_next:
    print("".join(str(x) for x in row))

if next_next == grid:
    print("PASS: Blinker oscillates correctly")
else:
    print("FAIL: Blinker doesn't oscillate")

# Test with block (still life)
print("\n" + "="*50)
print("Test 2: Block pattern (still life)")
grid2 = [[0]*5 for _ in range(5)]
grid2[2][2] = 1
grid2[2][3] = 1
grid2[3][2] = 1
grid2[3][3] = 1

print("Initial:")
for row in grid2:
    print("".join(str(x) for x in row))

next_grid2 = apply_gol_toroidal(grid2)
print("\nAfter 1 step (should be same):")
for row in next_grid2:
    print("".join(str(x) for x in row))

if next_grid2 == grid2:
    print("PASS: Block is stable")
else:
    print("FAIL: Block changed")
