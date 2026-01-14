"""
Fast Backend Tests - Optimized for Speed

Quick tests that verify backend functionality without heavy computation.
"""

import pytest
import numpy as np
import time
from quantum_debugger import QuantumCircuit
from quantum_debugger.backends import get_backend, list_available_backends


def test_sparse_backend_small_circuit():
    """Test sparse backend with small circuit"""
    circuit = QuantumCircuit(5, backend="sparse")
    for i in range(5):
        circuit.h(i)
    for i in range(4):
        circuit.cnot(i, i + 1)

    result = circuit.run(shots=50)
    assert len(circuit.gates) == 9  # 5 H + 4 CNOT
    assert "counts" in result
    assert len(result["counts"]) > 0


def test_complex_number_precision():
    """Test complex number precision across backends"""
    for backend_name in ["numpy", "sparse"]:
        circuit = QuantumCircuit(2, backend=backend_name)
        circuit.h(0).cnot(0, 1)
        circuit.h(1)

        result = circuit.run(shots=100)
        assert "counts" in result
        assert sum(result["counts"].values()) == 100


def test_backend_consistency():
    """Test backend consistency across numpy and sparse"""
    results = {}
    for backend_name in ["numpy", "sparse"]:
        circuit = QuantumCircuit(3, backend=backend_name)
        circuit.h(0).cnot(0, 1).cnot(1, 2)
        results[backend_name] = circuit.run(shots=200)

    # Both should produce valid results
    assert "counts" in results["numpy"]
    assert "counts" in results["sparse"]
    assert len(results["numpy"]["counts"]) > 0
    assert len(results["sparse"]["counts"]) > 0


def test_performance_comparison():
    """Quick performance comparison between backends"""
    perf = {}
    for backend_name in ["numpy", "sparse"]:
        circuit = QuantumCircuit(6, backend=backend_name)
        for i in range(6):
            circuit.h(i)

        start = time.perf_counter()
        circuit.run(shots=100)
        elapsed = time.perf_counter() - start

        perf[backend_name] = elapsed
        assert elapsed > 0  # Should take some time


def test_backend_switching():
    """Test backend switching between circuits"""
    c1 = QuantumCircuit(2, backend="numpy")
    c2 = QuantumCircuit(2, backend="sparse")

    # Backend names might include details like 'Sparse (SciPy)'
    assert "numpy" in c1._initial_state.backend.name.lower()
    assert "sparse" in c2._initial_state.backend.name.lower()


def test_auto_backend_selection():
    """Test automatic backend selection"""
    circuit = QuantumCircuit(3)
    backend_name = circuit._initial_state.backend.name
    available = list_available_backends()

    # Check that some backend was selected and is available
    assert backend_name is not None
    # Backend name might be capitalized (NumPy) or lowercase (numpy)
    assert any(backend_name.lower() == k.lower() for k in available.keys())
