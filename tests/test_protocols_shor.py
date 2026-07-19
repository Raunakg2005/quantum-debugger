"""Tests for teleportation, superdense coding, and Shor's algorithm."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    teleport,
    superdense_coding,
    entanglement_swap,
    period_finding,
    shor_factor,
)


class TestTeleportation:
    @pytest.mark.parametrize("seed", [0, 1, 2, 3])
    def test_teleports_random_state(self, seed):
        rng = np.random.default_rng(seed)
        psi = rng.standard_normal(2) + 1j * rng.standard_normal(2)
        result = teleport(psi)
        assert result["fidelity"] > 0.999
        assert result["measurement"][0] in (0, 1)

    def test_teleports_basis_states(self):
        assert teleport([1, 0])["fidelity"] > 0.999
        assert teleport([0, 1])["fidelity"] > 0.999


class TestSuperdenseCoding:
    @pytest.mark.parametrize("bits", [(0, 0), (0, 1), (1, 0), (1, 1)])
    def test_all_messages(self, bits):
        result = superdense_coding(bits)
        assert result["decoded"] == bits
        assert result["success"]


class TestEntanglementSwap:
    @pytest.mark.parametrize("seed", range(8))
    def test_outer_qubits_become_bell_pair(self, seed):
        result = entanglement_swap(seed=seed)
        assert result["fidelity"] > 0.999
        assert result["measurement"][0] in (0, 1)


class TestShor:
    def test_period_finding_mod15(self):
        assert period_finding(7, 15, n_count=8)["period"] == 4
        assert period_finding(2, 15, n_count=8)["period"] == 4

    def test_factor_15(self):
        result = shor_factor(15, a=7, n_count=8)
        assert set(result["factors"]) == {3, 5}

    def test_factor_21(self):
        result = shor_factor(21, a=2, n_count=9)
        assert set(result["factors"]) == {3, 7}

    def test_even_number(self):
        result = shor_factor(8)
        assert result["factors"][0] * result["factors"][1] == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
