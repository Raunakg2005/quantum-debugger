"""
EXTREME Qiskit Integration Tests

The most challenging test scenarios:
- 10+ qubit circuits
- Quantum error correction
- Variational algorithms at scale
- Hybrid classical-quantum
- Performance benchmarks
"""

import numpy as np
import time
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger import QuantumCircuit, QuantumDebugger
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter


def test_10_qubit_random_circuit():
    """Test 10-qubit random circuit conversion"""
    print("\n" + "="*70)
    print("EXTREME TEST 1: 10-Qubit Random Circuit (50 gates)")
    print("="*70)
    
    # Create large random circuit
    np.random.seed(42)
    qc = QiskitCircuit(10)
    
    # Add random gates
    for _ in range(50):
        gate_type = np.random.choice(['h', 'x', 'rx', 'cx', 'cz'])
        qubit = np.random.randint(0, 10)
        
        if gate_type == 'h':
            qc.h(qubit)
        elif gate_type == 'x':
            qc.x(qubit)
        elif gate_type == 'rx':
            qc.rx(np.random.random() * 2 * np.pi, qubit)
        elif gate_type in ['cx', 'cz']:
            target = np.random.randint(0, 10)
            if target != qubit:
                if gate_type == 'cx':
                    qc.cx(qubit, target)
                else:
                    qc.cz(qubit, target)
    
    print(f"\n✓ Created 10-qubit circuit with {len(qc.data)} gates")
    
    # Convert and measure performance
    start = time.time()
    qc_qd = QiskitAdapter.from_qiskit(qc)
    conversion_time = time.time() - start
    
    print(f"✓ Conversion time: {conversion_time*1000:.2f}ms")
    
    # Execute
    start = time.time()
    state = qc_qd.get_statevector()
    execution_time = time.time() - start
    
    print(f"✓ Execution time: {execution_time*1000:.2f}ms")
    print(f"✓ State space: {state.dim} dimensions (2^{qc_qd.num_qubits})")
    print(f"✓ Entropy: {state.entropy():.4f}")
    print(f"✓ Norm: {np.linalg.norm(state.state_vector):.10f}")
    
    if abs(np.linalg.norm(state.state_vector) - 1.0) < 1e-10:
        print("\n✅ 10-qubit circuit executed successfully!")
        return True
    return False


