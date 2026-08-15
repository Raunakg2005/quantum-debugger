"""Tests for quantum state discrimination (Helstrom + unambiguous)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    helstrom_bound,
    helstrom_measurement,
    unambiguous_discrimination,
)


def _pair(theta):
    a = np.array([1, 0], dtype=complex)
    b = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
    return a, b


class TestHelstrom:
    @pytest.mark.parametrize("theta", [np.pi / 2, np.pi / 3, np.pi / 6])
    def test_pure_state_closed_form(self, theta):
        a, b = _pair(theta)
        s = abs(np.cos(theta))
        expected = (1 - np.sqrt(1 - s**2)) / 2
        assert abs(helstrom_bound(0.5, a, 0.5, b) - expected) < 1e-12

    def test_orthogonal_states_perfectly_distinguishable(self):
        a, b = _pair(np.pi / 2)
        assert helstrom_bound(0.5, a, 0.5, b) < 1e-12

    def test_identical_states_error_is_smaller_prior(self):
        a = np.array([1, 1], dtype=complex) / np.sqrt(2)
        assert abs(helstrom_bound(0.3, a, 0.7, a) - 0.3) < 1e-12

    @pytest.mark.parametrize("p0", [0.2, 0.5, 0.8])
    def test_unequal_priors_closed_form(self, p0):
        # Pure states: P_err = (1 - sqrt(1 - 4 p0 p1 s^2)) / 2.
        theta = np.pi / 4
        a, b = _pair(theta)
        p1 = 1 - p0
        s = abs(np.cos(theta))
        expected = (1 - np.sqrt(1 - 4 * p0 * p1 * s**2)) / 2
        assert abs(helstrom_bound(p0, a, p1, b) - expected) < 1e-12

    @pytest.mark.parametrize("theta", [np.pi / 3, np.pi / 5])
    def test_explicit_measurement_achieves_bound(self, theta):
        a, b = _pair(theta)
        r = helstrom_measurement(0.5, a, 0.5, b)
        assert abs(r["error_probability"] - r["bound"]) < 1e-12

    def test_mixed_states_supported(self):
        rho0 = np.diag([0.8, 0.2]).astype(complex)
        rho1 = np.diag([0.3, 0.7]).astype(complex)
        r = helstrom_measurement(0.5, rho0, 0.5, rho1)
        assert abs(r["error_probability"] - r["bound"]) < 1e-12
        assert 0 < r["bound"] < 0.5


class TestUnambiguous:
    @pytest.mark.parametrize("theta", [np.pi / 3, np.pi / 4, np.pi / 8])
    def test_idp_bound_achieved_with_zero_error(self, theta):
        a, b = _pair(theta)
        r = unambiguous_discrimination(a, b)
        assert r["povm_valid"]
        assert abs(r["success_probability"] - r["analytic"]) < 1e-12
        assert r["error_probability"] < 1e-12  # NEVER wrong
        assert abs(r["success_probability"] + r["inconclusive_probability"] - 1) < 1e-12

    def test_orthogonal_states_always_succeed(self):
        a, b = _pair(np.pi / 2)
        r = unambiguous_discrimination(a, b)
        assert abs(r["success_probability"] - 1.0) < 1e-12

    def test_usd_pays_for_certainty(self):
        # USD success < Helstrom success: zero errors cost conclusiveness.
        theta = np.pi / 4
        a, b = _pair(theta)
        usd_succ = unambiguous_discrimination(a, b)["success_probability"]
        hel_succ = 1 - helstrom_bound(0.5, a, 0.5, b)
        assert usd_succ < hel_succ

    def test_non_qubit_rejected(self):
        with pytest.raises(ValueError):
            unambiguous_discrimination(np.ones(4), np.ones(4))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
