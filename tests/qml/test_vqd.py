"""Tests for Variational Quantum Deflation (excited states)."""

import numpy as np
import pytest

from quantum_debugger.qml.algorithms import VQD


class TestVQD:
    def test_initialization(self):
        H = np.eye(4, dtype=complex)
        vqd = VQD(H, num_qubits=2, n_states=2, n_layers=3)
        assert vqd.n_params == 2 * (3 + 1)

    def test_rejects_wrong_hamiltonian_size(self):
        with pytest.raises(ValueError):
            VQD(np.eye(8), num_qubits=2)

    def test_finds_ground_and_excited_diagonal(self):
        H = np.diag([0.0, 1.0, 2.0, 3.0]).astype(complex)
        vqd = VQD(H, num_qubits=2, n_states=3, n_layers=3, beta=5.0, max_iterations=300)
        result = vqd.run(seed=1)
        exact = vqd.exact_spectrum()
        for k in range(3):
            assert abs(result["energies"][k] - exact[k]) < 0.1

    def test_finds_excited_random_symmetric(self):
        np.random.seed(2)
        A = np.random.randn(4, 4)
        H = ((A + A.T) / 2).astype(complex)
        vqd = VQD(H, num_qubits=2, n_states=2, n_layers=4, beta=5.0, max_iterations=400)
        result = vqd.run(seed=2)
        exact = vqd.exact_spectrum()
        assert abs(result["energies"][0] - exact[0]) < 0.1
        assert abs(result["energies"][1] - exact[1]) < 0.15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
