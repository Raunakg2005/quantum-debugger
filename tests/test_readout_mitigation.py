"""Tests for readout error mitigation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    assignment_matrix,
    apply_readout_noise,
    mitigate_readout,
    mitigate_expectation,
)


class TestAssignmentMatrix:
    def test_columns_are_distributions(self):
        A = assignment_matrix(2, 0.05, 0.08)
        assert np.allclose(A.sum(axis=0), 1.0)  # each column sums to 1

    def test_no_noise_is_identity(self):
        assert np.allclose(assignment_matrix(3, 0.0, 0.0), np.eye(8))

    def test_shape(self):
        assert assignment_matrix(3, 0.1, 0.1).shape == (8, 8)


class TestMitigation:
    def test_recovers_true_distribution(self):
        n = 3
        true = np.zeros(2**n)
        true[0] = true[7] = 0.5  # GHZ populations
        measured = apply_readout_noise(true, 0.05, 0.08)
        corrected = mitigate_readout(measured, 0.05, 0.08)
        assert np.allclose(corrected, true, atol=1e-9)

    def test_correction_beats_no_correction(self):
        rng = np.random.default_rng(0)
        n = 3
        true = rng.random(2**n)
        true /= true.sum()
        measured = apply_readout_noise(true, 0.07, 0.1)
        corrected = mitigate_readout(measured, 0.07, 0.1)
        assert np.max(np.abs(corrected - true)) < np.max(np.abs(measured - true))

    def test_output_is_valid_distribution(self):
        rng = np.random.default_rng(1)
        measured = rng.random(8)
        measured /= measured.sum()
        corrected = mitigate_readout(measured, 0.1, 0.05)
        assert abs(corrected.sum() - 1.0) < 1e-9
        assert np.all(corrected >= -1e-12)

    def test_no_noise_leaves_distribution_unchanged(self):
        rng = np.random.default_rng(2)
        p = rng.random(4)
        p /= p.sum()
        assert np.allclose(mitigate_readout(p, 0.0, 0.0), p, atol=1e-12)


class TestExpectationMitigation:
    def test_recovers_true_expectation(self):
        # <Z0 Z1 Z2> parity for a GHZ-like population.
        n = 3
        true = np.zeros(2**n)
        true[0] = true[7] = 0.5
        parity = np.array([(-1) ** bin(i).count("1") for i in range(2**n)], dtype=float)
        measured = apply_readout_noise(true, 0.06, 0.09)
        r = mitigate_expectation(measured, parity, 0.06, 0.09)
        true_exp = float(parity @ true)
        assert abs(r["mitigated"] - true_exp) < 1e-9
        assert abs(r["raw"] - true_exp) > abs(r["mitigated"] - true_exp)  # raw is worse

    def test_correction_field(self):
        n = 2
        true = np.array([1.0, 0, 0, 0])  # |00>, <Z0> = 1
        z0 = np.array([1, -1, 1, -1], dtype=float)  # <Z0> diagonal (little-endian)
        measured = apply_readout_noise(true, 0.1, 0.1)
        r = mitigate_expectation(measured, z0, 0.1, 0.1)
        assert abs(r["correction"] - (r["mitigated"] - r["raw"])) < 1e-12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
