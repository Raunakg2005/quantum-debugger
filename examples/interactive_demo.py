"""
Interactive Demo - Complete Feature Showcase

This example demonstrates all major features of QuantumDebugger.
"""

from quantum_debugger import QuantumCircuit, QuantumDebugger, CircuitProfiler
from quantum_debugger.visualization import StateVisualizer, BlochSphere
from quantum_debugger.core.quantum_state import QuantumState


def demo_basic_debugging():
    """Demonstrate basic debugging features"""
    print("\n" + "="*70)
    print("📝 DEMO 1: Basic Debugging Features")
    print("="*70)
    
    # Create a simple circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cnot(0, 1)
    qc.rz(1.5, 0)
    
    print("\nCircuit:")
    print(qc.draw())
    
    # Debug step-by-step
    debugger = QuantumDebugger(qc)
    
    print("\n▶️  Step 1: Initial state")
    debugger.print_status()
    
    print("\n▶️  Step 2: After Hadamard")
    debugger.step()
    print(debugger.inspector.format_state_string(debugger.current_state))
    
    print("\n▶️  Step 3: After CNOT")
    debugger.step()
    print(debugger.inspector.format_state_string(debugger.current_state))
    
    print("\n▶️  Step 4: After RZ rotation")
    debugger.step()
    print(debugger.inspector.format_state_string(debugger.current_state))


def demo_breakpoints():
    """Demonstrate breakpoint features"""
    print("\n" + "="*70)
    print("🔴 DEMO 2: Breakpoints")
    print("="*70)
    
    # Create circuit
    qc = QuantumCircuit(3)
    for _ in range(3):
        for q in range(3):
            qc.h(q)
        qc.cnot(0, 1)
        qc.cnot(1, 2)
    
    debugger = QuantumDebugger(qc)
    
    # Set breakpoint at gate 5
    print("\n▶️  Setting breakpoint at gate 5...")
    debugger.set_breakpoint(gate=5, description="Checkpoint after 5 gates")
    
    # Set conditional breakpoint for entanglement
    print("▶️  Setting conditional breakpoint for entanglement...")
    debugger.set_breakpoint(
        condition=lambda s: s.is_entangled() if s.num_qubits == 2 else False,
        description="When state becomes entangled"
    )
    
    debugger.print_status()
    
    print("\n▶️  Running until breakpoint...")
    debugger.run_until_breakpoint()
    
    print(f"\nStopped at gate {debugger.current_gate_index}")
    print(debugger.inspector.format_state_string(debugger.current_state))


def demo_profiling():
    """Demonstrate profiling features"""
    print("\n" + "="*70)
    print("📊 DEMO 3: Circuit Profiling")
    print("="*70)
    
    # Create a more complex circuit
    qc = QuantumCircuit(4)
    
    # Entangle all qubits
    for q in range(4):
        qc.h(q)
    
    for q in range(3):
        qc.cnot(q, q+1)
    
    # Add some rotations
    for q in range(4):
        qc.rz(0.5, q)
        qc.rx(0.3, q)
    
    # More entanglement
    qc.cnot(3, 0)
    qc.cnot(2, 1)
    
    # Profile the circuit
    profiler = CircuitProfiler(qc)
    profiler.print_report()


def demo_state_inspection():
    """Demonstrate state inspection features"""
    print("\n" + "="*70)
    print("🔍 DEMO 4: State Inspection")
    print("="*70)
    
    # Create GHZ state
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cnot(0, 1)
    qc.cnot(0, 2)
    
    state = qc.get_statevector()
    
    print("\nGHZ State:")
    print(StateInspector.format_state_string(state))
    
    print("\n📈 State Summary:")
    from quantum_debugger.debugger.inspector import StateInspector
    summary = StateInspector.get_state_summary(state)
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n📊 Measurement Statistics:")
    stats = StateInspector.get_measurement_stats(state)
    for basis, prob in stats.items():
        print(f"   |{basis}⟩: {prob:.4f}")
    
    print("\n📉 Per-Qubit Analysis:")
    for q in range(3):
        p0, p1 = StateInspector.get_qubit_probabilities(state, q)
        print(f"   Qubit {q}: P(0)={p0:.4f}, P(1)={p1:.4f}")


def demo_visualization():
    """Demonstrate visualization features"""
    print("\n" + "="*70)
    print("🎨 DEMO 5: Visualizations")
    print("="*70)
    
    # Create interesting state
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.cnot(0, 2)
    
    state = qc.get_statevector()
    
    print("\nGenerating visualizations...")
    print("(Close plot windows to continue)")
    
    try:
        # State vector plot
        StateVisualizer.plot_state_vector(state)
        
        # Probability plot
        StateVisualizer.plot_probabilities(state)
        
        # Per-qubit probabilities
        StateVisualizer.plot_qubit_probabilities(state)
        
        # Bloch sphere for qubit 0
        BlochSphere.plot(state, qubit=0)
        
        print("✅ Visualizations displayed!")
        
    except Exception as e:
        print(f"⚠️  Visualization requires display environment: {e}")


def demo_execution_history():
    """Demonstrate execution history and rewind"""
    print("\n" + "="*70)
    print("⏮️  DEMO 6: Execution History and Rewind")
    print("="*70)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cnot(0, 1)
    qc.rz(1.0, 0)
    qc.rx(0.5, 1)
    
    debugger = QuantumDebugger(qc)
    
    print("\n▶️  Executing circuit...")
    debugger.run_to_end()
    
    print(f"\nFinal state (at gate {debugger.current_gate_index}):")
    print(debugger.inspector.format_state_string(debugger.current_state))
    
    print("\n⏮️  Rewinding 2 steps...")
    debugger.step_back(2)
    
    print(f"\nState after rewind (at gate {debugger.current_gate_index}):")
    print(debugger.inspector.format_state_string(debugger.current_state))
    
    print("\n📜 Execution trace:")
    trace = debugger.get_execution_trace()
    for entry in trace[:5]:  # Show first 5
        print(f"   Gate {entry['gate_index']}: {entry['gate_name']}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" " * 15 + "🚀 QUANTUM DEBUGGER - INTERACTIVE DEMO")
    print("="*70)
    print("\nThis demo showcases all major features of the QuantumDebugger library.")
    print("\nPress Enter after each demo to continue to the next one...")
    
    demos = [
        ("Basic Debugging", demo_basic_debugging),
        ("Breakpoints", demo_breakpoints),
        ("Circuit Profiling", demo_profiling),
        ("State Inspection", demo_state_inspection),
        ("Visualizations", demo_visualization),
        ("Execution History", demo_execution_history),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        if i > 1:
            input(f"\n\nPress Enter to run Demo {i}: {name}...")
        
        try:
            demo_func()
        except Exception as e:
            print(f"\n⚠️  Error in demo: {e}")
        
        print(f"\n✅ Demo {i} complete!")
    
    print("\n" + "="*70)
    print(" " * 20 + "🎉 ALL DEMOS COMPLETE!")
    print("="*70)
    print("\nThank you for trying QuantumDebugger!")
    print("Visit our documentation for more examples and tutorials.\n")


if __name__ == "__main__":
    main()
