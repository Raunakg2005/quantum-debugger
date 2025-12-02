"""
Qiskit Integration Example

Demonstrates how to use QuantumDebugger with Qiskit circuits.
"""

from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger import QuantumCircuit, QuantumDebugger
from quantum_debugger.integrations import QiskitAdapter


def example_1_import_qiskit():
    """Example 1: Import a Qiskit circuit into QuantumDebugger"""
    print("\n" + "="*70)
    print("Example 1: Import Qiskit Circuit")
    print("="*70)
    
    # Create a Qiskit circuit (Grover's algorithm for 2 qubits)
    qc_qiskit = QiskitCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.h(1)
    qc_qiskit.cz(0, 1)
    qc_qiskit.h(0)
    qc_qiskit.h(1)
    
    print("\n✓ Created Qiskit circuit (Grover iteration)")
    print(f"  Qiskit gates: {len(qc_qiskit.data)}")
    
    # Convert to QuantumDebugger
    qc_qd = QiskitAdapter.from_qiskit(qc_qiskit)
    
    print(f"\n✓ Imported into QuantumDebugger")
    print(f"  QuantumDebugger gates: {len(qc_qd.gates)}")
    
    # Now use QuantumDebugger features!
    debugger = QuantumDebugger(qc_qd)
    
    print(f"\n✓ Debugging with QuantumDebugger:")
    for i in range(3):
        debugger.step()
        state = debugger.get_current_state()
        print(f"  Step {i+1}: {state}")


def example_2_export_to_qiskit():
    """Example 2: Create in QuantumDebugger, export to Qiskit"""
    print("\n" + "="*70)
    print("Example 2: Export to Qiskit")
    print("="*70)
    
    # Create circuit in QuantumDebugger
    qc_qd = QuantumCircuit(3)
    qc_qd.h(0)
    qc_qd.cnot(0, 1)
    qc_qd.cnot(1, 2)
    
    print("\n✓ Created GHZ state in QuantumDebugger")
    print(f"  Gates: {len(qc_qd.gates)}")
    
    # Convert to Qiskit
    qc_qiskit = QiskitAdapter.to_qiskit(qc_qd)
    
    print(f"\n✓ Exported to Qiskit")
    print(f"  Qiskit gates: {len(qc_qiskit.data)}")
    
    # Now you can use Qiskit features (simulators, hardware, etc.)
    print("\n✓ Can now use with Qiskit ecosystem:")
    print("  - Run on IBM Quantum hardware")
    print("  - Use Qiskit simulators")
    print("  - Transpile for specific backends")


def example_3_debug_qiskit_algorithm():
    """Example 3: Debug a Qiskit algorithm step-by-step"""
    print("\n" + "="*70)
    print("Example 3: Debug Qiskit Algorithm")
    print("="*70)
    
    # Create a parameterized Qiskit circuit (VQE ansatz)
    import numpy as np
    qc_qiskit = QiskitCircuit(2)
    qc_qiskit.ry(np.pi/4, 0)
    qc_qiskit.ry(np.pi/3, 1)
    qc_qiskit.cx(0, 1)
    qc_qiskit.rz(np.pi/2, 1)
    
    print("\n✓ Created parameterized Qiskit circuit (VQE ansatz)")
    
    # Import to QuantumDebugger
    qc_qd = QiskitAdapter.from_qiskit(qc_qiskit)
    
    # Set up debugger with breakpoint
    debugger = QuantumDebugger(qc_qd)
    debugger.add_breakpoint_at_gate(2)  # Break before CNOT
    
    print("\n✓ Debugging with breakpoint:")
    
    # Step through
    debugger.step()
    print(f"  After gate 1: {debugger.get_current_state()}")
    
    debugger.step()
    print(f"  After gate 2: {debugger.get_current_state()}")
    
    debugger.continue_execution()
    print(f"  Final state: {debugger.get_current_state()}")


def example_4_compare_results():
    """Example 4: Compare Qiskit and QuantumDebugger execution"""
    print("\n" + "="*70)
    print("Example 4: Compare Results")
    print("="*70)
    
    # Create same circuit in both
    qc_qiskit = QiskitCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.cx(0, 1)
    
    qc_qd = QuantumCircuit(2)
    qc_qd.h(0)
    qc_qd.cnot(0, 1)
    
    print("\n✓ Created identical Bell state circuits")
    
    # Execute in QuantumDebugger
    state_qd = qc_qd.get_statevector()
    
    # Import Qiskit circuit and execute
    qc_qd_from_qiskit = QiskitAdapter.from_qiskit(qc_qiskit)
    state_from_qiskit = qc_qd_from_qiskit.get_statevector()
    
    # Compare
    fidelity = state_qd.fidelity(state_from_qiskit)
    
    print(f"\n✓ Results comparison:")
    print(f"  QD state: {state_qd}")
    print(f"  From Qiskit: {state_from_qiskit}")
    print(f"  Fidelity: {fidelity:.10f}")
    
    if fidelity > 0.9999:
        print("  ✓ Results match perfectly!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*15 + "QISKIT INTEGRATION EXAMPLES")
    print("="*70)
    
    example_1_import_qiskit()
    example_2_export_to_qiskit()
    example_3_debug_qiskit_algorithm()
    example_4_compare_results()
    
    print("\n" + "="*70)
    print("✨ Qiskit integration allows you to:")
    print("  • Import existing Qiskit circuits")
    print("  • Debug step-by-step with breakpoints")
    print("  • Export back to Qiskit for hardware execution")
    print("  • Leverage both ecosystems together!")
    print("="*70 + "\n")
