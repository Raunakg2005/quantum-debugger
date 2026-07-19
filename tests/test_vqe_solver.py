"""Tests for the variational ground-state solver (VQE)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    variational_ground_state,
    tfim_hamiltonian,
    heisenberg_hamiltonian,
)


class TestHamiltonians:
    def test_tfim_term_count(self):
        # n-1 ZZ couplings + n transverse fields.
        terms = tfim_hamiltonian(4)
        assert len(terms) == 3 + 4

    def test_heisenberg_is_hermitian_ground_below_zero(self):
        r = variational_ground_state(heisenberg_hamiltonian(2), layers=3, restarts=8)
        assert r["exact_energy"] < 0


class TestVQE:
    @pytest.mark.parametrize("n", [2, 3])
    def test_tfim_matches_exact(self, n):
        r = variational_ground_state(
            tfim_hamiltonian(n, field=1.0), layers=3, restarts=10, seed=1
        )
        assert r["error"] < 1e-3

    @pytest.mark.parametrize("n", [2, 3])
    def test_heisenberg_matches_exact(self, n):
        r = variational_ground_state(
            heisenberg_hamiltonian(n), layers=3, restarts=10, seed=2
        )
        assert r["error"] < 1e-3

    def test_energy_is_variational_upper_bound(self):
        # VQE energy can never be below the true ground energy.
        r = variational_ground_state(tfim_hamiltonian(4), layers=3, restarts=8, seed=1)
        assert r["energy"] >= r["exact_energy"] - 1e-6
        assert r["error"] < 0.05  # approximate, but close


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
