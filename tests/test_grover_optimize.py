"""Tests for Grover adaptive minimization (Durr-Hoyer)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import grover_minimize


class TestGroverMinimize:
    def test_quadratic_minimum(self):
        # (x - 11)^2 is minimized at x = 11 on 4 bits.
        r = grover_minimize(lambda x: (x - 11) ** 2, 4, seed=1)
        assert r["argmin"] == 11
        assert r["found_optimum"]

    @pytest.mark.parametrize("seed", range(10))
    def test_random_cost_finds_optimum(self, seed):
        rng = np.random.default_rng(seed)
        vals = rng.permutation(16)
        r = grover_minimize(lambda x: int(vals[x]), 4, seed=seed)
        assert r["found_optimum"]
        assert r["min_value"] == r["exact_min"]

    def test_never_worse_than_exact(self):
        rng = np.random.default_rng(3)
        vals = rng.permutation(32)
        r = grover_minimize(lambda x: int(vals[x]), 5, seed=7)
        # Can never beat the true minimum, and reports the exact one it found.
        assert r["min_value"] >= r["exact_min"]
        assert r["min_value"] == r["exact_min"]

    def test_5bit(self):
        r = grover_minimize(lambda x: (x - 20) ** 2, 5, seed=2)
        assert r["argmin"] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
