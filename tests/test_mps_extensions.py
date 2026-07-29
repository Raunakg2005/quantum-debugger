"""Tests for MPS extension methods (construction, linear algebra, readout)."""

import numpy as np
import pytest

from quantum_debugger.mps import MPS
from quantum_debugger.core.gates import GateLibrary

_Z = np.diag([1, -1]).astype(complex)
_X = GateLibrary.X
_H = GateLibrary.H
_CNOT = GateLibrary.CNOT


def _ghz(n):
    m = MPS.zero_state(n)
    m.apply_single(_H, 0)
    for q in range(n - 1):
        m.apply_two(_CNOT, q)
    return m


class TestConstruction:
    def test_from_product(self):
        m = MPS.from_product([[1, 0], [0, 1], [1, 0], [0, 1]])  # |0101>
        assert np.argmax(np.abs(m.to_statevector())) == 0b1010  # little-endian
        assert m.max_bond_dimension() == 1

    def test_random_normalized(self):
        m = MPS.random(6, bond=4, seed=1)
        assert abs(m.norm() - 1.0) < 1e-9
        assert m.max_bond_dimension() <= 4

    def test_random_reproducible(self):
        a = MPS.random(4, bond=3, seed=2).to_statevector()
        b = MPS.random(4, bond=3, seed=2).to_statevector()
        assert np.allclose(a, b)


class TestLinearAlgebra:
    def test_add_matches_dense(self):
        rng = np.random.default_rng(0)
        n = 4
        a = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); a /= np.linalg.norm(a)
        b = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); b /= np.linalg.norm(b)
        s = MPS.from_statevector(a).add(MPS.from_statevector(b))
        expected = (a + b) / np.linalg.norm(a + b)
        assert abs(np.vdot(expected, s.to_statevector())) ** 2 > 1 - 1e-9

    def test_add_bond_dims_grow(self):
        a = _ghz(4)
        s = a.add(_ghz(4), normalize=True)
        assert s.max_bond_dimension() >= 2

    def test_compress_high_fidelity(self):
        # A GHZ compresses to bond 2 losslessly.
        g = _ghz(6)
        c = g.compress(max_bond=2)
        assert abs(g.fidelity(c) - 1.0) < 1e-9

    def test_mismatched_add_rejected(self):
        with pytest.raises(ValueError):
            MPS.zero_state(3).add(MPS.zero_state(4))


class TestReadout:
    def test_magnetization_profile(self):
        assert all(abs(z) < 1e-9 for z in _ghz(4).magnetization_profile(_Z))

    def test_correlation_profile(self):
        # GHZ: <Z_0 Z_j> = 1 for all j.
        prof = _ghz(5).correlation_profile(_Z, _Z, ref=0)
        assert all(abs(c - 1.0) < 1e-9 for c in prof)

    def test_variance_zero_on_eigenstate(self):
        from quantum_debugger.algorithms import tfim_hamiltonian, hamiltonian_matrix

        n = 4
        terms = tfim_hamiltonian(n, 1.0, 1.0)
        H = hamiltonian_matrix(terms, n)
        gs = MPS.from_statevector(np.linalg.eigh(H)[1][:, 0], max_bond=16)
        assert abs(gs.variance(terms)) < 1e-8

    def test_variance_positive_off_eigenstate(self):
        from quantum_debugger.algorithms import tfim_hamiltonian

        assert MPS.zero_state(4).variance(tfim_hamiltonian(4, 1.0, 1.0)) > 1e-6

    def test_renyi_matches_von_neumann_for_flat(self):
        # GHZ has a flat 2-value Schmidt spectrum, so all Renyi orders give 1 bit.
        g = _ghz(4)
        assert abs(g.renyi_entropy(1, 2.0) - 1.0) < 1e-9
        assert abs(g.renyi_entropy(1, 1.0) - 1.0) < 1e-9

    def test_renyi_bounded_by_von_neumann(self):
        rng = np.random.default_rng(3)
        psi = rng.normal(size=2**5) + 1j * rng.normal(size=2**5)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=32)
        # Renyi-2 <= von Neumann (Renyi is non-increasing in alpha).
        assert m.renyi_entropy(2, 2.0) <= m.renyi_entropy(2, 1.0) + 1e-9

class TestOperatorsAndRDM:
    def test_apply_mpo_matches_dense(self):
        from quantum_debugger.mpo import tfim_mpo, mpo_to_matrix

        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=64)
        Hpsi = m.apply_mpo(tfim_mpo(n, 1.0, 0.7)).to_statevector()
        assert np.allclose(Hpsi, mpo_to_matrix(tfim_mpo(n, 1.0, 0.7)) @ psi, atol=1e-9)

    def test_expectation_mpo_matches_energy(self):
        from quantum_debugger.mpo import tfim_mpo
        from quantum_debugger.algorithms import tfim_hamiltonian

        rng = np.random.default_rng(1)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        assert abs(m.expectation_mpo(tfim_mpo(n, 1.0, 0.7))
                   - m.energy(tfim_hamiltonian(n, 0.7, 1.0))) < 1e-9

    def test_single_qubit_rdm_matches_dense(self):
        from quantum_debugger.density_matrix import DensityMatrix

        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=64)
        dm = DensityMatrix(state_vector=psi)
        for q in range(n):
            assert np.allclose(m.single_qubit_rdm(q), dm.partial_trace([q]).rho, atol=1e-9)

    def test_rdm_is_valid_density_matrix(self):
        rdm = _ghz(4).single_qubit_rdm(0)
        assert abs(np.trace(rdm).real - 1.0) < 1e-9
        assert np.linalg.eigvalsh(rdm).min() > -1e-9

    def test_entanglement_spectrum_bell(self):
        b = MPS.zero_state(2)
        b.apply_single(_H, 0)
        b.apply_two(_CNOT, 0)
        assert np.allclose(b.entanglement_spectrum(0), [1 / np.sqrt(2)] * 2, atol=1e-9)

    def test_spectrum_squares_sum_to_one(self):
        rng = np.random.default_rng(2)
        psi = rng.normal(size=2**5) + 1j * rng.normal(size=2**5); psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=32)
        assert abs(np.sum(m.entanglement_spectrum(2) ** 2) - 1.0) < 1e-9



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
