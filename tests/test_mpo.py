"""Tests for matrix product operators."""

import numpy as np
import pytest

from quantum_debugger.mpo import tfim_mpo, mpo_expectation, mpo_to_matrix
from quantum_debugger.mps import MPS
from quantum_debugger.core.gates import GateLibrary
from quantum_debugger.algorithms import hamiltonian_matrix, tfim_hamiltonian


class TestMPOMatrix:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_matches_dense_hamiltonian(self, n):
        M = mpo_to_matrix(tfim_mpo(n, 1.0, 0.7))
        H = hamiltonian_matrix(tfim_hamiltonian(n, 0.7, 1.0), n)
        assert np.allclose(M, H, atol=1e-9)

    def test_bond_dimension_three(self):
        mpo = tfim_mpo(5, 1.0, 1.0)
        assert mpo[2].shape == (3, 2, 2, 3)  # bulk tensor


class TestMPOExpectation:
    def test_matches_mps_energy(self):
        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        mval = mpo_expectation(m, tfim_mpo(n, 1.0, 0.7))
        assert abs(mval - m.energy(tfim_hamiltonian(n, 0.7, 1.0))) < 1e-9

    def test_matches_dense_expectation(self):
        rng = np.random.default_rng(1)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        H = hamiltonian_matrix(tfim_hamiltonian(n, 0.7, 1.0), n)
        m = MPS.from_statevector(psi, max_bond=16)
        assert abs(mpo_expectation(m, tfim_mpo(n, 1.0, 0.7)) - np.real(psi.conj() @ H @ psi)) < 1e-9

    def test_large_ghz(self):
        n = 30
        m = MPS.zero_state(n)
        m.apply_single(GateLibrary.H, 0)
        for q in range(n - 1):
            m.apply_two(GateLibrary.CNOT, q)
        # <ZZ> = 1 per bond, <X> = 0 -> E = -J(n-1).
        assert abs(mpo_expectation(m, tfim_mpo(n, 1.0, 0.0)) - (-(n - 1))) < 1e-9

    def test_product_state_energy(self):
        m = MPS.zero_state(5)  # |00000>: <ZZ>=1 per bond, <X>=0
        assert abs(mpo_expectation(m, tfim_mpo(5, 1.0, 1.0)) - (-4.0)) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
