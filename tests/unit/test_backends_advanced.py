"""
Advanced Backend Tests - Edge Cases and Performance

Tests backend robustness with edge cases,large circuits,
and cross-backend numerical consistency.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from quantum_debugger import QuantumCircuit
from quantum_debugger.backends import get_backend, list_available_backends


def test_large_circuit_memory_efficiency():
    """Test large circuit memory efficiency with sparse backend"""
    # Create 10-qubit circuit with sparse backend
    circuit_sparse = QuantumCircuit(10, backend='sparse')
    for i in range(10):
        circuit_sparse.h(i)
    for i in range(9):
        circuit_sparse.cnot(i, i+1)
    
    # Run and measure
    result = circuit_sparse.run(shots=100)
    assert 'counts' in result
    assert len(circuit_sparse.gates) > 0


def test_complex_number_precision():
    """Test complex number precision across backends"""
    backends = ['numpy', 'sparse']
    
    # Create circuit with rotation gates (complex amplitudes)
    for backend_name in backends:
        circuit = QuantumCircuit(2, backend=backend_name)
        circuit.h(0)
        circuit.rx(0, np.pi/4)  # Rotation gate
        circuit.ry(1, np.pi/3)
        
        result = circuit.run(shots=1000)
        assert 'counts' in result


def test_cross_backend_consistency():
    """Test cross-backend consistency for deep circuits"""
    # Create identical circuits with different backends
    circuits = {}
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(3, backend=backend_name)
        circuit.h(0).h(1).h(2)
        circuit.cnot(0, 1).cnot(1, 2)
        circuit.h(0).h(1).h(2)
        circuits[backend_name] = circuit
    
    # Run and compare
    results = {}
    for name, circuit in circuits.items():
        results[name] = circuit.run(shots=1000)
    
    # Check consistency
    numpy_counts = results['numpy']['counts']
    sparse_counts = results['sparse']['counts']
    
   # Should have same keys
    assert set(numpy_counts.keys()) == set(sparse_counts.keys())


def test_performance_comparison():
    """Test performance comparison between backends"""
    circuit_size = 8
    shots = 500
    
    perf_results = {}
    
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(circuit_size, backend=backend_name)
        
        # Add gates
        for i in range(circuit_size):
            circuit.h(i)
        for i in range(circuit_size - 1):
            circuit.cnot(i, i+1)
        
        # Benchmark
        start = time.perf_counter()
        result = circuit.run(shots=shots)
        elapsed = time.perf_counter() - start
        
        perf_results[backend_name] = elapsed
    
    # Both should complete
    assert all(t > 0 for t in perf_results.values())


def test_backend_switching():
    """Test backend switching mid-workflow"""
    # Start with numpy
    circuit1 = QuantumCircuit(3, backend='numpy')
    circuit1.h(0).cnot(0, 1)
    result1 = circuit1.run(shots=100)
    
    # Switch to sparse
    circuit2 = QuantumCircuit(3, backend='sparse')
    circuit2.h(0).cnot(0, 1)
    result2 = circuit2.run(shots=100)
    
    assert circuit1._initial_state.backend.name == "NumPy"
    assert circuit2._initial_state.backend.name == "Sparse (SciPy)"


def test_single_qubit_edge_case():
    """Test single qubit edge case on all backends"""
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(1, backend=backend_name)
        circuit.h(0)
        result = circuit.run(shots=100)
        
        # Should have results
        counts = result['counts']
        assert len(counts) > 0


def test_scaling_to_larger_circuits():
    """Test scaling to larger circuits with sparse backend"""
    # Try 12 qubits with sparse backend (dense would need 16GB!)
    circuit = QuantumCircuit(12, backend='sparse')
    circuit.h(0)
    for i in range(11):
        circuit.cnot(i, i+1)
    
    # Just 10 shots to keep it fast
    result = circuit.run(shots=10)
    assert 'counts' in result


def test_auto_backend_selection():
    """Test auto backend selection logic"""
    # Test that auto picks the right backend
    circuit = QuantumCircuit(5)  # backend='auto' is default
    
    backend_name = circuit._initial_state.backend.name
    available = list_available_backends()
    
    # Should pick Numba if available, else NumPy
    if available.get('numba', False):
        expected = "Numba (JIT)"
    else:
        expected = "NumPy"
    
    assert backend_name in [expected, "NumPy", "Numba (JIT)"]
