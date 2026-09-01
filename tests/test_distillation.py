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


class TestNoisySwap:
    @pytest.mark.parametrize("F1,F2", [(1.0, 1.0), (0.9, 0.9), (0.8, 0.95), (0.7, 0.6)])
    def test_circuit_matches_closed_form(self, F1, F2):
        from quantum_debugger.algorithms import entanglement_swap_noisy

        r = entanglement_swap_noisy(F1, F2)
        assert abs(r["fidelity"] - r["analytic"]) < 1e-9
        assert abs(r["analytic"] - (F1 * F2 + (1 - F1) * (1 - F2) / 3)) < 1e-12

    def test_perfect_pairs_swap_perfectly(self):
        from quantum_debugger.algorithms import entanglement_swap_noisy

        assert abs(entanglement_swap_noisy(1.0, 1.0)["fidelity"] - 1.0) < 1e-9

    def test_swap_degrades_fidelity(self):
        from quantum_debugger.algorithms import entanglement_swap_noisy

        r = entanglement_swap_noisy(0.9, 0.9)
        assert r["fidelity"] < 0.9

    def test_two_entangled_pairs_can_swap_to_separable(self):
        # 0.7 and 0.6 are both entangled (> 1/2), but the swapped pair is not.
        from quantum_debugger.algorithms import entanglement_swap_noisy
        from quantum_debugger.algorithms import werner_state
        from quantum_debugger.density_matrix import DensityMatrix

        r = entanglement_swap_noisy(0.7, 0.6)
        assert r["fidelity"] < 0.5
        assert DensityMatrix(rho=werner_state(r["fidelity"])).negativity([0]) < 1e-12


class TestRepeaterChain:
    def test_single_link_is_input(self):
        from quantum_debugger.algorithms import repeater_chain

        assert abs(repeater_chain(0.9, 1)["fidelity"] - 0.9) < 1e-12

    def test_two_links_match_swap_circuit(self):
        from quantum_debugger.algorithms import repeater_chain, entanglement_swap_noisy

        chain = repeater_chain(0.9, 2)["fidelity"]
        circuit = entanglement_swap_noisy(0.9, 0.9)["fidelity"]
        assert abs(chain - circuit) < 1e-9

    def test_decays_toward_quarter(self):
        from quantum_debugger.algorithms import repeater_chain

        r = repeater_chain(0.9, 40)
        traj = r["trajectory"]
        assert all(b < a for a, b in zip(traj, traj[1:]))  # monotone decay
        assert abs(r["fidelity"] - 0.25) < 0.01  # -> fully mixed value

    def test_long_chain_loses_entanglement(self):
        from quantum_debugger.algorithms import repeater_chain

        assert repeater_chain(0.9, 2)["entangled"]
        assert not repeater_chain(0.9, 12)["entangled"]

    def test_distillation_rescues_chain(self):
        # The repeater story: swap degrades, distill restores.
        from quantum_debugger.algorithms import repeater_chain, bbpssw_distill

        f_after_swaps = repeater_chain(0.95, 3)["fidelity"]
        assert f_after_swaps < 0.95
        assert bbpssw_distill(f_after_swaps)["fidelity"] > f_after_swaps

    def test_invalid_links_rejected(self):
        from quantum_debugger.algorithms import repeater_chain

        with pytest.raises(ValueError):
            repeater_chain(0.9, 0)


class TestDEJMPS:
    @pytest.mark.parametrize("seed", range(6))
    def test_circuit_matches_recurrence(self, seed):
        from quantum_debugger.algorithms import dejmps_distill

        rng = np.random.default_rng(seed)
        lams = tuple(rng.dirichlet([2, 1, 1, 1]))
        r = dejmps_distill(lams)
        for got, want in zip(r["coefficients"], r["analytic"]):
            assert abs(got - want) < 1e-9
        l1, l2, l3, l4 = lams
        N = (l1 + l4) ** 2 + (l2 + l3) ** 2
        assert abs(r["success_probability"] - N) < 1e-9

    def test_werner_input_reduces_to_bbpssw(self):
        from quantum_debugger.algorithms import dejmps_distill, bbpssw_distill

        F = 0.75
        r = (1 - F) / 3
        d = dejmps_distill((F, r, r, r))
        b = bbpssw_distill(F)
        assert abs(d["fidelity"] - b["fidelity"]) < 1e-9
        assert abs(d["success_probability"] - b["success_probability"]) < 1e-9

    def test_beats_bbpssw_on_asymmetric_state(self):
        # Same total fidelity 0.7, but all the noise in one Bell component:
        # DEJMPS keeps the asymmetry and purifies much faster than BBPSSW
        # (which would first twirl the state to Werner form).
        from quantum_debugger.algorithms import dejmps_distill, bbpssw_distill

        d = dejmps_distill((0.7, 0.3, 0.0, 0.0))
        b = bbpssw_distill(0.7)
        assert d["fidelity"] > b["fidelity"] + 0.05  # 0.845 vs 0.735

    def test_rounds_reach_target(self):
        from quantum_debugger.algorithms import dejmps_rounds

        r = dejmps_rounds((0.7, 0.1, 0.1, 0.1), 0.999)
        assert r["reached"]
        fids = r["fidelities"]
        assert all(b > a for a, b in zip(fids, fids[1:]))

    def test_rounds_faster_than_bbpssw(self):
        from quantum_debugger.algorithms import dejmps_rounds, distillation_rounds

        target = 0.99
        dej = dejmps_rounds((0.7, 0.3, 0.0, 0.0), target)
        bbp = distillation_rounds(0.7, target)
        assert dej["reached"] and bbp["reached"]
        assert dej["rounds"] <= bbp["rounds"]

    def test_below_threshold_not_reached(self):
        from quantum_debugger.algorithms import dejmps_rounds

        r = dejmps_rounds((0.25, 0.25, 0.25, 0.25), 0.9)
        assert not r["reached"]

    def test_bell_diagonal_state_valid(self):
        from quantum_debugger.algorithms import bell_diagonal_state
        from quantum_debugger.density_matrix import DensityMatrix

        rho = bell_diagonal_state(0.4, 0.3, 0.2, 0.1)
        assert abs(np.trace(rho).real - 1.0) < 1e-12
        assert np.all(np.linalg.eigvalsh(rho) > -1e-12)
        # Pure Phi+ at (1,0,0,0).
        phi_p = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        assert np.allclose(
            bell_diagonal_state(1, 0, 0, 0), np.outer(phi_p, phi_p.conj())
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
