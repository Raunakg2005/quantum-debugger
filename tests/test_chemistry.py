"""
Tests for the 1.4.0 quantum-chemistry suite: fermion-to-qubit mappings, molecular
Hamiltonians, particle-conserving ansätze, RDMs, qubit tapering, measurement grouping,
and excited-state solvers. Everything is checked against exact diagonalization or a
closed form.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.fermion_mappings import (
    jordan_wigner_annihilation, parity_annihilation, bravyi_kitaev_annihilation,
    satisfies_car, pauli_weight)
from quantum_debugger.algorithms.molecular_hamiltonian import (
    molecular_hamiltonian, number_operator, fci_energy, hartree_fock_energy,
    hubbard_dimer_hamiltonian)
from quantum_debugger.algorithms.chemistry_ansatze import (
    hartree_fock_state, givens_rotation, uccsd_operator,
    conserves_particle_number, is_unitary, apply_ansatz)
from quantum_debugger.algorithms.rdm import (
    one_particle_rdm, two_particle_rdm, energy_from_rdm, natural_orbital_occupations)
from quantum_debugger.algorithms.qubit_tapering import (
    z2_symmetry_generators, is_symmetry, spectrum_is_union_of_sectors)
from quantum_debugger.algorithms.measurement_grouping import (
    qubit_wise_commuting_groups, commuting_groups, is_valid_grouping, measurement_reduction)
from quantum_debugger.algorithms.excited_states import (
    nearest_eigenstate, subspace_energies, ssvqe_cost, excited_spectrum_by_deflation)


def _dimer_ground_state(t=1.0, U=4.0):
    H = hubbard_dimer_hamiltonian(t, U)
    N = number_operator(4)
    occ = np.rint(np.real(np.diag(N))).astype(int)
    sector = np.where(occ == 2)[0]
    _, v = np.linalg.eigh(H[np.ix_(sector, sector)])
    gs = np.zeros(16, dtype=complex); gs[sector] = v[:, 0]
    return H, gs


class TestFermionMappings:
    def test_car(self):
        for fn in (jordan_wigner_annihilation, parity_annihilation, bravyi_kitaev_annihilation):
            assert satisfies_car([fn(j, 4) for j in range(4)])

    def test_same_spectrum(self):
        def H(fn):
            a = [fn(j, 4) for j in range(4)]
            return sum(-(a[p].conj().T @ a[(p + 1) % 4] + a[(p + 1) % 4].conj().T @ a[p])
                       for p in range(4))
        s_jw = np.linalg.eigvalsh(H(jordan_wigner_annihilation))
        s_par = np.linalg.eigvalsh(H(parity_annihilation))
        s_bk = np.linalg.eigvalsh(H(bravyi_kitaev_annihilation))
        assert np.allclose(s_jw, s_par) and np.allclose(s_jw, s_bk)

    def test_bk_reduces_hopping_weight(self):
        jw = [jordan_wigner_annihilation(j, 4) for j in range(4)]
        bk = [bravyi_kitaev_annihilation(j, 4) for j in range(4)]
        hop = lambda a: pauli_weight(a[0].conj().T @ a[3] + a[3].conj().T @ a[0])
        assert pauli_weight(bk[0].conj().T @ bk[3] + bk[3].conj().T @ bk[0]) <= hop(jw)


class TestMolecularHamiltonian:
    def test_hubbard_dimer_closed_form(self):
        t, U = 1.0, 4.0
        exact = (U - np.sqrt(U**2 + 16 * t**2)) / 2
        for m in ("jw", "parity", "bk"):
            E = fci_energy(hubbard_dimer_hamiltonian(t, U, m), 2, 4, m)
            assert abs(E - exact) < 1e-9

    def test_non_interacting(self):
        rng = np.random.default_rng(0)
        A = rng.normal(size=(4, 4)); h1 = (A + A.T) / 2
        H = molecular_hamiltonian(h1)
        orb = np.sort(np.linalg.eigvalsh(h1))
        for k in (1, 2, 3):
            assert abs(fci_energy(H, k, 4) - sum(orb[:k])) < 1e-9

    def test_number_conservation(self):
        H = hubbard_dimer_hamiltonian(1.0, 4.0); N = number_operator(4)
        assert np.allclose(H @ N - N @ H, 0, atol=1e-9)

    def test_hf_upper_bounds_fci(self):
        t, U = 1.0, 4.0
        h1 = np.zeros((4, 4)); h1[0, 2] = h1[2, 0] = -t; h1[1, 3] = h1[3, 1] = -t
        h2 = np.zeros((4, 4, 4, 4)); h2[0, 1, 1, 0] = U; h2[2, 3, 3, 2] = U
        e_hf = hartree_fock_energy(h1, h2, 2)
        e_fci = (U - np.sqrt(U**2 + 16 * t**2)) / 2
        assert e_hf >= e_fci - 1e-9


class TestAnsatze:
    def test_hf_state_particle_number(self):
        hf = hartree_fock_state(4, 2); N = number_operator(4)
        assert abs(np.real(np.vdot(hf, N @ hf)) - 2) < 1e-9

    def test_givens_conserving_unitary(self):
        G = givens_rotation(0.4, 0, 2, 4)
        assert is_unitary(G) and conserves_particle_number(G, 4)

    def test_uccsd_conserving_unitary(self):
        U = uccsd_operator([(0.3, 2, 0)], [(0.5, 3, 2, 1, 0)], 4)
        assert is_unitary(U) and conserves_particle_number(U, 4)
        psi = apply_ansatz(hartree_fock_state(4, 2), U)
        assert abs(np.real(np.vdot(psi, number_operator(4) @ psi)) - 2) < 1e-9


class TestRDM:
    def test_one_rdm_trace_and_hermitian(self):
        _, gs = _dimer_ground_state()
        D = one_particle_rdm(gs)
        assert abs(np.real(np.trace(D)) - 2) < 1e-9
        assert np.allclose(D, D.conj().T)

    def test_natural_occupations_in_range(self):
        _, gs = _dimer_ground_state()
        occ = natural_orbital_occupations(gs)
        assert np.all(occ >= -1e-9) and np.all(occ <= 1 + 1e-9)

    def test_energy_from_rdm(self):
        H, gs = _dimer_ground_state()
        t, U = 1.0, 4.0
        h1 = np.zeros((4, 4)); h1[0, 2] = h1[2, 0] = -t; h1[1, 3] = h1[3, 1] = -t
        h2 = np.zeros((4, 4, 4, 4)); h2[0, 1, 1, 0] = U; h2[2, 3, 3, 2] = U
        E = energy_from_rdm(one_particle_rdm(gs), two_particle_rdm(gs), h1, h2)
        assert abs(E - np.real(np.vdot(gs, H @ gs))) < 1e-9


class TestTapering:
    def test_symmetries_genuine(self):
        H = hubbard_dimer_hamiltonian(1.0, 4.0)
        gens = z2_symmetry_generators(H)
        assert len(gens) >= 1
        assert all(is_symmetry(H, g) for g in gens)

    def test_spectrum_preserved(self):
        H = hubbard_dimer_hamiltonian(1.0, 4.0)
        for g in z2_symmetry_generators(H):
            assert spectrum_is_union_of_sectors(H, g)


class TestMeasurementGrouping:
    def test_valid_and_reducing(self):
        H = hubbard_dimer_hamiltonian(1.0, 4.0)
        qwc = qubit_wise_commuting_groups(H)
        com = commuting_groups(H)
        assert is_valid_grouping(H, qwc, qwc=True)
        assert is_valid_grouping(H, com, qwc=False)
        r = measurement_reduction(H)
        assert r["n_commuting_groups"] <= r["n_qwc_groups"] <= r["n_terms"]


class TestExcitedStates:
    def _H(self):
        rng = np.random.default_rng(2)
        A = rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8))
        return (A + A.conj().T) / 2

    def test_folded_spectrum(self):
        H = self._H(); w = np.linalg.eigvalsh(H)
        omega = w[3] + 0.1
        e, _ = nearest_eigenstate(H, omega)
        assert abs(e - w[np.argmin(np.abs(w - omega))]) < 1e-6

    def test_ritz_variational(self):
        H = self._H(); w = np.linalg.eigvalsh(H)
        vecs = np.linalg.eigh(H)[1]
        assert np.allclose(np.sort(subspace_energies(H, vecs[:, :3])), w[:3])
        rng = np.random.default_rng(3)
        Br = rng.normal(size=(8, 3)) + 1j * rng.normal(size=(8, 3))
        assert np.all(np.sort(subspace_energies(H, Br)) >= w[:3] - 1e-9)

    def test_ssvqe_optimum(self):
        H = self._H(); w = np.linalg.eigvalsh(H); vecs = np.linalg.eigh(H)[1]
        weights = [3, 2, 1]
        opt = ssvqe_cost(H, [vecs[:, i] for i in range(3)], weights)
        assert abs(opt - sum(weights[i] * w[i] for i in range(3))) < 1e-9

    def test_deflation(self):
        H = self._H(); w = np.linalg.eigvalsh(H)
        assert np.allclose(excited_spectrum_by_deflation(H, 4, beta=100.0), w[:4], atol=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
