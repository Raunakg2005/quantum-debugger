"""
Complex Qiskit Integration Test

Tests advanced features including:
- Multi-qubit algorithms (Grover's, QFT)
- Parameterized gates
- Step-by-step debugging
- State analysis
"""

import numpy as np
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger import QuantumCircuit, QuantumDebugger
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter


def test_grover_algorithm():
    """Test importing Grover's algorithm from Qiskit"""
    print("\n" + "=" * 70)
    print("TEST 1: Grover's Algorithm (3 qubits)")
    print("=" * 70)

    # Create Grover's algorithm in Qiskit
    qc = QiskitCircuit(3)

    # Initialization
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # Oracle (marks |101⟩)
    qc.cz(0, 2)

    # Diffusion operator
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.x(0)
    qc.x(1)
    qc.x(2)
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    qc.x(0)
    qc.x(1)
    qc.x(2)
    qc.h(0)
    qc.h(1)
    qc.h(2)

    print(f"\n✓ Created Qiskit Grover circuit: {len(qc.data)} gates")

    # Import to QuantumDebugger
    qc_qd = QiskitAdapter.from_qiskit(qc)
    print(f"✓ Imported to QuantumDebugger: {len(qc_qd.gates)} gates")

    # Execute and check result
    state = qc_qd.get_statevector()
    probs = state.get_probabilities()

    # Find most likely state
    max_idx = np.argmax(probs)
    max_prob = probs[max_idx]

    print(f"\n✓ Most likely state: |{format(max_idx, '03b')}⟩ with P={max_prob:.3f}")

    if max_idx == 5:  # |101⟩ in little-endian
        print("✅ Grover's algorithm works! Found marked state")
        return True
    else:
        print("⚠️  Different result")
        return False


def test_qft_with_debugging():
    """Test QFT with step-by-step debugging"""
    print("\n" + "=" * 70)
    print("TEST 2: Quantum Fourier Transform with Debugging")
    print("=" * 70)

    # Create 3-qubit QFT in Qiskit
    qc = QiskitCircuit(3)

    # QFT implementation
    # Qubit 2
    qc.h(2)
    qc.cp(np.pi / 2, 1, 2)
    qc.cp(np.pi / 4, 0, 2)

    # Qubit 1
    qc.h(1)
    qc.cp(np.pi / 2, 0, 1)

    # Qubit 0
    qc.h(0)

    # Swaps
    qc.swap(0, 2)

    print(f"\n✓ Created Qiskit QFT circuit: {len(qc.data)} gates")

    # Import and debug
    qc_qd = QiskitAdapter.from_qiskit(qc)
    debugger = QuantumDebugger(qc_qd)

    print("\n✓ Debugging step-by-step:")

    # Add breakpoint at swap
    debugger.add_breakpoint_at_gate(len(qc_qd.gates) - 1)

    steps = 0
    while debugger.step():
        steps += 1
        if steps <= 3:
            state = debugger.get_current_state()
            print(f"   Step {steps}: Entropy = {state.entropy():.4f}")

    final_state = debugger.get_current_state()
    print(f"\n✓ Final state norm: {np.linalg.norm(final_state.state_vector):.10f}")

    if abs(np.linalg.norm(final_state.state_vector) - 1.0) < 1e-10:
        print("✅ QFT maintains unitarity!")
        return True
    return False


def test_parameterized_vqe():
    """Test VQE ansatz with parameterized gates"""
    print("\n" + "=" * 70)
    print("TEST 3: VQE Ansatz with Parameterized Gates")
    print("=" * 70)

    # Create VQE ansatz in Qiskit
    theta1, theta2, theta3 = np.pi / 4, np.pi / 3, np.pi / 6

    qc = QiskitCircuit(2)
    qc.ry(theta1, 0)
    qc.ry(theta2, 1)
    qc.cx(0, 1)
    qc.rz(theta3, 0)
    qc.rz(theta3, 1)

    print(f"\n✓ Created parameterized VQE ansatz: {len(qc.data)} gates")
    print(f"   Parameters: θ₁={theta1:.3f}, θ₂={theta2:.3f}, θ₃={theta3:.3f}")

    # Convert and analyze
    qc_qd = QiskitAdapter.from_qiskit(qc)

    # Check parameters preserved
    param_gates = [g for g in qc_qd.gates if g.params]
    print(f"\n✓ Parameterized gates in QD: {len(param_gates)}")

    # Execute
    state = qc_qd.get_statevector()

    # Check entanglement
    is_entangled = state.is_entangled()
    entropy = state.entropy()

    print(f"\n✓ State properties:")
    print(f"   Entangled: {is_entangled}")
    print(f"   Entropy: {entropy:.4f}")

    # Export back and verify
    qc_back = QiskitAdapter.to_qiskit(qc_qd)

    if len(qc_back.data) == len(qc.data):
        print("\n✅ Roundtrip conversion preserves structure!")
        return True
    return False


def test_algorithm_comparison():
    """Compare execution: Qiskit vs QuantumDebugger"""
    print("\n" + "=" * 70)
    print("TEST 4: Direct Comparison - Deutsch-Jozsa")
    print("=" * 70)

    # Create Deutsch-Jozsa in Qiskit
    qc = QiskitCircuit(3)

    # Prepare superposition
    qc.x(2)
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # Oracle (balanced function)
    qc.cx(0, 2)
    qc.cx(1, 2)

    # Final Hadamards
    qc.h(0)
    qc.h(1)

    print(f"\n✓ Created Deutsch-Jozsa circuit")

    # Method 1: Import Qiskit → QuantumDebugger
    qc_qd_from_qiskit = QiskitAdapter.from_qiskit(qc)
    state_from_qiskit = qc_qd_from_qiskit.get_statevector()

    # Method 2: Direct QuantumDebugger
    qc_qd_direct = QuantumCircuit(3)
    qc_qd_direct.x(2)
    qc_qd_direct.h(0).h(1).h(2)
    qc_qd_direct.cnot(0, 2).cnot(1, 2)
    qc_qd_direct.h(0).h(1)
    state_direct = qc_qd_direct.get_statevector()

    # Compare
    fidelity = state_from_qiskit.fidelity(state_direct)

    print(f"\n✓ Comparison:")
    print(f"   From Qiskit: {state_from_qiskit}")
    print(f"   Direct QD:   {state_direct}")
    print(f"   Fidelity: {fidelity:.15f}")

    if fidelity > 0.99999:
        print("\n✅ Perfect agreement between Qiskit and QuantumDebugger!")
        return True
    return False


def main():
    """Run all complex tests"""
    print("\n" + "=" * 70)
    print(" " * 15 + "COMPLEX QISKIT INTEGRATION TESTS")
    print(" " * 20 + "Advanced Algorithms")
    print("=" * 70)

    tests = [
        test_grover_algorithm,
        test_qft_with_debugging,
        test_parameterized_vqe,
        test_algorithm_comparison,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print(" " * 25 + "SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\n  ✅ Passed: {passed}/{total}")
    print(f"  ❌ Failed: {total - passed}/{total}")

    if all(results):
        print("\n  🎉 ALL COMPLEX TESTS PASSED!")
        print("\n  Qiskit integration validated for:")
        print("    ✓ Multi-qubit algorithms (Grover)")
        print("    ✓ Quantum Fourier Transform")
        print("    ✓ Parameterized circuits (VQE)")
        print("    ✓ Algorithm comparison")
        print("    ✓ Step-by-step debugging")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
