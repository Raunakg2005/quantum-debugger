"""Tests for Quantum Singular Value Transformation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    qsvt_transform,
    qsvt_scalar_response,
    chebyshev_of_matrix,
)


def _random_hermitian(d, seed, norm=0.7):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    A = (M + M.conj().T) / 2
    return A / (np.linalg.norm(A, 2) / norm)


class TestEigenvalueTransformation:
    @pytest.mark.parametrize("phases", [
        [0, 0, 0, 0],
        [0.3, 0.5, -0.2, 0.7],
        [0.5, -0.3, 0.8],
        [0.1, 0.2, 0.3, 0.4, 0.5],
    ])
    def test_applies_scalar_function_eigenvaluewise(self, phases):
        A = _random_hermitian(3, len(phases))
        w, v = np.linalg.eigh(A)
        g = np.array([qsvt_scalar_response(phases, lam) for lam in w])
        classical = v @ np.diag(g) @ v.conj().T
        assert np.allclose(qsvt_transform(A, phases), classical, atol=1e-8)

    def test_zero_phases_give_chebyshev(self):
        A = _random_hermitian(3, 0)
        for d in (1, 2, 3, 4):
            phases = [0.0] * (d + 1)
            assert np.allclose(qsvt_transform(A, phases), chebyshev_of_matrix(A, d), atol=1e-8)

    def test_output_commutes_with_input(self):
        # A function of A commutes with A.
        A = _random_hermitian(3, 2)
        P = qsvt_transform(A, [0.3, 0.5, -0.2, 0.7])
        assert np.allclose(P @ A, A @ P, atol=1e-8)

    def test_diagonal_matrix(self):
        A = np.diag([0.3, -0.5, 0.6]).astype(complex)
        phases = [0.2, -0.4, 0.6]
        out = qsvt_transform(A, phases)
        expected = np.diag([qsvt_scalar_response(phases, x) for x in (0.3, -0.5, 0.6)])
        assert np.allclose(out, expected, atol=1e-8)


class TestScalarResponse:
    def test_bounded(self):
        rng = np.random.default_rng(0)
        phases = rng.uniform(-np.pi, np.pi, 5)
        for x in np.linspace(-0.99, 0.99, 50):
            assert abs(qsvt_scalar_response(phases, x)) <= 1 + 1e-9

    def test_zero_phase_chebyshev_scalar(self):
        for d in (1, 2, 3, 5):
            phases = [0.0] * (d + 1)
            for x in np.linspace(-0.9, 0.9, 20):
                assert abs(qsvt_scalar_response(phases, x).real - np.cos(d * np.arccos(x))) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
