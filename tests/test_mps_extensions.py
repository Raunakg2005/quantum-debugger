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
        a = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        a /= np.linalg.norm(a)
        b = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        b /= np.linalg.norm(b)
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
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=64)
        Hpsi = m.apply_mpo(tfim_mpo(n, 1.0, 0.7)).to_statevector()
        assert np.allclose(Hpsi, mpo_to_matrix(tfim_mpo(n, 1.0, 0.7)) @ psi, atol=1e-9)

    def test_expectation_mpo_matches_energy(self):
        from quantum_debugger.mpo import tfim_mpo
        from quantum_debugger.algorithms import tfim_hamiltonian

        rng = np.random.default_rng(1)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        assert (
            abs(
                m.expectation_mpo(tfim_mpo(n, 1.0, 0.7))
                - m.energy(tfim_hamiltonian(n, 0.7, 1.0))
            )
            < 1e-9
        )

    def test_single_qubit_rdm_matches_dense(self):
        from quantum_debugger.density_matrix import DensityMatrix

        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=64)
        dm = DensityMatrix(state_vector=psi)
        for q in range(n):
            assert np.allclose(
                m.single_qubit_rdm(q), dm.partial_trace([q]).rho, atol=1e-9
            )

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
        psi = rng.normal(size=2**5) + 1j * rng.normal(size=2**5)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=32)
        assert abs(np.sum(m.entanglement_spectrum(2) ** 2) - 1.0) < 1e-9


class TestCondensedMatterObservables:
    def test_heisenberg_mpo_matches_dense(self):
        from quantum_debugger.mpo import heisenberg_mpo, mpo_to_matrix
        from quantum_debugger.algorithms import (
            hamiltonian_matrix,
            heisenberg_hamiltonian,
        )

        M = mpo_to_matrix(heisenberg_mpo(4, 1.0))
        H = hamiltonian_matrix(heisenberg_hamiltonian(4), 4)
        assert np.allclose(M, H, atol=1e-9)

    def test_bloch_vector_ghz_is_zero(self):
        assert np.allclose(_ghz(4).bloch_vector(0), [0, 0, 0], atol=1e-9)

    def test_bloch_vector_plus_state(self):
        m = MPS.from_product([[1, 1]])  # |+>
        assert np.allclose(m.bloch_vector(0), [1, 0, 0], atol=1e-9)

    def test_purity_profile_ghz(self):
        assert all(abs(p - 0.5) < 1e-9 for p in _ghz(4).purity_profile())

    def test_purity_profile_product(self):
        assert all(abs(p - 1.0) < 1e-9 for p in MPS.zero_state(4).purity_profile())

    def test_schmidt_gap_product_is_one(self):
        assert abs(MPS.zero_state(4).schmidt_gap(1) - 1.0) < 1e-9

    def test_schmidt_gap_ghz_is_zero(self):
        assert abs(_ghz(4).schmidt_gap(1)) < 1e-9

    def test_total_magnetization(self):
        Z = np.diag([1, -1]).astype(complex)
        m = MPS.zero_state(5)  # |00000>: each <Z> = 1
        assert abs(m.total_magnetization(Z) - 5.0) < 1e-9

    def test_structure_factor_ferromagnet(self):
        # |0...0>: fully correlated, S(k=0) = n.
        Z = np.diag([1, -1]).astype(complex)
        assert abs(MPS.zero_state(4).structure_factor(Z, 0.0) - 4.0) < 1e-9

    def test_structure_factor_matches_dense(self):
        from quantum_debugger.density_matrix import DensityMatrix

        Z = np.diag([1, -1]).astype(complex)
        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        k = 0.7

        # dense reference
        def zop(i):
            o = np.array([[1]], dtype=complex)
            for q in range(n):
                o = np.kron(Z if q == i else np.eye(2), o)
            return o

        s = (
            sum(
                np.exp(1j * k * (i - j)) * (psi.conj() @ zop(i) @ zop(j) @ psi)
                for i in range(n)
                for j in range(n)
            )
            / n
        )
        assert abs(m.structure_factor(Z, k) - np.real(s)) < 1e-9


