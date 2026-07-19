"""Tests for quantum state tomography."""

import numpy as np
import pytest

from quantum_debugger.tomography import state_tomography
from quantum_debugger.core.circuit import QuantumCircuit


class TestStateTomography:
    def test_single_qubit(self):
        qc = QuantumCircuit(1)
        qc.ry(0.7, 0)
        sv = qc.get_statevector().state_vector
        result = state_tomography(sv, shots=8000, seed=0)
        assert result["fidelity"] > 0.95
        assert result["density_matrix"].shape == (2, 2)
        # Density matrix has trace 1.
        assert np.isclose(np.trace(result["density_matrix"]).real, 1.0, atol=1e-9)

    def test_bell_state(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cnot(0, 1)
        sv = qc.get_statevector().state_vector
        result = state_tomography(sv, shots=8000, seed=1)
        assert result["fidelity"] > 0.95
        assert result["density_matrix"].shape == (4, 4)

    def test_random_two_qubit(self):
        np.random.seed(3)
        v = np.random.randn(4) + 1j * np.random.randn(4)
        v /= np.linalg.norm(v)
        result = state_tomography(v, shots=10000, seed=2)
        assert result["fidelity"] > 0.9

    def test_rejects_large_systems(self):
        with pytest.raises(ValueError):
            state_tomography(np.ones(16) / 4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
