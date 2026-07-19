"""Tests for Trotterized Hamiltonian simulation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    trotter_evolve,
    hamiltonian_matrix,
    pauli_term_matrix,
)

TFIM = [
    (1.0, "ZZI"),
    (1.0, "IZZ"),
    (0.5, "XII"),
    (0.5, "IXI"),
    (0.5, "IIX"),
]


class TestPauliMatrices:
    def test_single_pauli(self):
        assert np.allclose(pauli_term_matrix("X"), [[0, 1], [1, 0]])
        assert np.allclose(pauli_term_matrix("Z"), [[1, 0], [0, -1]])

    def test_hamiltonian_is_hermitian(self):
        H = hamiltonian_matrix(TFIM, 3)
        assert np.allclose(H, H.conj().T)


class TestTrotter:
    def test_single_term_is_exact(self):
        for pauli in ["X", "Y", "Z"]:
            r = trotter_evolve([(0.7, pauli)], time=0.9, steps=1, order=1)
            assert r["fidelity"] > 1 - 1e-9

    def test_more_steps_improve_fidelity(self):
        low = trotter_evolve(TFIM, 1.0, steps=2, order=1)["fidelity"]
        high = trotter_evolve(TFIM, 1.0, steps=40, order=1)["fidelity"]
        assert high > low
        assert high > 0.999

    def test_second_order_beats_first(self):
        f1 = trotter_evolve(TFIM, 1.0, steps=4, order=1)["fidelity"]
        f2 = trotter_evolve(TFIM, 1.0, steps=4, order=2)["fidelity"]
        assert f2 > f1

    def test_converges_to_exact(self):
        r = trotter_evolve(TFIM, 1.0, steps=50, order=2)
        assert r["fidelity"] > 0.9999

    def test_custom_initial_state(self):
        psi0 = np.zeros(8, dtype=complex)
        psi0[5] = 1.0
        r = trotter_evolve(TFIM, 0.5, initial_state=psi0, steps=30, order=2)
        assert r["fidelity"] > 0.999

    def test_invalid_order(self):
        with pytest.raises(ValueError):
            trotter_evolve(TFIM, 1.0, steps=1, order=3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
