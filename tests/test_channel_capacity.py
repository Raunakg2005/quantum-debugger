"""Tests for channel coherent information and quantum capacity."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    coherent_information,
    amplitude_damping_capacity,
)
from quantum_debugger.density_matrix import amplitude_damping, depolarizing


def _h(x):
    if x <= 0 or x >= 1:
        return 0.0
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


class TestCoherentInformation:
    @pytest.mark.parametrize("g", [0.1, 0.3, 0.5, 0.7])
    @pytest.mark.parametrize("p", [0.2, 0.5, 0.8])
    def test_matches_ad_closed_form(self, g, p):
        got = coherent_information(amplitude_damping(g), np.diag([1 - p, p]))
        want = _h((1 - g) * p) - _h(g * p)
        assert abs(got - want) < 1e-9

    def test_perfect_channel_gives_input_entropy(self):
        # Identity channel: I_c = S(rho) (nothing leaks to the environment).
        eye = [np.eye(2, dtype=complex)]
        rho = np.diag([0.3, 0.7]).astype(complex)
        s_rho = -(0.3 * np.log2(0.3) + 0.7 * np.log2(0.7))
        assert abs(coherent_information(eye, rho) - s_rho) < 1e-9

    def test_antisymmetry_about_half(self):
        # AD channel: I_c(gamma) = -I_c(1 - gamma) for the same diagonal input.
        rho = np.diag([0.4, 0.6]).astype(complex)
        a = coherent_information(amplitude_damping(0.2), rho)
        b = coherent_information(amplitude_damping(0.8), rho)
        assert abs(a + b) < 1e-9

    def test_gamma_half_is_exactly_zero(self):
        rho = np.diag([0.5, 0.5]).astype(complex)
        assert abs(coherent_information(amplitude_damping(0.5), rho)) < 1e-9

    def test_full_depolarizing_destroys_everything(self):
        rho = np.diag([0.5, 0.5]).astype(complex)
        ic = coherent_information(depolarizing(1.0), rho)
        assert ic < -0.9  # output maximally mixed, environment huge


class TestADCapacity:
    def test_noiseless_capacity_is_one(self):
        r = amplitude_damping_capacity(0.0)
        assert abs(r["capacity"] - 1.0) < 1e-6
        assert abs(r["optimal_input"] - 0.5) < 1e-4

    @pytest.mark.parametrize("g", [0.5, 0.6, 0.9])
    def test_antidegradable_regime_is_zero(self, g):
        assert amplitude_damping_capacity(g)["capacity"] == 0.0

    def test_monotone_decreasing(self):
        caps = [amplitude_damping_capacity(g)["capacity"] for g in (0.0, 0.1, 0.25, 0.4)]
        assert all(b < a for a, b in zip(caps, caps[1:]))

    def test_capacity_matches_analytic_form(self):
        r = amplitude_damping_capacity(0.25)
        assert r["capacity"] > 0
        assert abs(r["capacity"] - r["analytic"]) < 1e-8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
