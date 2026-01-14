"""
Backend Integration Test

Test that QuantumCircuit properly uses backends.
"""

import pytest
import numpy as np
from quantum_debugger import QuantumCircuit


def test_create_circuit_with_backends():
    """Test creating circuits with different backends"""
    backends_to_test = ["numpy", "sparse"]

    for backend_name in backends_to_test:
        circuit = QuantumCircuit(2, backend=backend_name)
        circuit.h(0).cnot(0, 1)

        assert backend_name.lower() in circuit._initial_state.backend.name.lower()


def test_run_circuit_with_backends():
    """Test running circuits with different backends"""
    backends_to_test = ["numpy", "sparse"]

    for backend_name in backends_to_test:
        circuit = QuantumCircuit(2, backend=backend_name)
        circuit.h(0).cnot(0, 1)

        result = circuit.run(shots=100)

        assert "counts" in result
        assert sum(result["counts"].values()) == 100


def test_consistency_across_backends():
    """Test that different backends give consistent results"""
    reference_circuit = QuantumCircuit(2, backend="numpy")
    reference_circuit.h(0).cnot(0, 1)
    reference_result = reference_circuit.run(shots=1000)

    # Test sparse backend
    circuit = QuantumCircuit(2, backend="sparse")
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=1000)

    # Both should have similar distributions (within statistical variance)
    ref_counts = reference_result["counts"]
    test_counts = result["counts"]

    # Check same keys exist
    assert set(ref_counts.keys()) == set(test_counts.keys())

    # Check statistical similarity (loose tolerance due to randomness)
    for key in ref_counts:
        assert abs(ref_counts[key] - test_counts[key]) < 200  # 20% tolerance


def test_auto_backend_selection():
    """Test automatic backend selection"""
    circuit = QuantumCircuit(2)  # Should auto-select

    assert circuit._initial_state.backend.name is not None

    result = circuit.run(shots=100)
    assert "counts" in result
