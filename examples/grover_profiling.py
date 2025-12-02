"""
Grover's Algorithm Profiling Demo

This example demonstrates circuit profiling and optimization analysis.
"""

import numpy as np
from quantum_debugger import QuantumCircuit, CircuitProfiler


def create_grover_circuit(n_qubits: int = 3, target: int = 5):
    """
    Create a simple Grover's algorithm circuit
    
    Args:
        n_qubits: Number of qubits
        target: Target state to search for
    """
    qc = QuantumCircuit(n_qubits)
    
    # Initialize: Create superposition
    for q in range(n_qubits):
        qc.h(q)
    
    # Oracle: Mark target state
    # (Simplified oracle using phase flip)
    for i, bit in enumerate(format(target, f'0{n_qubits}b')):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled Z gate (simplified with Toffoli decomposition)
    if n_qubits == 3:
        qc.toffoli(0, 1, 2)
    
    for i, bit in enumerate(format(target, f'0{n_qubits}b')):
        if bit == '0':
            qc.x(i)
    
    # Diffusion operator
    for q in range(n_qubits):
        qc.h(q)
    for q in range(n_qubits):
        qc.x(q)
    
    if n_qubits == 3:
        qc.toffoli(0, 1, 2)
    
    for q in range(n_qubits):
        qc.x(q)
    for q in range(n_qubits):
        qc.h(q)
    
    return qc


def main():
    print("=" * 70)
    print(" " * 15 + "GROVER'S ALGORITHM PROFILING DEMO")
    print("=" * 70)
    
    # Create Grover circuit
    print("\n1️⃣  Creating Grover's search circuit...")
    target_state = 5  # Searching for |101⟩
    qc = create_grover_circuit(n_qubits=3, target=target_state)
    
    print(f"   Circuit created: {qc.size()} gates, {qc.num_qubits} qubits")
    print(f"   Searching for state: |{format(target_state, '03b')}⟩")
    
    # Display circuit
    print("\n2️⃣  Circuit diagram:")
    print(qc.draw())
    
    # Initialize profiler
    print("\n3️⃣  Running profiler analysis...")
    profiler = CircuitProfiler(qc)
    
    # Print comprehensive report
    profiler.print_report()
    
    # Get specific metrics
    print("\n4️⃣  Detailed metrics:")
    metrics = profiler.metrics
    
    print(f"\n   Gate Distribution:")
    total = metrics.total_gates
    for gate_name, count in sorted(metrics.gate_counts.items(), 
                                   key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"   - {gate_name}: {count} ({percentage:.1f}%)")
    
    print(f"\n   Critical Path Analysis:")
    print(f"   - Critical path length: {len(metrics.critical_path)} gates")
    print(f"   - Total gates: {metrics.total_gates}")
    print(f"   - Parallelism achieved: {metrics.parallelism:.2f}x")
    
    # Run circuit and analyze results
    print("\n5️⃣  Running circuit simulation...")
    results = qc.run(shots=1000)
    
    print(f"\n   Measurement results (top 5):")
    sorted_counts = sorted(results['counts'].items(), 
                          key=lambda x: x[1], reverse=True)
    for outcome, count in sorted_counts[:5]:
        print(f"   |{outcome}⟩: {count} times ({count/10:.1f}%)")
    
    # Check if target was found
    target_binary = format(target_state, '03b')
    if target_binary in results['counts']:
        target_count = results['counts'][target_binary]
        print(f"\n   ✅ Target state |{target_binary}⟩ found {target_count} times!")
        print(f"   Success probability: {target_count/10:.1f}%")
    
    # Compare different circuit sizes
    print("\n6️⃣ Scaling analysis:")
    print(f"\n   {'Qubits':<10} {'Gates':<10} {'Depth':<10} {'CNOT':<10} {'Exec Time (μs)':<15}")
    print(f"   {'-'*60}")
    
    for n in [2, 3, 4, 5]:
        try:
            temp_qc = create_grover_circuit(n_qubits=n, target=1)
            temp_profiler = CircuitProfiler(temp_qc)
            temp_metrics = temp_profiler.metrics
            exec_time = temp_metrics.estimate_execution_time()
            
            print(f"   {n:<10} {temp_metrics.total_gates:<10} "
                  f"{temp_metrics.depth:<10} {temp_metrics.cnot_count:<10} "
                  f"{exec_time:<15.2f}")
        except:
            pass
    
    print("\n✅ Profiling demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
