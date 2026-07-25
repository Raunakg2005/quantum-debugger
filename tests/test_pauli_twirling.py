"""Tests for Pauli twirling (noise tailoring)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import pauli_twirl, coherent_error_kraus
from quantum_debugger.density_matrix import depolarizing, amplitude_damping


class TestTwirledIsPauliChannel:
    def test_coherent_error_becomes_pauli(self):
        r = pauli_twirl(coherent_error_kraus(0.3, "X"))
        assert r["is_pauli_channel"]

    def test_amplitude_damping_becomes_pauli(self):
        r = pauli_twirl(amplitude_damping(0.2))
        assert r["is_pauli_channel"]

    def test_probabilities_sum_to_one(self):
        r = pauli_twirl(coherent_error_kraus(0.5, "Y"))
        assert abs(sum(r["pauli_probabilities"].values()) - 1.0) < 1e-9


class TestRxTwirl:
    def test_matches_analytic_pauli_channel(self):
        # Twirling Rx(theta) gives cos^2(theta/2) I + sin^2(theta/2) X.
        theta = 0.3
        r = pauli_twirl(coherent_error_kraus(theta, "X"))
        p = r["pauli_probabilities"]
        assert abs(p["I"] - np.cos(theta / 2) ** 2) < 1e-9
        assert abs(p["X"] - np.sin(theta / 2) ** 2) < 1e-9
        assert abs(p["Y"]) < 1e-9 and abs(p["Z"]) < 1e-9

    def test_rz_twirls_to_z_channel(self):
        theta = 0.4
        r = pauli_twirl(coherent_error_kraus(theta, "Z"))
        p = r["pauli_probabilities"]
        assert abs(p["Z"] - np.sin(theta / 2) ** 2) < 1e-9


class TestFidelityPreserved:
    def test_average_fidelity_unchanged(self):
        # Twirling preserves the average gate fidelity of the original channel.
        from quantum_debugger.density_matrix import average_gate_fidelity

        kraus = coherent_error_kraus(0.6, "X")
        original = average_gate_fidelity(kraus)
        twirled = pauli_twirl(kraus)["average_fidelity"]
        assert abs(original - twirled) < 1e-9

    def test_depolarizing_is_fixed_point(self):
        # Depolarizing is already a Pauli channel; twirling leaves it unchanged.
        p = 0.2
        r = pauli_twirl(depolarizing(p))
        probs = r["pauli_probabilities"]
        assert abs(probs["I"] - (1 - 3 * p / 4)) < 1e-9
        assert abs(probs["X"] - p / 4) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
