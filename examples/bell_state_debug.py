"""
Bell State Creation and Debugging Demo

This example demonstrates step-by-step debugging of Bell state creation.
"""

from quantum_debugger import QuantumCircuit, QuantumDebugger
from quantum_debugger.visualization import StateVisualizer, BlochSphere


def main():
    print("=" * 70)
    print(" " * 15 + "BELL STATE DEBUGGING DEMO")
    print("=" * 70)
    
    # Create a Bell state circuit
    print("\n1️⃣  Creating Bell state circuit...")
    qc = QuantumCircuit(2)
    qc.h(0)        # Hadamard on qubit 0
    qc.cnot(0, 1)  # CNOT with control=0, target=1
    
    print(f"   Circuit created: {qc.size()} gates, depth {qc.depth()}")
    print(qc.draw())
    
    # Initialize debugger
    print("\n2️⃣  Initializing debugger...")
    debugger = QuantumDebugger(qc)
    
    # Inspect initial state
    print("\n3️⃣  Initial state |00⟩:")
    debugger.visualize()
    
    # Step 1: Apply Hadamard
    print("\n4️⃣  Stepping through: Applying H gate to qubit 0...")
    debugger.step()
    debugger.visualize()
    
    print("\n   🔍 Analysis after Hadamard:")
    print(f"   - Qubit 0 is in superposition")
    prob_0, prob_1 = debugger.inspector.get_qubit_probabilities(debugger.current_state, 0)
    print(f"   - Qubit 0 probabilities: |0⟩={prob_0:.3f}, |1⟩={prob_1:.3f}")
    print(f"   - Qubit 1 is still |0⟩")
    
    # Step 2: Apply CNOT
    print("\n5️⃣  Stepping through: Applying CNOT gate...")
    debugger.step()
    debugger.visualize()
    
    print("\n   🔍 Analysis after CNOT:")
    state_info = debugger.inspect_state()
    print(f"   - State is entangled: {state_info['is_entangled']}")
    print(f"   - Entropy: {state_info['entropy']:.3f}")
    
    # Show measurement statistics
    print("\n6️⃣  Measurement statistics:")
    stats = debugger.inspector.get_measurement_stats(debugger.current_state)
    for basis, prob in stats.items():
        print(f"   |{basis}⟩: {prob:.4f} ({prob*100:.1f}%)")
    
    # Run actual measurements
    print("\n7️⃣  Running 1000 measurements...")
    results = qc.run(shots=1000)
    print(f"   Measurement counts:")
    for outcome, count in sorted(results['counts'].items()):
        print(f"   |{outcome}⟩: {count} times ({count/10:.1f}%)")
    
    # Visualizations
    print("\n8️⃣  Creating visualizations...")
    try:
        # Plot state probabilities
        StateVisualizer.plot_probabilities(debugger.current_state)
        
        # Plot Bloch sphere for each qubit
        BlochSphere.plot(debugger.current_state, qubit=0)
        BlochSphere.plot(debugger.current_state, qubit=1)
        
    except Exception as e:
        print(f"   Visualization requires display: {e}")
    
    print("\n✅ Demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