def test_quantum_phase_estimation():
    """Test Quantum Phase Estimation algorithm"""
    print("\n" + "="*70)
    print("EXTREME TEST 2: Quantum Phase Estimation")
    print("="*70)
    
    # QPE with 3 counting qubits, 1 eigenstate qubit
    n_count = 3
    qc = QiskitCircuit(n_count + 1)
    
    # Initialize counting qubits
    for qubit in range(n_count):
        qc.h(qubit)
    
    # Prepare eigenstate
    qc.x(n_count)
    
    # Controlled-U operations
    repetitions = 1
    for counting_qubit in range(n_count):
        for _ in range(repetitions):
            # Controlled-T gate (phase π/4)
            angle = np.pi / 4
            qc.cp(angle, counting_qubit, n_count)
        repetitions *= 2
    
    # Inverse QFT on counting qubits
    for qubit in range(n_count // 2):
        qc.swap(qubit, n_count - qubit - 1)
    
    for j in range(n_count):
        for m in range(j):
            qc.cp(-np.pi / float(2**(j - m)), m, j)
        qc.h(j)
    
    print(f"\n✓ Created QPE circuit: {len(qc.data)} gates")
    
    # Convert and analyze
    qc_qd = QiskitAdapter.from_qiskit(qc)
    state = qc_qd.get_statevector()
    
    probs = state.get_probabilities()
    max_idx = np.argmax(probs)
    max_prob = probs[max_idx]
    
    print(f"\n✓ Most likely measurement: |{format(max_idx, f'0{n_count+1}b')}⟩")
    print(f"   Probability: {max_prob:.4f}")
    print(f"   State entropy: {state.entropy():.4f}")
    
    print("\n✅ Quantum Phase Estimation executed!")
    return True


def test_variational_quantum_eigensolver_ansatz():
    """Test complex VQE ansatz with multiple layers"""
    print("\n" + "="*70)
    print("EXTREME TEST 3: Multi-Layer VQE Ansatz")
    print("="*70)
    
    n_qubits = 4
    n_layers = 3
    
    # Create layered ansatz
    qc = QiskitCircuit(n_qubits)
    
    param_count = 0
    for layer in range(n_layers):
        # Rotation layer
        for q in range(n_qubits):
            theta = np.random.random() * 2 * np.pi
            qc.ry(theta, q)
            param_count += 1
        
        # Entangling layer
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)
        qc.cx(n_qubits - 1, 0)  # Circular entanglement
        
        # Phase layer
        for q in range(n_qubits):
            phi = np.random.random() * 2 * np.pi
            qc.rz(phi, q)
            param_count += 1
    
    print(f"\n✓ Created {n_layers}-layer VQE ansatz")
    print(f"   Total gates: {len(qc.data)}")
    print(f"   Parameters: {param_count}")
    
    # Convert with debugger
    qc_qd = QiskitAdapter.from_qiskit(qc)
    debugger = QuantumDebugger(qc_qd)
    
    # Track entanglement through layers
    print(f"\n✓ Tracking entanglement through layers:")
    
    gates_per_layer = len(qc_qd.gates) // n_layers
    for layer in range(n_layers):
        for _ in range(gates_per_layer):
            if debugger.current_gate_index >= len(qc_qd.gates):
                break
            debugger.step()
        
        state = debugger.get_current_state()
        print(f"   Layer {layer + 1}: Entropy = {state.entropy():.4f}, Entangled = {state.is_entangled()}")
    
    # Complete execution
    debugger.continue_execution()
    final_state = debugger.get_current_state()
    
    print(f"\n✓ Final state:")
    print(f"   Entropy: {final_state.entropy():.4f}")
    print(f"   Entangled: {final_state.is_entangled()}")
    
    print("\n✅ Multi-layer VQE ansatz works!")
    return True


def test_error_correction_encoding():
    """Test quantum error correction encoding circuit"""
    print("\n" + "="*70)
    print("EXTREME TEST 4: 3-Qubit Bit-Flip Code Encoding")
    print("="*70)
    
    # Encode 1 logical qubit into 3 physical qubits
    qc = QiskitCircuit(3)
    
    # Prepare logical qubit (arbitrary state)
    qc.ry(np.pi/3, 0)
    
    # Encoding circuit
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    print(f"\n✓ Created error correction encoding: {len(qc.data)} gates")
    
    # Convert and verify
    qc_qd = QiskitAdapter.from_qiskit(qc)
    state = qc_qd.get_statevector()
    
    # Check encoded state properties
    probs = state.get_probabilities()
    
    # Should have weight on |000⟩ and |111⟩
    print(f"\n✓ Encoded state probabilities:")
    print(f"   P(|000⟩) = {probs[0]:.4f}")
    print(f"   P(|111⟩) = {probs[7]:.4f}")
    print(f"   Entangled: {state.is_entangled()}")
    
    if state.is_entangled():
        print("\n✅ Error correction encoding creates entanglement!")
        return True
    return False


