"""Tests for the Horodecki CHSH criterion and the entangled-but-local window."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    chsh_maximum,
    chsh_maximum_optimized,
    werner_nonlocality,
    werner_state,
    bell_diagonal_state,
)


class TestHorodeckiCriterion:
    def test_bell_state_reaches_tsirelson(self):
        phi_p = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(phi_p, phi_p.conj())
        assert abs(chsh_maximum(rho) - 2 * np.sqrt(2)) < 1e-9

    @pytest.mark.parametrize("F", [0.6, 0.8, 0.9, 1.0])
    def test_werner_closed_form(self, F):
        expected = 2 * np.sqrt(2) * abs(4 * F - 1) / 3
        assert abs(chsh_maximum(werner_state(F)) - expected) < 1e-9

    def test_product_state_obeys_classical_bound(self):
        sv = np.array([1, 0, 0, 0], dtype=complex)  # |00>
        rho = np.outer(sv, sv.conj())
        assert chsh_maximum(rho) <= 2 + 1e-9

    @pytest.mark.parametrize("seed", range(3))
    def test_matches_direct_optimization(self, seed):
        rng = np.random.default_rng(seed)
        lams = rng.dirichlet([2, 1, 1, 1])
        rho = bell_diagonal_state(*lams)
        closed = chsh_maximum(rho)
        direct = chsh_maximum_optimized(rho, restarts=10, seed=seed)
        assert abs(closed - direct) < 1e-5

    def test_threshold_is_exactly_two(self):
        F_star = (1 + 3 / np.sqrt(2)) / 4
        assert abs(chsh_maximum(werner_state(F_star)) - 2.0) < 1e-9


class TestEntangledButLocal:
    def test_below_half_neither(self):
        r = werner_nonlocality(0.4)
        assert not r["entangled"] and not r["nonlocal"]

    def test_window_entangled_but_local(self):
        # 1/2 < F < 0.7803: entangled, yet no CHSH violation possible.
        r = werner_nonlocality(0.65)
        assert r["entangled"]
        assert not r["nonlocal"]
        assert r["entangled_but_local"]
        assert r["chsh"] < 2

    def test_above_threshold_nonlocal(self):
        r = werner_nonlocality(0.9)
        assert r["entangled"] and r["nonlocal"]
        assert not r["entangled_but_local"]

    def test_pure_bell_maximal(self):
        r = werner_nonlocality(1.0)
        assert abs(r["chsh"] - 2 * np.sqrt(2)) < 1e-9
        assert abs(r["negativity"] - 0.5) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
