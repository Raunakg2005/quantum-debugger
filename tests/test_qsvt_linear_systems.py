"""Tests for QSVT matrix inversion and linear systems."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    matrix_inverse_qsvt,
    solve_linear_system_qsvt,
)


def _random_pd(d, seed, lo=0.2, hi=0.9):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(d, d))
    A = M @ M.T
    A = A / np.linalg.norm(A, 2)
    return lo * np.eye(d) + (hi - lo) * A  # positive definite, spectrum roughly [lo, hi]


class TestMatrixInverse:
    def test_converges_to_inverse(self):
        A = _random_pd(4, 0)
        err = np.linalg.norm(matrix_inverse_qsvt(A, degree=40) - np.linalg.inv(A), 2)
        assert err < 1e-6

    def test_error_decreases_with_degree(self):
        A = _random_pd(4, 1)
        Ainv = np.linalg.inv(A)
        errs = [np.linalg.norm(matrix_inverse_qsvt(A, d) - Ainv, 2) for d in (10, 20, 40)]
        assert errs[-1] < errs[0]
        assert errs[-1] < 1e-6

    def test_inverse_times_matrix_is_identity(self):
        A = _random_pd(3, 2)
        prod = matrix_inverse_qsvt(A, degree=40) @ A
        assert np.allclose(prod, np.eye(3), atol=1e-5)


class TestLinearSystem:
    def test_solves_system(self):
        rng = np.random.default_rng(3)
        A = _random_pd(4, 3)
        b = rng.normal(size=4)
        r = solve_linear_system_qsvt(A, b, degree=40)
        assert r["error"] < 1e-5
        assert r["fidelity"] > 1 - 1e-8

    def test_matches_numpy_solve(self):
        rng = np.random.default_rng(4)
        A = _random_pd(3, 4)
        b = rng.normal(size=3) + 1j * rng.normal(size=3)
        r = solve_linear_system_qsvt(A, b, degree=40)
        assert np.allclose(r["solution"], np.linalg.solve(A, b), atol=1e-5)

    def test_residual_small(self):
        # A x ~= b.
        rng = np.random.default_rng(5)
        A = _random_pd(4, 5)
        b = rng.normal(size=4)
        x = solve_linear_system_qsvt(A, b, degree=40)["solution"]
        assert np.linalg.norm(A @ x - b) < 1e-4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
