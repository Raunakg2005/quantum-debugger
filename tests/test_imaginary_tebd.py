"""Tests for imaginary-time TEBD ground-state search on an MPS."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    imaginary_tebd_ground_state,
    tfim_mps_energy,
    hamiltonian_matrix,
    tfim_hamiltonian,
)
from quantum_debugger.mps import MPS


class TestGroundState:
    @pytest.mark.parametrize("n", [4, 6, 8])
    def test_converges_to_exact(self, n):
        r = imaginary_tebd_ground_state(n, 1.0, 1.0, dtau=0.05, steps=300, max_bond=16)
        assert r["error"] < 5e-3

    def test_variational_upper_bound(self):
        # A variational energy can never dip below the true ground energy.
        r = imaginary_tebd_ground_state(6, 1.0, 1.0, dtau=0.05, steps=300)
        assert r["energy"] >= r["exact_energy"] - 1e-6

    def test_finer_step_improves(self):
        e_coarse = imaginary_tebd_ground_state(6, 1.0, 1.0, dtau=0.2, steps=80)["error"]
        e_fine = imaginary_tebd_ground_state(6, 1.0, 1.0, dtau=0.03, steps=500)["error"]
        assert e_fine < e_coarse

    def test_deep_paramagnet(self):
        # Large field: ground state ~ |+...+>, energy ~ -h * n.
        n, h = 6, 5.0
        r = imaginary_tebd_ground_state(
            n, j_coupling=0.2, field=h, dtau=0.02, steps=400
        )
        assert r["error"] < 1e-2


class TestScale:
    def test_large_chain(self):
        # 24-qubit ground state -- beyond the dense diagonalizer.
        r = imaginary_tebd_ground_state(24, 1.0, 1.0, dtau=0.05, steps=150, max_bond=12)
        assert "exact_energy" not in r  # too big to diagonalize
        assert r["energy"] < 0  # ferromagnetic-ish, negative
        assert r["bond"] <= 12

    def test_extensive_energy(self):
        # Ground energy per site is roughly constant (extensivity).
        e12 = (
            imaginary_tebd_ground_state(12, 1.0, 1.0, dtau=0.05, steps=200)["energy"]
            / 12
        )
        e20 = (
            imaginary_tebd_ground_state(
                20, 1.0, 1.0, dtau=0.05, steps=200, max_bond=16
            )["energy"]
            / 20
        )
        assert abs(e12 - e20) < 0.1


class TestEnergyHelper:
    def test_product_state_energy(self):
        # |0...0>: <ZZ> = 1 per bond, <X> = 0, so E = -J*(n-1).
        m = MPS.zero_state(5)
        assert abs(tfim_mps_energy(m, j_coupling=1.0, field=1.0) - (-4.0)) < 1e-9

    def test_matches_dense_energy(self):
        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        H = hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 1.0), n)
        dense = np.real(psi.conj() @ H @ psi)
        assert abs(tfim_mps_energy(m, 1.0, 1.0) - dense) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
