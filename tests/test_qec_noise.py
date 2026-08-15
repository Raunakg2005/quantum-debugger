"""Tests for QEC under continuous noise (density-matrix, exact)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    bit_flip_code_noisy,
    phase_flip_code_noisy,
    syndrome_extraction_cycle,
    repetition_code_logical_error,
)


class TestBitFlipCodeNoisy:
    @pytest.mark.parametrize("p", [0.0, 0.05, 0.1, 0.2, 0.3, 0.49])
    def test_matches_closed_form(self, p):
        # Logical |0_L> codeword: recovered fidelity = (1-p)^3 + 3p(1-p)^2 exactly.
        r = bit_flip_code_noisy(p, alpha=1.0, beta=0.0)
        assert abs(r["corrected"] - r["analytic"]) < 1e-7

    @pytest.mark.parametrize("p", [0.01, 0.1, 0.3])
    def test_superposition_at_least_as_protected(self, p):
        # For |+_L> a logical-X failure maps the state to itself, so it is protected
        # at least as well as the success probability (here, perfectly: F = 1).
        r = bit_flip_code_noisy(p, alpha=1.0, beta=1.0)
        assert r["corrected"] >= r["analytic"] - 1e-9
        assert abs(r["corrected"] - 1.0) < 1e-7

    @pytest.mark.parametrize("p", [0.05, 0.1, 0.2, 0.4])
    def test_beats_unencoded_below_threshold(self, p):
        r = bit_flip_code_noisy(p)
        assert r["corrected"] > r["uncorrected"]  # encoding helps for p < 1/2

    def test_worse_above_threshold(self):
        # Above p = 1/2 the code hurts: majority vote amplifies the error.
        r = bit_flip_code_noisy(0.6)
        assert r["corrected"] < r["uncorrected"]

    def test_perfect_channel_is_lossless(self):
        r = bit_flip_code_noisy(0.0)
        assert abs(r["corrected"] - 1.0) < 1e-12


class TestPhaseFlipCodeNoisy:
    @pytest.mark.parametrize("p", [0.0, 0.05, 0.15, 0.3, 0.45])
    def test_matches_closed_form(self, p):
        r = phase_flip_code_noisy(p, alpha=1.0, beta=0.0)
        assert abs(r["corrected"] - r["analytic"]) < 1e-7


class TestRepetitionCodeLogicalError:
    def test_distance_3_matches_formula(self):
        p = 0.1
        expected = 3 * p**2 * (1 - p) + p**3
        assert abs(repetition_code_logical_error(p, 3) - expected) < 1e-12

    def test_larger_distance_suppresses_error_below_threshold(self):
        p = 0.1
        e3 = repetition_code_logical_error(p, 3)
        e5 = repetition_code_logical_error(p, 5)
        e7 = repetition_code_logical_error(p, 7)
        assert e7 < e5 < e3  # more qubits -> lower logical error below threshold

    def test_at_threshold_is_half(self):
        assert abs(repetition_code_logical_error(0.5, 3) - 0.5) < 1e-12
        assert abs(repetition_code_logical_error(0.5, 5) - 0.5) < 1e-12

    def test_even_distance_rejected(self):
        with pytest.raises(ValueError):
            repetition_code_logical_error(0.1, 4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestSyndromeExtractionCircuit:
    @pytest.mark.parametrize("p", [0.0, 0.05, 0.1, 0.2, 0.3, 0.4])
    def test_circuit_matches_ideal_recovery(self, p):
        # The physical measured-ancilla circuit reproduces (1-p)^3 + 3p(1-p)^2.
        r = syndrome_extraction_cycle(p)
        assert abs(r["corrected"] - r["analytic"]) < 1e-9

    def test_agrees_with_abstract_recovery(self):
        from quantum_debugger.algorithms import bit_flip_code_noisy

        for p in (0.1, 0.25):
            circ = syndrome_extraction_cycle(p)["corrected"]
            abstract = bit_flip_code_noisy(p)["corrected"]
            assert abs(circ - abstract) < 1e-9

    def test_superposition_codeword_protected(self):
        r = syndrome_extraction_cycle(0.15, alpha=1.0, beta=1.0)
        assert abs(r["corrected"] - 1.0) < 1e-7  # |+_L> logical-X-invariant

    def test_perfect_channel_lossless(self):
        assert abs(syndrome_extraction_cycle(0.0)["corrected"] - 1.0) < 1e-12


class TestRepeatedCycles:
    @pytest.mark.parametrize("p", [0.02, 0.05, 0.1])
    def test_matches_closed_form_every_cycle(self, p):
        from quantum_debugger.algorithms import repeated_qec_cycles

        r = repeated_qec_cycles(p, 8)
        for sim, ana in zip(r["fidelities"], r["analytic"]):
            assert abs(sim - ana) < 1e-9
        assert abs(r["logical_flip_probability"] - (3 * p**2 - 2 * p**3)) < 1e-12

    def test_monotone_decay_toward_half(self):
        from quantum_debugger.algorithms import repeated_qec_cycles

        fids = repeated_qec_cycles(0.1, 12)["fidelities"]
        assert all(b < a for a, b in zip(fids, fids[1:]))
        assert fids[-1] > 0.5  # decays toward 1/2, never below

    def test_lifetime_gain_scales_inverse_p(self):
        from quantum_debugger.algorithms import repeated_qec_cycles

        gain = repeated_qec_cycles(0.01, 1)["lifetime_gain"]
        assert 25 < gain < 40  # ~ 1/(3p) ~ 33

    def test_plus_logical_immune(self):
        from quantum_debugger.algorithms import repeated_qec_cycles

        r = repeated_qec_cycles(0.1, 5, alpha=1.0, beta=1.0)
        assert all(abs(f - 1.0) < 1e-9 for f in r["fidelities"])

    def test_gain_above_one_for_all_p_below_half(self):
        # q = 3p^2 - 2p^3 < p iff (2p-1)(p-1) > 0, i.e. for EVERY p < 1/2;
        # the crossover is exactly at the p = 1/2 threshold (q = 1/2 there).
        from quantum_debugger.algorithms import repeated_qec_cycles

        assert repeated_qec_cycles(0.05, 1)["lifetime_gain"] > 1
        assert repeated_qec_cycles(0.45, 1)["lifetime_gain"] > 1
        q_at_half = repeated_qec_cycles(0.5, 1)["logical_flip_probability"]
        assert abs(q_at_half - 0.5) < 1e-12  # fixed point: no help, no harm
