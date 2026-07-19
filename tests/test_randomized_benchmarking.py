"""Tests for single-qubit randomized benchmarking."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    randomized_benchmarking,
    single_qubit_clifford_group,
)


class TestCliffordGroup:
    def test_group_has_24_elements(self):
        assert len(single_qubit_clifford_group()) == 24

    def test_all_unitary(self):
        for U in single_qubit_clifford_group():
            assert np.allclose(U @ U.conj().T, np.eye(2), atol=1e-9)


class TestRB:
    def test_zero_noise_survives(self):
        r = randomized_benchmarking(depolarizing=0.0, shots=20, seed=1)
        assert all(s > 0.999 for s in r["survival"])
        assert r["average_error"] < 0.01

    def test_decay_matches_depolarizing(self):
        # For per-gate depolarizing lambda, RB gives p ~ 1 - lambda.
        r = randomized_benchmarking(depolarizing=0.03, shots=80, seed=2)
        assert np.isclose(r["p"], 0.97, atol=0.02)
        assert np.isclose(r["average_error"], 0.015, atol=0.01)

    def test_error_increases_with_noise(self):
        errs = [
            randomized_benchmarking(depolarizing=lam, shots=60, seed=3)["average_error"]
            for lam in (0.01, 0.04, 0.09)
        ]
        assert errs[0] < errs[1] < errs[2]

    def test_survival_decreases_with_length(self):
        r = randomized_benchmarking(depolarizing=0.05, shots=80, seed=4)
        s = r["survival"]
        # Longer sequences accumulate more error -> lower survival (allow noise).
        assert s[-1] < s[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
