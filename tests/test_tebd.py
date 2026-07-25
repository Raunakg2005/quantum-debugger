"""Tests for TEBD (time-evolving block decimation on an MPS)."""

import numpy as np
import pytest
from scipy.linalg import expm

from quantum_debugger.algorithms import (
    tebd_tfim,
    tebd_magnetization,
    hamiltonian_matrix,
    tfim_hamiltonian,
)
from quantum_debugger.mps import MPS

_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class TestAccuracy:
    @pytest.mark.parametrize("n", [4, 5])
    def test_matches_exact_evolution(self, n):
        j, h, t = 1.0, 0.6, 1.0
        psi0 = np.zeros(2**n, dtype=complex)
        psi0[0] = 1
        m = MPS.from_statevector(psi0, max_bond=32)
        m = tebd_tfim(n, t, steps=200, j_coupling=j, field=h, max_bond=32, initial=m)
        H = hamiltonian_matrix(tfim_hamiltonian(n, h, j), n)  # tfim(n, field, coupling)
        exact = expm(-1j * H * t) @ psi0
        assert abs(np.vdot(exact, m.to_statevector())) ** 2 > 1 - 1e-4

    def test_zero_time_is_initial_state(self):
        m = tebd_tfim(4, time=0.0, steps=1)
        assert abs(m.expectation(_Z, 0) - 1.0) < 1e-9  # still |0000>

    def test_finer_trotter_improves_accuracy(self):
        n, j, h, t = 4, 1.0, 0.8, 1.0
        psi0 = np.zeros(2**n, dtype=complex)
        psi0[0] = 1
        H = hamiltonian_matrix(tfim_hamiltonian(n, h, j), n)
        exact = expm(-1j * H * t) @ psi0

        def err(steps):
            m = tebd_tfim(n, t, steps=steps, j_coupling=j, field=h, max_bond=32,
                          initial=MPS.from_statevector(psi0, max_bond=32))
            return 1 - abs(np.vdot(exact, m.to_statevector())) ** 2

        assert err(400) < err(20)


class TestScale:
    def test_large_chain_runs(self):
        # 30-qubit quench -- far beyond the dense state vector.
        r = tebd_magnetization(30, time=0.5, steps=30, field=0.5, max_bond=12)
        assert len(r["z_profile"]) == 30
        assert r["max_bond"] <= 12

    def test_bond_capped(self):
        m = tebd_tfim(20, time=1.0, steps=40, field=1.0, max_bond=8)
        assert m.max_bond_dimension() <= 8


class TestPhysics:
    def test_no_field_freezes_magnetization(self):
        # h = 0: H = -J ZZ is diagonal, |0...0> is an eigenstate -> <Z> stays 1.
        r = tebd_magnetization(6, time=2.0, steps=50, field=0.0, max_bond=4)
        assert all(abs(z - 1.0) < 1e-6 for z in r["z_profile"])

    def test_field_tilts_spins(self):
        # A transverse field rotates the spins away from +z.
        r = tebd_magnetization(6, time=1.0, steps=100, field=1.0, max_bond=16)
        assert r["mean_z"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
