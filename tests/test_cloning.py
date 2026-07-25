"""Tests for the Buzek-Hillery optimal universal cloner."""

import numpy as np
import pytest

from quantum_debugger.algorithms import universal_clone
from quantum_debugger.algorithms.cloning import _bh_isometry


class TestUniversalCloner:
    def test_isometry_valid(self):
        V = _bh_isometry()
        assert np.allclose(V.conj().T @ V, np.eye(2), atol=1e-12)

    @pytest.mark.parametrize("a,b", [(1, 0), (0, 1), (1, 1), (1, 1j), (0.6, 0.8j)])
    def test_both_clones_five_sixths(self, a, b):
        r = universal_clone(a, b)
        assert abs(r["clone1_fidelity"] - 5 / 6) < 1e-12
        assert abs(r["clone2_fidelity"] - 5 / 6) < 1e-12

    @pytest.mark.parametrize("seed", range(5))
    def test_universality_random_states(self, seed):
        # The SAME fidelity for every input -- no state is cloned better.
        rng = np.random.default_rng(seed)
        a, b = rng.normal(size=2) + 1j * rng.normal(size=2)
        r = universal_clone(a, b)
        assert abs(r["clone1_fidelity"] - 5 / 6) < 1e-12

    def test_clones_are_identical(self):
        assert universal_clone(0.6, 0.8j)["clones_identical"]

    def test_no_cloning_enforced(self):
        # 5/6 < 1: perfect cloning is impossible.
        r = universal_clone(1, 1)
        assert r["clone1_fidelity"] < 1.0

    def test_beats_classical_strategy(self):
        r = universal_clone(1, 1j)
        assert r["clone1_fidelity"] > r["classical_limit"] + 0.15  # 5/6 vs 2/3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
