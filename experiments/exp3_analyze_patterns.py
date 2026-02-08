"""
Experiment 3: Pattern Analysis
Analyze the collected data to identify update rules.
"""
import json
import numpy as np

def analyze_transition(state_t, state_t1):
    """Analyze how a state transitions to the next."""
    # Convert to numpy arrays
    s0 = np.array(state_t)
    s1 = np.array(state_t1)

    # Count changes
    changed = np.sum(s0 != s1)
    birth = np.sum((s0 == 0) & (s1 == 1))
    death = np.sum((s0 == 1) & (s1 == 0))

    return {
        "total_changed": int(changed),
        "births": int(birth),
        "deaths": int(death),
        "density_before": float(np.mean(s0)),
        "density_after": float(np.mean(s1))
    }

def check_neighbor_rule(state_t, state_t1):
    """Check if updates follow neighbor-counting rule (like Game of Life)."""
    s0 = np.array(state_t)
    s1 = np.array(state_t1)

    # For each cell, count neighbors
    patterns = []
    for i in range(1, 8):  # Avoid edges for now
        for j in range(1, 8):
            # Count live neighbors
            neighbors = (
                s0[i-1, j-1] + s0[i-1, j] + s0[i-1, j+1] +
                s0[i, j-1] + s0[i, j+1] +
                s0[i+1, j-1] + s0[i+1, j] + s0[i+1, j+1]
            )

            patterns.append({
                "alive": int(s0[i, j]),
                "neighbors": int(neighbors),
                "next_alive": int(s1[i, j])
            })

    return patterns

if __name__ == "__main__":
    print("Analyzing experimental results...\n")

    # Load exp1 results (random)
    with open("e:/toy-physics discovery/experiments/exp1_results.json", "r") as f:
        exp1 = json.load(f)

    # Load exp2 results (controlled)
    with open("e:/toy-physics discovery/experiments/exp2_results.json", "r") as f:
        exp2 = json.load(f)

    print("="*60)
    print("TRANSITION STATISTICS (Random Episodes)")
    print("="*60)

    for seed, states in exp1.items():
        print(f"\nSeed {seed}:")
        for t in range(min(3, len(states)-1)):
            stats = analyze_transition(states[t], states[t+1])
            print(f"  t={t}→{t+1}: changed={stats['total_changed']}, "
                  f"births={stats['births']}, deaths={stats['deaths']}, "
                  f"density={stats['density_before']:.3f}→{stats['density_after']:.3f}")

    print("\n" + "="*60)
    print("NEIGHBOR RULE ANALYSIS")
    print("="*60)

    # Aggregate all transitions to find patterns
    all_patterns = []

    # Use first random episode
    first_seed = list(exp1.keys())[0]
    states = exp1[first_seed]

    for t in range(len(states)-1):
        patterns = check_neighbor_rule(states[t], states[t+1])
        all_patterns.extend(patterns)

    # Group by (alive, neighbors) and see what next_alive is
    from collections import defaultdict
    rule_map = defaultdict(list)

    for p in all_patterns:
        key = (p["alive"], p["neighbors"])
        rule_map[key].append(p["next_alive"])

    print("\nRule extraction (alive, neighbors) → next_alive:")
    for key in sorted(rule_map.keys()):
        alive, neighbors = key
        outcomes = rule_map[key]
        # Check if deterministic
        if len(set(outcomes)) == 1:
            print(f"  Cell={'alive' if alive else 'dead'}, neighbors={neighbors} → "
                  f"{'ALIVE' if outcomes[0] else 'DEAD'} (n={len(outcomes)})")
        else:
            alive_count = sum(outcomes)
            prob = alive_count / len(outcomes)
            print(f"  Cell={'alive' if alive else 'dead'}, neighbors={neighbors} → "
                  f"ALIVE with prob={prob:.3f} (n={len(outcomes)})")

    # Save analysis
    analysis_results = {
        "rule_map": {str(k): v for k, v in rule_map.items()}
    }

    with open("e:/toy-physics discovery/experiments/exp3_analysis.json", "w") as f:
        json.dump(analysis_results, f, indent=2)

    print("\nAnalysis saved to exp3_analysis.json")
