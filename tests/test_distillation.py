"""Tests for BBPSSW entanglement distillation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    werner_state,
    bbpssw_distill,
    distillation_rounds,
)
from quantum_debugger.density_matrix import DensityMatrix


class TestWernerState:
    @pytest.mark.parametrize("F", [0.3, 0.5, 0.75, 1.0])
    def test_unit_trace_and_fidelity(self, F):
        rho = werner_state(F)
        assert abs(np.trace(rho).real - 1.0) < 1e-12
        phi_p = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        assert abs(float(np.real(phi_p.conj() @ rho @ phi_p)) - F) < 1e-12

    def test_entangled_iff_above_half(self):
        assert DensityMatrix(rho=werner_state(0.75)).negativity([0]) > 1e-6
        assert DensityMatrix(rho=werner_state(0.45)).negativity([0]) < 1e-12

    def test_pure_bell_at_f_one(self):
        phi_p = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        assert np.allclose(werner_state(1.0), np.outer(phi_p, phi_p.conj()))


class TestBBPSSW:
    @pytest.mark.parametrize("F", [0.55, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99])
    def test_circuit_matches_closed_form(self, F):
        r = bbpssw_distill(F)
        assert abs(r["fidelity"] - r["analytic"]) < 1e-9
        denom = F**2 + 2 * F * (1 - F) / 3 + 5 * ((1 - F) / 3) ** 2
        assert abs(r["success_probability"] - denom) < 1e-9

    @pytest.mark.parametrize("F", [0.55, 0.7, 0.9])
    def test_improves_above_threshold(self, F):
        assert bbpssw_distill(F)["improved"]

    def test_no_improvement_at_half(self):
        # F = 1/2 is the distillation threshold (fixed point).
        r = bbpssw_distill(0.5)
        assert abs(r["fidelity"] - 0.5) < 1e-9
        assert not r["improved"]

    def test_below_threshold_degrades(self):
        assert bbpssw_distill(0.4)["fidelity"] < 0.4

    def test_perfect_input_stays_perfect(self):
        r = bbpssw_distill(1.0)
        assert abs(r["fidelity"] - 1.0) < 1e-9
        assert abs(r["success_probability"] - 1.0) < 1e-9


class TestRounds:
    def test_monotone_trajectory(self):
        r = distillation_rounds(0.7, 0.99)
        assert r["reached"]
        fids = r["fidelities"]
        assert all(b > a for a, b in zip(fids, fids[1:]))
        assert fids[-1] >= 0.99

    def test_each_round_matches_single_circuit(self):
        # The trajectory's first step equals the verified one-round circuit.
        r = distillation_rounds(0.8, 0.99)
        assert abs(r["fidelities"][1] - bbpssw_distill(0.8)["fidelity"]) < 1e-12

    def test_below_threshold_unreachable(self):
        r = distillation_rounds(0.45, 0.9)
        assert not r["reached"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
