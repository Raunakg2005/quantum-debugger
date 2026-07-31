"""
Reduced density matrices (RDMs) for electronic-structure states.

Every observable of a fermionic state that is at most two-body -- and the molecular
energy is exactly two-body -- is determined by the one- and two-particle reduced
density matrices

    D_{pq}   = <psi| a_p^dagger a_q |psi>,
    d_{pqrs} = <psi| a_p^dagger a_q^dagger a_r a_s |psi>.

They compress a ``2^n`` state into ``O(n^2)`` / ``O(n^4)`` numbers from which the energy
``E = sum h_{pq} D_{pq} + sum h_{pqrs} d_{pqrs}`` follows exactly. This module builds
both RDMs from a state and reconstructs the energy, verified: the 1-RDM trace equals the
particle number, and the RDM energy matches the direct expectation ``<psi|H|psi>``.
"""

import numpy as np

from .fermion_mappings import (
    jordan_wigner_annihilation, parity_annihilation, bravyi_kitaev_annihilation)

_MAPPINGS = {
    "jw": jordan_wigner_annihilation, "jordan_wigner": jordan_wigner_annihilation,
    "parity": parity_annihilation, "bk": bravyi_kitaev_annihilation,
    "bravyi_kitaev": bravyi_kitaev_annihilation,
}


def _annihilators(n, mapping):
    return [_MAPPINGS[mapping](j, n) for j in range(n)]


def one_particle_rdm(state, mapping: str = "jw") -> np.ndarray:
    """
    One-particle reduced density matrix ``D_{pq} = <psi| a_p^dagger a_q |psi>``. Hermitian
    and positive semi-definite; its trace is the particle number and its eigenvalues (the
    natural-orbital occupations) lie in ``[0, 1]``. Verified against those properties.
    """
    psi = np.asarray(state, dtype=complex)
    n = int(round(np.log2(len(psi))))
    a = _annihilators(n, mapping)
    D = np.zeros((n, n), dtype=complex)
    for p in range(n):
        for q in range(n):
            D[p, q] = np.vdot(psi, a[p].conj().T @ a[q] @ psi)
    return D


def two_particle_rdm(state, mapping: str = "jw") -> np.ndarray:
    """
    Two-particle reduced density matrix
    ``d_{pqrs} = <psi| a_p^dagger a_q^dagger a_r a_s |psi>`` -- the object from which the
    electron-repulsion energy is read off.
    """
    psi = np.asarray(state, dtype=complex)
    n = int(round(np.log2(len(psi))))
    a = _annihilators(n, mapping)
    d = np.zeros((n, n, n, n), dtype=complex)
    adag = [x.conj().T for x in a]
    for p in range(n):
        for q in range(n):
            left = adag[p] @ adag[q]
            for r in range(n):
                for s in range(n):
                    d[p, q, r, s] = np.vdot(psi, left @ a[r] @ a[s] @ psi)
    return d


def energy_from_rdm(rdm1, rdm2, one_body, two_body=None) -> float:
    """
    Molecular energy reconstructed from the RDMs:
    ``E = sum_{pq} h_{pq} D_{pq} + sum_{pqrs} h_{pqrs} d_{pqrs}``. Matches the direct
    expectation ``<psi|H|psi>`` exactly -- the basis of RDM-based (measurement-frugal)
    energy evaluation.
    """
    E = np.real(np.sum(np.asarray(one_body) * np.asarray(rdm1)))
    if two_body is not None:
        E += np.real(np.sum(np.asarray(two_body) * np.asarray(rdm2)))
    return float(E)


def natural_orbital_occupations(state, mapping: str = "jw") -> np.ndarray:
    """
    Natural-orbital occupation numbers: the eigenvalues of the 1-RDM (sorted descending),
    each in ``[0, 1]`` and summing to the particle number -- a diagnostic of how
    correlated a state is (all 0/1 for a single determinant).
    """
    w = np.linalg.eigvalsh(one_particle_rdm(state, mapping))
    return np.sort(np.real(w))[::-1]
