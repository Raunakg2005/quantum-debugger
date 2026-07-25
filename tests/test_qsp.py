"""Tests for Quantum Signal Processing."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    signal_operator,
    qsp_unitary,
    qsp_response,
    chebyshev_via_qsp,
)


class TestSignalOperator:
    def test_unitary(self):
        for x in (-0.9, -0.3, 0.0, 0.5, 1.0):
            W = signal_operator(x)
            assert np.allclose(W.conj().T @ W, np.eye(2), atol=1e-12)

    def test_endpoints(self):
        assert np.allclose(signal_operator(1.0), np.eye(2))


class TestChebyshev:
    @pytest.mark.parametrize("d", [1, 2, 3, 4, 5, 8])
    def test_zero_phases_give_chebyshev(self, d):
        xs = np.linspace(-1, 1, 50)
        expected = np.cos(d * np.arccos(xs))
        assert np.allclose(chebyshev_via_qsp(d, xs), expected, atol=1e-9)

    def test_t2_is_2x2_minus_1(self):
        xs = np.linspace(-1, 1, 25)
        assert np.allclose(chebyshev_via_qsp(2, xs), 2 * xs**2 - 1, atol=1e-9)


class TestPolynomialProperties:
    def test_parity_matches_degree(self):
        # A degree-d QSP polynomial has parity d mod 2.
        phases_odd = [0.3, 0.5, -0.2, 0.7]      # d = 3 -> odd
        phases_even = [0.3, 0.5, -0.2, 0.7, 0.1]  # d = 4 -> even
        xs = np.linspace(0.05, 0.95, 20)
        p_odd = qsp_response(phases_odd, xs)
        p_odd_neg = qsp_response(phases_odd, -xs)
        assert np.allclose(p_odd, -p_odd_neg, atol=1e-9)     # odd
        p_even = qsp_response(phases_even, xs)
        p_even_neg = qsp_response(phases_even, -xs)
        assert np.allclose(p_even, p_even_neg, atol=1e-9)    # even

    def test_bounded_by_one(self):
        rng = np.random.default_rng(0)
        phases = rng.uniform(-np.pi, np.pi, 6)
        xs = np.linspace(-1, 1, 100)
        assert np.all(np.abs(qsp_response(phases, xs)) <= 1 + 1e-9)

    def test_unitary_at_each_x(self):
        phases = [0.2, -0.5, 0.8]
        for x in np.linspace(-1, 1, 10):
            U = qsp_unitary(phases, x)
            assert np.allclose(U.conj().T @ U, np.eye(2), atol=1e-10)

    def test_global_phase_only(self):
        # A single phase (d = 0) gives the constant polynomial cos(2 phi_0)? Actually
        # <0|Rz(phi)|0> = e^{i phi}, real part cos(phi).
        xs = np.linspace(-1, 1, 5)
        assert np.allclose(qsp_response([0.7], xs), np.cos(0.7), atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
