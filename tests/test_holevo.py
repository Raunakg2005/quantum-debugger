"""Tests for the Holevo bound and accessible information."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    holevo_bound,
    accessible_information,
    holevo_gap,
)


def _h(x):
    if x <= 0 or x >= 1:
        return 0.0
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


class TestHolevoBound:
    def test_orthogonal_pure_states_reach_one_bit(self):
        chi = holevo_bound([0.5, 0.5], [np.array([1, 0]), np.array([0, 1])])
        assert abs(chi - 1.0) < 1e-12

    def test_identical_states_carry_nothing(self):
        s = np.array([1, 1]) / np.sqrt(2)
        assert holevo_bound([0.5, 0.5], [s, s]) < 1e-12

    def test_bb84_ensemble_chi_is_one(self):
        states = [
            np.array([1, 0]),
            np.array([0, 1]),
            np.array([1, 1]) / np.sqrt(2),
            np.array([1, -1]) / np.sqrt(2),
        ]
        assert abs(holevo_bound([0.25] * 4, states) - 1.0) < 1e-9

    def test_qubit_never_exceeds_one_bit(self):
        rng = np.random.default_rng(0)
        states = []
        for _ in range(5):
            v = rng.normal(size=2) + 1j * rng.normal(size=2)
            states.append(v / np.linalg.norm(v))
        chi = holevo_bound([0.2] * 5, states)
        assert chi <= 1.0 + 1e-9


class TestAccessibleInformation:
    @pytest.mark.parametrize("theta", [np.pi / 3, np.pi / 4, np.pi / 8])
    def test_two_state_closed_forms(self, theta):
        r = holevo_gap(theta)
        assert abs(r["chi"] - r["chi_analytic"]) < 1e-6
        assert abs(r["accessible"] - r["accessible_analytic"]) < 1e-6

    def test_orthogonal_states_no_gap(self):
        r = holevo_gap(np.pi / 2)
        assert abs(r["chi"] - 1.0) < 1e-9
        assert abs(r["accessible"] - 1.0) < 1e-6
        assert r["gap"] < 1e-6

    @pytest.mark.parametrize("theta", [np.pi / 3, np.pi / 4])
    def test_gap_is_strictly_positive(self, theta):
        # Non-orthogonal states: information exists that no measurement extracts.
        r = holevo_gap(theta)
        assert r["gap"] > 0.1

    def test_bb84_accessible_is_half(self):
        # The eavesdropper's fundamental limit: chi = 1 but only 1/2 bit reachable.
        states = [
            np.array([1, 0]),
            np.array([0, 1]),
            np.array([1, 1]) / np.sqrt(2),
            np.array([1, -1]) / np.sqrt(2),
        ]
        acc = accessible_information([0.25] * 4, states)
        assert abs(acc - 0.5) < 1e-6

    def test_never_exceeds_holevo(self):
        rng = np.random.default_rng(1)
        states = []
        for _ in range(3):
            v = rng.normal(size=2) + 1j * rng.normal(size=2)
            states.append(v / np.linalg.norm(v))
        probs = [0.5, 0.3, 0.2]
        assert accessible_information(probs, states) <= holevo_bound(probs, states) + 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
