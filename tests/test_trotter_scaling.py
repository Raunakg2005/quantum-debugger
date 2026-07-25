"""Tests for Trotter error scaling."""

import numpy as np
import pytest
from scipy.linalg import expm

from quantum_debugger.algorithms import (
    trotter_unitary,
    trotter_error_scaling,
    hamiltonian_matrix,
    tfim_hamiltonian,
    heisenberg_hamiltonian,
)


class TestTrotterUnitary:
    def test_single_step_is_unitary(self):
        U = trotter_unitary(tfim_hamiltonian(3, 1.0, 0.7), time=0.5, steps=4, order=2)
        assert np.allclose(U.conj().T @ U, np.eye(8), atol=1e-10)

    def test_converges_to_exact(self):
        terms = tfim_hamiltonian(3, 1.0, 0.7)
        H = hamiltonian_matrix(terms, 3)
        exact = expm(-1j * 1.0 * H)
        U = trotter_unitary(terms, time=1.0, steps=200, order=2)
        assert np.linalg.norm(U - exact, 2) < 1e-3


class TestErrorScaling:
    def test_first_order_slope_minus_one(self):
        r = trotter_error_scaling(tfim_hamiltonian(3, 1.0, 0.7), order=1)
        assert abs(r["slope"] - (-1.0)) < 0.15

    def test_second_order_slope_minus_two(self):
        r = trotter_error_scaling(tfim_hamiltonian(3, 1.0, 0.7), order=2)
        assert abs(r["slope"] - (-2.0)) < 0.15

    def test_errors_decrease_monotonically(self):
        r = trotter_error_scaling(tfim_hamiltonian(3, 1.0, 0.7), order=1)
        assert all(b < a for a, b in zip(r["errors"], r["errors"][1:]))

    def test_second_order_beats_first_order(self):
        e1 = trotter_error_scaling(tfim_hamiltonian(3, 1.0, 0.7), order=1)["errors"][-1]
        e2 = trotter_error_scaling(tfim_hamiltonian(3, 1.0, 0.7), order=2)["errors"][-1]
        assert e2 < e1

    def test_heisenberg_scaling(self):
        r = trotter_error_scaling(heisenberg_hamiltonian(3), time=0.8, order=2)
        assert abs(r["slope"] - (-2.0)) < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
