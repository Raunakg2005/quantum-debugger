"""Tests for the Kitaev chain (topological superconductor)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    kitaev_chain_hamiltonian,
    kitaev_ground_degeneracy,
)


class TestHamiltonian:
    def test_hermitian(self):
        H = kitaev_chain_hamiltonian(5, mu=0.5, t=1.0, delta=0.8)
        assert np.allclose(H, H.conj().T)

    def test_parity_symmetry(self):
        # Fermion parity P = prod Z_j commutes with the Kitaev Hamiltonian.
        n = 4
        H = kitaev_chain_hamiltonian(n, mu=0.7, t=1.0, delta=1.0)
        P = np.array([[1]], dtype=complex)
        for _ in range(n):
            P = np.kron(np.array([[1, 0], [0, -1]], dtype=complex), P)
        assert np.allclose(H @ P - P @ H, 0, atol=1e-10)


class TestTopologicalPhase:
    def test_degenerate_ground_in_topological_phase(self):
        r = kitaev_ground_degeneracy(6, mu=0.0, t=1.0, delta=1.0)
        assert r["topological"]
        assert r["splitting"] < 1e-9          # essentially exact degeneracy
        assert r["nearly_degenerate"]

    def test_unique_ground_in_trivial_phase(self):
        r = kitaev_ground_degeneracy(6, mu=3.0, t=1.0, delta=1.0)
        assert not r["topological"]
        assert r["splitting"] > 0.1           # large gap, unique ground
        assert not r["nearly_degenerate"]

    def test_splitting_decays_exponentially_with_length(self):
        # Majorana modes localize: the ground splitting halves per added site.
        splittings = [
            kitaev_ground_degeneracy(n, mu=1.0, t=1.0, delta=1.0)["splitting"]
            for n in (4, 5, 6, 7, 8)
        ]
        ratios = [b / a for a, b in zip(splittings, splittings[1:])]
        assert all(r < 0.7 for r in ratios)   # each step shrinks it markedly
        assert splittings[-1] < splittings[0]

    def test_bulk_gap_stays_open_in_topological_phase(self):
        # The degeneracy is between two states well below the bulk excitation gap.
        r = kitaev_ground_degeneracy(7, mu=1.0, t=1.0, delta=1.0)
        assert r["bulk_gap"] > 10 * r["splitting"]

    def test_transition_at_mu_equals_2t(self):
        # Crossing |mu| = 2t flips the topological flag.
        assert kitaev_ground_degeneracy(5, mu=1.9, t=1.0)["topological"]
        assert not kitaev_ground_degeneracy(5, mu=2.1, t=1.0)["topological"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
