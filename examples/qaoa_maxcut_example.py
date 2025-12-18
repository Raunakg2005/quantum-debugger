"""
Complete QAOA Example: Solving MaxCut on Various Graphs
========================================================

This example demonstrates using QAOA to solve the MaxCut problem
on different graph topologies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger.qml import QAOA

def solve_maxcut(graph, graph_name, p=2):
    """Solve MaxCut for a given graph using QAOA"""
    print(f"\n{'=' * 70}")
    print(f" {graph_name}")
    print(f"{'=' * 70}")
    print(f"Graph: {len(set([n for edge in graph for n in edge]))} nodes, {len(graph)} edges")
    print(f"QAOA layers (p): {p}")
    
    # Setup QAOA
    qaoa = QAOA(graph=graph, p=p, optimizer='COBYLA', max_iterations=50)
    
    # Run optimization
    np.random.seed(42)
    result = qaoa.run()
    
    # Display results
    print(f"\nResults:")
    print(f"  Best cut value: {result['best_value']:.4f}")
    print(f"  Max possible: {len(graph)}")
    print(f"  Approximation ratio: {result['best_value']/len(graph):.2%}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Success: {result['success']}")
    
    return result


def visualize_convergence(qaoa, graph_name):
    """Show optimization convergence"""
    costs = [-h['cost'] for h in qaoa.history]  # Negate for maximization
    
    print(f"\nConvergence for {graph_name}:")
    print(f"  Initial cut: {costs[0]:.4f}")
    print(f"  Final cut:   {costs[-1]:.4f}")
    print(f"  Improvement: {costs[-1] - costs[0]:.4f}")
    
    # Show progress every 10 iterations
    print("\n  Progress:")
    for i in range(0, len(costs), max(1, len(costs)//5)):
        print(f"    Iter {i:3d}: {costs[i]:.4f}")


def main():
    print("=" * 70)
    print(" QAOA Examples: MaxCut on Various Graphs")
    print("=" * 70)
    print("\nThis example demonstrates QAOA on different graph topologies.")
    
    # Example 1: Triangle
    graph_triangle = [(0,1), (1,2), (2,0)]
    result1 = solve_maxcut(graph_triangle, "Triangle Graph (C3)", p=2)
    
    # Example 2: Square
    graph_square = [(0,1), (1,2), (2,3), (3,0)]
    result2 = solve_maxcut(graph_square, "Square Graph (C4)", p=2)
    
    # Example 3: Complete Graph K4
    graph_complete = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    result3 = solve_maxcut(graph_complete, "Complete Graph (K4)", p=3)
    
    # Example 4: Star Graph
    graph_star = [(0,1), (0,2), (0,3), (0,4)]
    result4 = solve_maxcut(graph_star, "Star Graph", p=2)
    
    # Example 5: Line Graph
    graph_line = [(0,1), (1,2), (2,3)]
    result5 = solve_maxcut(graph_line, "Line Graph (Path)", p=1)
    
    # Summary
    print("\n" + "=" * 70)
    print(" Summary of Results")
    print("=" * 70)
    
    results = [
        ("Triangle (C3)", result1, 2),
        ("Square (C4)", result2, 4),
        ("Complete (K4)", result3, 4),
        ("Star", result4, 4),
        ("Line (Path)", result5, 2)
    ]
    
    print(f"\n{'Graph':<15} {'Cut Value':<12} {'Optimal':<10} {'Quality':<10}")
    print("-" * 50)
    for name, result, optimal in results:
        quality = (result['best_value'] / optimal) * 100
        print(f"{name:<15} {result['best_value']:<12.2f} {optimal:<10} {quality:>6.1f}%")
    
    # Comparison: Effect of p value
    print("\n" + "=" * 70)
    print(" Effect of p (Number of QAOA Layers)")
    print("=" * 70)
    print("\nTesting square graph with different p values...")
    
    graph = [(0,1), (1,2), (2,3), (3,0)]
    p_values = [1, 2, 3]
    p_results = {}
    
    for p in p_values:
        qaoa = QAOA(graph=graph, p=p, max_iterations=30)
        result = qaoa.run(np.random.rand(2*p))
        p_results[p] = result['best_value']
        print(f"  p={p}: Cut value = {result['best_value']:.4f}")
    
    print("\nObservation: Higher p generally finds better solutions.")
    
    print("\n" + "=" * 70)
    print(" Key Takeaways")
    print("=" * 70)
    print("""
✓ QAOA finds good approximate solutions to MaxCut
✓ Performance varies by graph topology
✓ Higher p (more layers) → better approximations
✓ Trade-off: more layers = more parameters to optimize
✓ Typical approximation ratios: 70-95% of optimal

Tips for better results:
  1. Start with p=2 for most problems
  2. Use p=3+ for harder instances
  3. Try multiple random initializations
  4. Consider problem-specific parameter initialization
    """)

if __name__ == "__main__":
    main()
