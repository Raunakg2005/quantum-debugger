"""Tests for decoherence-free subspaces under collective dephasing."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    collective_dephasing,
    dfs_encode,
    dfs_protection,
)
from quantum_debugger.density_matrix import DensityMatrix


class TestCollectiveDephasing:
    @pytest.mark.parametrize("sigma", [0.2, 0.5, 0.8, 1.5])
    def test_bare_qubit_matches_closed_form(self, sigma):
        plus = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        out = collective_dephasing(plus, sigma)
        assert abs(2 * abs(out.rho[0, 1]) - np.exp(-(sigma**2) / 2)) < 1e-9

    def test_trace_preserved(self):
        dm = DensityMatrix(state_vector=np.array([1, 1j, -1, 1], dtype=complex) / 2)
        out = collective_dephasing(dm, 0.7)
        assert abs(np.trace(out.rho).real - 1.0) < 1e-9

    def test_zero_noise_is_identity(self):
        dm = DensityMatrix(state_vector=np.array([0.6, 0.8j], dtype=complex))
        out = collective_dephasing(dm, 0.0)
        assert np.allclose(out.rho, dm.rho, atol=1e-12)

    def test_diagonal_states_unaffected(self):
        dm = DensityMatrix(rho=np.diag([0.4, 0.1, 0.3, 0.2]).astype(complex))
        out = collective_dephasing(dm, 2.0)
        assert np.allclose(out.rho, dm.rho, atol=1e-9)


class TestDFS:
    @pytest.mark.parametrize("sigma", [0.3, 0.8, 2.0, 5.0])
    def test_dfs_immune_at_any_strength(self, sigma):
        r = dfs_protection(sigma, 0.6, 0.8j)
        assert abs(r["dfs_fidelity"] - 1.0) < 1e-9

    @pytest.mark.parametrize("sigma", [0.3, 0.8, 1.2])
    def test_bare_and_antidfs_decay_as_predicted(self, sigma):
        r = dfs_protection(sigma)
        assert abs(r["bare_coherence"] - r["bare_analytic"]) < 1e-9
        assert abs(r["antidfs_coherence"] - r["antidfs_analytic"]) < 1e-9

    def test_antidfs_decays_faster_than_bare(self):
        r = dfs_protection(0.8)
        assert r["antidfs_coherence"] < r["bare_coherence"] < 1.0

    def test_encoded_state_normalized(self):
        sv = dfs_encode(3.0, 4.0)
        assert abs(np.linalg.norm(sv) - 1.0) < 1e-12
        assert abs(sv[0b01] - 0.6) < 1e-12 and abs(sv[0b10] - 0.8) < 1e-12

    def test_dfs_preserves_superposition_not_just_populations(self):
        # The DFS state keeps its off-diagonal coherence exactly.
        sigma = 1.0
        sv = dfs_encode(1.0, 1.0)
        out = collective_dephasing(DensityMatrix(state_vector=sv), sigma)
        assert abs(abs(out.rho[0b01, 0b10]) - 0.5) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
