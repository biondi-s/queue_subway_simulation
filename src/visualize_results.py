"""
Visualization script for highway simulation results
"""

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from .simulation import run_simulation


def visualize_results(results: dict, save_path: str = None):
    """
    Create visualization of traffic jam probability vs bad practice ratio
    """
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available. Install with: pip install matplotlib")
        return
    
    ratios = sorted(results.keys())
    probabilities = [results[r] for r in ratios]
    
    plt.figure(figsize=(10, 6))
    plt.plot(ratios, probabilities, 'b-o', linewidth=2, markersize=8)
    plt.xlabel('Bad Practice Ratio (Fraction of Cars)', fontsize=12)
    plt.ylabel('Traffic Jam Probability', fontsize=12)
    plt.title('Traffic Jam Probability vs Bad Practice Ratio\n(Italian Highway Rules Simulation)', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, max(probabilities) * 1.1 if probabilities else 1.05)
    
    # Add trend line
    if len(ratios) > 1:
        z = np.polyfit(ratios, probabilities, 1)
        p = np.poly1d(z)
        plt.plot(ratios, p(ratios), "r--", alpha=0.5, linewidth=1, 
                label=f'Trend: y={z[0]:.3f}x+{z[1]:.3f}')
        plt.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"\nGraph saved to {save_path}")
    else:
        plt.show()


if __name__ == "__main__":
    # Run simulation
    print("=" * 60)
    print("HIGHWAY TRAFFIC SIMULATION - ITALIAN RULES")
    print("=" * 60)
    print()
    
    results = run_simulation(num_cars=25, num_trials=100)
    
    # Visualize results
    print("\n" + "=" * 60)
    print("Generating visualization...")
    print("=" * 60)
    
    try:
        visualize_results(results, save_path='media/traffic_jam_results.png')
    except ImportError:
        print("\nMatplotlib not available. Install with: pip install matplotlib")
        print("\nResults summary:")
        for ratio, prob in sorted(results.items()):
            print(f"  Bad Practice Ratio {ratio:.1f}: {prob:.3f} probability")
