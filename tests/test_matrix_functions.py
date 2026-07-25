"""Tests for matrix functions via Chebyshev/QSVT."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    matrix_function_chebyshev,
    chebyshev_coefficients,
    hamiltonian_simulation_qsvt,
)


def _random_hermitian(d, seed, norm=0.8):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    A = (M + M.conj().T) / 2
    return A / (np.linalg.norm(A, 2) / norm)


def _exact_function(A, func):
    w, v = np.linalg.eigh(A)
    return v @ np.diag(func(w)) @ v.conj().T


class TestMatrixFunction:
    @pytest.mark.parametrize("func", [np.cos, np.sin, lambda x: np.exp(0.5 * x)])
    def test_converges_to_exact(self, func):
        A = _random_hermitian(3, 0)
        err = np.linalg.norm(matrix_function_chebyshev(A, func, 20) - _exact_function(A, func), 2)
        assert err < 1e-8

    def test_error_decreases_with_degree(self):
        A = _random_hermitian(3, 1)
        f = lambda x: np.exp(-2 * x**2)
        exact = _exact_function(A, f)
        errs = [np.linalg.norm(matrix_function_chebyshev(A, f, d) - exact, 2) for d in (4, 8, 16)]
        assert errs[-1] < errs[0]
        assert errs[-1] < 1e-6

    def test_identity_function(self):
        # f(x) = x -> f(A) = A.
        A = _random_hermitian(3, 2)
        assert np.allclose(matrix_function_chebyshev(A, lambda x: x, 5), A, atol=1e-9)

    def test_coefficients_reproduce_chebyshev(self):
        # f = T_2 -> coefficients [0, 0, 1].
        from numpy.polynomial import chebyshev as C

        c = chebyshev_coefficients(lambda x: C.chebval(x, [0, 0, 1]), 4)
        assert abs(c[2] - 1.0) < 1e-9
        assert abs(c[0]) < 1e-9 and abs(c[1]) < 1e-9


class TestHamiltonianSimulation:
    def test_matches_exact_evolution(self):
        H = _random_hermitian(4, 3)
        r = hamiltonian_simulation_qsvt(H, time=1.0, degree=24)
        assert r["error"] < 1e-6

    def test_result_is_unitary(self):
        H = _random_hermitian(3, 4)
        r = hamiltonian_simulation_qsvt(H, time=2.0, degree=30)
        assert r["unitarity_error"] < 1e-4

    def test_zero_time_is_identity(self):
        H = _random_hermitian(3, 5)
        r = hamiltonian_simulation_qsvt(H, time=0.0, degree=10)
        assert np.allclose(r["unitary"], np.eye(3), atol=1e-9)

    def test_longer_time_needs_higher_degree(self):
        H = _random_hermitian(3, 6)
        low = hamiltonian_simulation_qsvt(H, time=5.0, degree=8)["error"]
        high = hamiltonian_simulation_qsvt(H, time=5.0, degree=30)["error"]
        assert high < low


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