class TestAmplitudesAndBasis:
    def test_amplitude_matches_dense(self):
        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        for idx in range(2**n):
            bits = [(idx >> q) & 1 for q in range(n)]
            assert abs(m.amplitude(bits) - psi[idx]) < 1e-9

    def test_probabilities_sum_to_one(self):
        rng = np.random.default_rng(1)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        total = sum(
            m.probability([(i >> q) & 1 for q in range(n)]) for i in range(2**n)
        )
        assert abs(total - 1.0) < 1e-9

    def test_from_bitstring(self):
        b = MPS.from_bitstring([1, 0, 1])
        assert np.argmax(np.abs(b.to_statevector())) == 0b101
        assert b.max_bond_dimension() == 1

    def test_most_probable_ghz(self):
        r = _ghz(4).most_probable(300, seed=0)
        assert r["bitstring"] in ("0000", "1111")
        assert abs(r["probability"] - 0.5) < 1e-9

    def test_amplitude_of_basis_state(self):
        b = MPS.from_bitstring([0, 1, 1, 0])
        assert abs(b.amplitude([0, 1, 1, 0]) - 1.0) < 1e-9
        assert abs(b.amplitude([0, 0, 0, 0])) < 1e-12


class TestTwoQubitCorrelations:
    def test_two_qubit_rdm_matches_dense(self):
        from quantum_debugger.density_matrix import DensityMatrix

        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        dm = DensityMatrix(state_vector=psi)
        for a in range(n):
            for b in range(n):
                if a != b:
                    assert np.allclose(
                        m.two_qubit_rdm(a, b), dm.partial_trace([a, b]).rho, atol=1e-9
                    )

    def test_bell_mutual_information(self):
        b = MPS.zero_state(2)
        b.apply_single(_H, 0)
        b.apply_two(_CNOT, 0)
        assert abs(b.mutual_information(0, 1) - 2.0) < 1e-9

    def test_bell_concurrence(self):
        b = MPS.zero_state(2)
        b.apply_single(_H, 0)
        b.apply_two(_CNOT, 0)
        assert abs(b.concurrence(0, 1) - 1.0) < 1e-9

    def test_product_no_correlation(self):
        m = MPS.zero_state(3)
        assert abs(m.mutual_information(0, 1)) < 1e-9
        assert abs(m.concurrence(0, 1)) < 1e-9

    def test_rdm_symmetric_in_arguments(self):
        rng = np.random.default_rng(2)
        psi = rng.normal(size=2**4) + 1j * rng.normal(size=2**4)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        assert np.allclose(m.two_qubit_rdm(1, 3), m.two_qubit_rdm(3, 1))


class TestTruncationAndNorm:
    def test_ghz_no_truncation_error_at_bond_two(self):
        g = _ghz(6)
        assert g.truncation_error(2) < 1e-9

    def test_truncation_error_decreases_with_bond(self):
        m = MPS.random(6, bond=8, seed=1)
        assert m.truncation_error(4) < m.truncation_error(2)

    def test_truncation_error_in_unit_interval(self):
        m = MPS.random(5, bond=6, seed=2)
        e = m.truncation_error(2)
        assert 0 <= e <= 1

    def test_normalize(self):
        u = MPS.random(4, bond=4, seed=2)
        u.tensors[0] = u.tensors[0] * 3.7
        assert abs(u.normalize().norm() - 1.0) < 1e-9

    def test_normalize_preserves_direction(self):
        rng = np.random.default_rng(3)
        psi = rng.normal(size=2**4) + 1j * rng.normal(size=2**4)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        m.tensors[0] = m.tensors[0] * 2.5
        m.normalize()
        assert abs(np.vdot(psi, m.to_statevector())) ** 2 > 1 - 1e-9


class TestTwoSiteExpectation:
    def test_matches_correlation(self):
        Z = np.diag([1, -1]).astype(complex)
        ZZ = np.kron(Z, Z)
        g = _ghz(4)
        assert abs(g.two_site_expectation(ZZ, 0, 1) - g.correlation(Z, 0, Z, 1)) < 1e-9

    def test_matches_dense(self):
        from scipy.stats import unitary_group
        from quantum_debugger.core.quantum_state import apply_gate_tensor

        rng = np.random.default_rng(0)
        psi = rng.normal(size=16) + 1j * rng.normal(size=16)
        psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        Op = unitary_group.rvs(4, random_state=1)
        Op = (Op + Op.conj().T) / 2
        dense = np.vdot(psi, apply_gate_tensor(np, psi, Op, [0, 1], 4))
        assert abs(m.two_site_expectation(Op, 0, 1) - np.real(dense)) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
