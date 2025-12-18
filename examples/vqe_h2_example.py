"""
Complete VQE Example: Finding H2 Molecule Ground State
======================================================

This example demonstrates the complete workflow for using VQE
to find the ground state energy of the H2 molecule.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger.qml import (
    VQE,
    h2_hamiltonian,
    hardware_efficient_ansatz
)

def main():
    print("=" * 70)
    print(" VQE Example: H2 Molecule Ground State Energy")
    print("=" * 70)
    
    # 1. Define the Hamiltonian
    print("\n1. Loading H2 Hamiltonian...")
    H = h2_hamiltonian()
    print(f"   Hamiltonian shape: {H.shape}")
    print(f"   Number of qubits: 2")
    
    # 2. Compute exact ground state (for comparison)
    exact_energy = np.linalg.eigvalsh(H)[0]
    print(f"\n2. Exact ground state energy:")
    print(f"   E_exact = {exact_energy:.6f} Hartree")
    
    # 3. Setup VQE
    print("\n3. Setting up VQE...")
    vqe = VQE(
        hamiltonian=H,
        ansatz_builder=hardware_efficient_ansatz,
        num_qubits=2,
        optimizer='COBYLA',
        max_iterations=100
    )
    print(f"   Ansatz: Hardware-efficient")
    print(f"   Optimizer: COBYLA")
    print(f"   Max iterations: 100")
    
    # 4. Initialize parameters
    print("\n4. Initializing parameters...")
    np.random.seed(42)
    initial_params = np.random.rand(2) * 0.1
    print(f"   Initial parameters: {initial_params}")
    
    # 5. Run VQE
    print("\n5. Running VQE optimization...")
    print("   (This may take a few seconds...)")
    result = vqe.run(initial_params)
    
    # 6. Display results
    print("\n" + "=" * 70)
    print(" VQE Results")
    print("=" * 70)
    print(f"\nOptimal parameters: {result['optimal_params']}")
    print(f"Ground state energy: {result['ground_state_energy']:.6f} Hartree")
    print(f"Exact energy:        {exact_energy:.6f} Hartree")
    print(f"\nError: {abs(result['ground_state_energy'] - exact_energy):.6f} Hartree")
    print(f"Relative error: {abs(result['ground_state_energy'] - exact_energy) / abs(exact_energy) * 100:.4f}%")
    print(f"\nIterations: {result['iterations']}")
    print(f"Optimization success: {result['success']}")
    
    # 7. Show convergence
    print("\n" + "=" * 70)
    print(" Convergence History")
    print("=" * 70)
    energies = [h['energy'] for h in vqe.history]
    print(f"\nInitial energy: {energies[0]:.6f} Hartree")
    print(f"Final energy:   {energies[-1]:.6f} Hartree")
    print(f"Improvement:    {energies[0] - energies[-1]:.6f} Hartree")
    
    # Show convergence progress
    print("\nEnergy vs Iteration (every 10 steps):")
    for i in range(0, len(energies), 10):
        improvement = ((energies[0] - energies[i]) / (energies[0] - exact_energy)) * 100
        print(f"  Iter {i:3d}: {energies[i]:.6f} Hartree ({improvement:5.1f}% to exact)")
    
    print("\n" + "=" * 70)
    print(" Summary")
    print("=" * 70)
    print(f"\n✓ VQE successfully found H2 ground state")
    print(f"✓ Accuracy: {(1 - abs(result['ground_state_energy'] - exact_energy)/abs(exact_energy))*100:.2f}%")
    print(f"✓ Chemical accuracy (0.0016 Hartree): {abs(result['ground_state_energy'] - exact_energy) < 0.0016}")
    
    if abs(result['ground_state_energy'] - exact_energy) < 0.001:
        print("\n🎉 Excellent! VQE found a highly accurate solution!")
    elif abs(result['ground_state_energy'] - exact_energy) < 0.01:
        print("\n✓ Good! VQE found a reasonable approximation.")
    else:
        print(f"\n⚠ Accuracy could be improved. Try more iterations or deeper ansatz.")
    
    print()

if __name__ == "__main__":
    main()
