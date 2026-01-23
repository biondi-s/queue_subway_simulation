"""
Highway Traffic Simulation - Italian Highway Rules

This simulation models a 3-lane highway where:
- Cars can only pass on the left
- Bad practice: driving in middle lane when right lane is free
- Shows how traffic jam probability increases with bad practice
"""


from typing import List
from .dynamics import HighwaySimulation


def run_simulation(num_cars: int = 20, num_trials: int = 100, 
                    bad_practice_ratios: List[float] = None) -> dict:
    """
    Run multiple simulations with different bad practice ratios

    Returns:
        Dictionary with results showing traffic jam probability vs bad practice ratio
    """
    if bad_practice_ratios is None:
        bad_practice_ratios = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    results = {}

    print("Running highway traffic simulations...")
    print(f"Number of cars: {num_cars}")
    print(f"Trials per configuration: {num_trials}")
    print("-" * 60)

    for ratio in bad_practice_ratios:
        jam_count = 0

        for trial in range(num_trials):
            sim = HighwaySimulation(num_cars=num_cars, bad_practice_ratio=ratio)
            if sim.run(max_steps=800):
                jam_count += 1

        probability = jam_count / num_trials
        results[ratio] = probability

        print(f"Bad Practice Ratio: {ratio:.1f} | "
              f"Traffic Jam Probability: {probability:.3f} | "
              f"Jams: {jam_count}/{num_trials}")

    return results


if __name__ == "__main__":
    # Run simulation with different bad practice ratios
    # Using fewer cars to reduce baseline jam probability
    results = run_simulation(num_cars=15, num_trials=100)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nThe simulation demonstrates that as the ratio of cars")
    print("following bad practice (not using rightmost free lane)")
    print("increases, the probability of traffic jams also increases.\n")

    ratios = sorted(results.keys())
    probabilities = [results[r] for r in ratios]

    print("Trend Analysis:")
    for i in range(len(ratios) - 1):
        change = probabilities[i+1] - probabilities[i]
        if change > 0:
            print(f"  Ratio {ratios[i]:.1f} → {ratios[i+1]:.1f}: "
                  f"Probability increased by {change:.3f}")