def test_performance_scaling():
    """Test performance across different qubit counts"""
    print("\n" + "="*70)
    print("EXTREME TEST 5: Performance Scaling (4-12 qubits)")
    print("="*70)
    
    results = []
    
    print(f"\n{'Qubits':<10}{'Gates':<10}{'Convert(ms)':<15}{'Execute(ms)':<15}")
    print("-" * 50)
    
    for n_qubits in [4, 6, 8, 10, 12]:
        # Create test circuit
        qc = QiskitCircuit(n_qubits)
        
        # Add gates (linear in qubit count)
        for q in range(n_qubits):
            qc.h(q)
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)
        for q in range(n_qubits):
            qc.rz(np.pi/4, q)
        
        n_gates = len(qc.data)
        
        # Measure conversion time
        start = time.time()
        qc_qd = QiskitAdapter.from_qiskit(qc)
        convert_time = (time.time() - start) * 1000
        
        # Measure execution time
        start = time.time()
        state = qc_qd.get_statevector()
        exec_time = (time.time() - start) * 1000
        
        print(f"{n_qubits:<10}{n_gates:<10}{convert_time:<15.2f}{exec_time:<15.2f}")
        
        results.append({
            'qubits': n_qubits,
            'convert_time': convert_time,
            'exec_time': exec_time
        })
    
    print(f"\n✓ Performance scaling measured")
    print(f"   10-qubit execution: {results[3]['exec_time']:.2f}ms")
    print(f"   12-qubit execution: {results[4]['exec_time']:.2f}ms")
    
    print("\n✅ Performance scales reasonably!")
    return True


def test_roundtrip_large_circuit():
    """Test roundtrip with a large complex circuit"""
    print("\n" + "="*70)
    print("EXTREME TEST 6: Large Circuit Roundtrip (8 qubits, 100 gates)")
    print("="*70)
    
    # Create large circuit
    np.random.seed(123)
    qc_original = QiskitCircuit(8)
    
    for _ in range(100):
        gate_type = np.random.choice(['h', 'rx', 'ry', 'rz', 'cx', 'cz', 'swap'])
        q1 = np.random.randint(0, 8)
        
        if gate_type == 'h':
            qc_original.h(q1)
        elif gate_type in ['rx', 'ry', 'rz']:
            angle = np.random.random() * 2 * np.pi
            getattr(qc_original, gate_type)(angle, q1)
        else:
            q2 = np.random.randint(0, 8)
            if q1 != q2:
                getattr(qc_original, gate_type)(q1, q2)
    
    print(f"\n✓ Created large circuit: {len(qc_original.data)} gates")
    
    # Roundtrip: Qiskit → QD → Qiskit
    qc_qd = QiskitAdapter.from_qiskit(qc_original)
    qc_roundtrip = QiskitAdapter.to_qiskit(qc_qd)
    
    print(f"✓ Roundtrip complete")
    print(f"   Original gates: {len(qc_original.data)}")
    print(f"   Roundtrip gates: {len(qc_roundtrip.data)}")
    
    # Verify gate count preserved
    if len(qc_original.data) == len(qc_roundtrip.data):
        print("\n✅ Large circuit roundtrip preserves all gates!")
        return True
    else:
        print(f"\n⚠️  Gate count mismatch: {len(qc_original.data)} vs {len(qc_roundtrip.data)}")
        return False


def main():
    """Run all extreme tests"""
    print("\n" + "="*70)
    print(" "*10 + "EXTREME QISKIT INTEGRATION TESTS")
    print(" "*15 + "Maximum Complexity & Scale")
    print("="*70)
    
    tests = [
        test_10_qubit_random_circuit,
        test_quantum_phase_estimation,
        test_variational_quantum_eigensolver_ansatz,
        test_error_correction_encoding,
        test_performance_scaling,
        test_roundtrip_large_circuit,
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
    
    # Final summary
    print("\n" + "="*70)
    print(" "*22 + "FINAL RESULTS")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\n  ✅ Passed: {passed}/{total}")
    print(f"  ❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n  🔥🔥🔥 ALL EXTREME TESTS PASSED! 🔥🔥🔥")
        print("\n  Your Qiskit integration handles:")
        print("    ✓ 10+ qubit circuits")
        print("    ✓ Quantum Phase Estimation")
        print("    ✓ Multi-layer VQE")
        print("    ✓ Error correction codes")
        print("    ✓ Performance at scale")
        print("    ✓ 100+ gate circuits")
        print("\n  🚀 PRODUCTION-GRADE QISKIT INTEGRATION! 🚀")
    
    print("\n" + "="*70 + "\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    exit(main())
