"""Tests for Schmidt decomposition and the area law."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    schmidt_decomposition,
    truncation_fidelity,
    area_law_compressibility,
    hamiltonian_matrix,
    tfim_hamiltonian,
)
from quantum_debugger.density_matrix import DensityMatrix


class TestSchmidtDecomposition:
    def test_bell_two_equal_values(self):
        d = schmidt_decomposition(
            np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2), [0]
        )
        assert np.allclose(d["schmidt_values"], [1 / np.sqrt(2)] * 2, atol=1e-9)
        assert d["schmidt_rank"] == 2
        assert abs(d["entropy"] - 1.0) < 1e-9

    def test_product_state_rank_one(self):
        d = schmidt_decomposition(np.array([1, 0, 0, 0], dtype=complex), [0])
        assert d["schmidt_rank"] == 1
        assert abs(d["entropy"]) < 1e-12

    def test_values_normalized(self):
        rng = np.random.default_rng(0)
        v = rng.normal(size=16) + 1j * rng.normal(size=16)
        d = schmidt_decomposition(v, [0, 1])
        assert abs(np.sum(d["schmidt_values"] ** 2) - 1.0) < 1e-9

    @pytest.mark.parametrize("seed", range(4))
    def test_entropy_matches_density_matrix(self, seed):
        rng = np.random.default_rng(seed)
        v = rng.normal(size=64) + 1j * rng.normal(size=64)
        v = v / np.linalg.norm(v)
        region = [0, 1, 2]
        s_schmidt = schmidt_decomposition(v, region)["entropy"]
        s_dm = DensityMatrix(state_vector=v).entanglement_entropy(region)
        assert abs(s_schmidt - s_dm) < 1e-9

    def test_values_descending(self):
        rng = np.random.default_rng(1)
        v = rng.normal(size=16) + 1j * rng.normal(size=16)
        s = schmidt_decomposition(v, [0, 1])["schmidt_values"]
        assert np.all(np.diff(s) <= 1e-12)


class TestAreaLaw:
    def _tfim_ground(self, n):
        H = hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 1.0), n)
        return np.linalg.eigh(H)[1][:, 0]

    def test_gapped_ground_state_compresses(self):
        # A gapped 1D ground state keeps almost all weight in a few Schmidt values.
        gs = self._tfim_ground(6)
        r = area_law_compressibility(gs, [0, 1, 2], bond_dim=3)
        assert r["compressible"]
        assert r["truncation_fidelity"] > 0.99

    def test_random_state_does_not_compress(self):
        rng = np.random.default_rng(2)
        v = rng.normal(size=64) + 1j * rng.normal(size=64)
        r = area_law_compressibility(v, [0, 1, 2], bond_dim=2)
        assert not r["compressible"]
        assert r["truncation_fidelity"] < 0.9

    def test_full_bond_dim_is_exact(self):
        gs = self._tfim_ground(6)
        assert abs(truncation_fidelity(gs, [0, 1, 2], bond_dim=8) - 1.0) < 1e-9

    def test_truncation_fidelity_monotone(self):
        gs = self._tfim_ground(6)
        fids = [truncation_fidelity(gs, [0, 1, 2], bond_dim=k) for k in (1, 2, 4, 8)]
        assert all(b >= a - 1e-12 for a, b in zip(fids, fids[1:]))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
