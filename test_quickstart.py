"""
Quick Start Test - Verify basic library functionality
"""

from quantum_debugger import QuantumCircuit, QuantumDebugger, CircuitProfiler


def test_basic_circuit():
    """Test basic circuit creation and execution"""
    print("\n1️⃣  Testing basic circuit creation...")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cnot(0, 1)
    
    assert qc.num_qubits == 2
    assert qc.size() == 2
    assert qc.depth() == 2
    print("   ✅ Circuit creation works!")
    
    # Test execution
    results = qc.run(shots=100)
    assert 'counts' in results
    assert results['shots'] == 100
    print("   ✅ Circuit execution works!")


def test_debugger():
    """Test debugger functionality"""
    print("\n2️⃣  Testing debugger...")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cnot(0, 1)
    
    debugger = QuantumDebugger(qc)
    
    # Test stepping
    assert debugger.current_gate_index == 0
    debugger.step()
    assert debugger.current_gate_index == 1
    print("   ✅ Step execution works!")
    
    # Test state inspection
    state_info = debugger.inspect_state()
    assert 'num_qubits' in state_info
    assert 'entropy' in state_info
    print("   ✅ State inspection works!")
    
    # Test step back
    debugger.step_back()
    assert debugger.current_gate_index == 0
    print("   ✅ Step back works!")


def test_profiler():
    """Test profiler functionality"""
    print("\n3️⃣  Testing profiler...")
    qc = QuantumCircuit(3)
    for q in range(3):
        qc.h(q)
    qc.cnot(0, 1)
    qc.cnot(1, 2)
    
    profiler = CircuitProfiler(qc)
    metrics = profiler.analyze()
    
    assert metrics.num_qubits == 3
    assert metrics.total_gates == 5
    assert metrics.cnot_count == 2
    print("   ✅ Profiler metrics work!")
    
    suggestions = profiler.get_optimization_suggestions()
    assert isinstance(suggestions, list)
    print("   ✅ Optimization suggestions work!")


def test_quantum_state():
    """Test quantum state operations"""
    print("\n4️⃣  Testing quantum state...")
    from quantum_debugger.core.quantum_state import QuantumState
    from quantum_debugger.core.gates import GateLibrary
    
    state = QuantumState(1)
    
    # Test initial state
    assert abs(state.state_vector[0] - 1.0) < 1e-10
    print("   ✅ State initialization works!")
    
    # Test gate application
    state.apply_gate(GateLibrary.H, [0])
    prob_0 = state.get_measurement_probability(0, 0)
    assert abs(prob_0 - 0.5) < 1e-10
    print("   ✅ Gate application works!")
    
    # Test measurement
    fidelity = state.fidelity(state)
    assert abs(fidelity - 1.0) < 1e-10
    print("   ✅ Fidelity calculation works!")


def test_breakpoints():
    """Test breakpoint system"""
    print("\n5️⃣  Testing breakpoints...")
    qc = QuantumCircuit(2)
    for _ in range(5):
        qc.h(0)
    
    debugger = QuantumDebugger(qc)
    bp = debugger.set_breakpoint(gate=3, description="Test breakpoint")
    
    assert len(debugger.breakpoints) == 1
    assert bp.gate_index == 3
    print("   ✅ Breakpoint creation works!")
    
    debugger.clear_breakpoints()
    assert len(debugger.breakpoints) == 0
    print("   ✅ Breakpoint management works!")


def main():
    """Run all tests"""
    print("="*60)
    print(" "*15 + "QUICK START TEST")
    print("="*60)
    print("\nTesting QuantumDebugger library functionality...\n")
    
    try:
        test_basic_circuit()
        test_debugger()
        test_profiler()
        test_quantum_state()
        test_breakpoints()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nThe QuantumDebugger library is working correctly!")
        print("\nNext steps:")
        print("  1. Run example demos in the examples/ directory")
        print("  2. Try: python examples/bell_state_debug.py")
        print("  3. Read the documentation in README.md")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
