"""
Second-quantized molecular Hamiltonians on qubits.

The electronic-structure Hamiltonian in a finite spin-orbital basis is

    H = sum_{pq} h_{pq} a_p^dagger a_q  +  sum_{pqrs} h_{pqrs} a_p^dagger a_q^dagger a_r a_s

with one-body integrals ``h_{pq}`` (kinetic + nuclear attraction) and two-body
integrals ``h_{pqrs}`` (electron repulsion). This module assembles ``H`` on qubits via
any of the :mod:`fermion_mappings` encodings, projects onto a fixed electron number,
and provides the two reference energies every VQE is measured against: the mean-field
**Hartree-Fock** energy (variational upper bound) and the exact **full-CI** energy.

The builder is verified against closed forms: for non-interacting electrons the ground
energy equals the sum of the lowest orbital energies, and for the two-site Hubbard
dimer it reproduces the analytic ``(U - sqrt(U^2 + 16 t^2)) / 2``.
"""

import numpy as np

from .fermion_mappings import (
    jordan_wigner_annihilation, parity_annihilation, bravyi_kitaev_annihilation)

_MAPPINGS = {
    "jw": jordan_wigner_annihilation,
    "jordan_wigner": jordan_wigner_annihilation,
    "parity": parity_annihilation,
    "bk": bravyi_kitaev_annihilation,
    "bravyi_kitaev": bravyi_kitaev_annihilation,
}


def _annihilators(n, mapping):
    fn = _MAPPINGS[mapping]
    return [fn(j, n) for j in range(n)]


def molecular_hamiltonian(one_body, two_body=None, mapping: str = "jw") -> np.ndarray:
    """
    Assemble the qubit Hamiltonian from one-body ``h_{pq}`` and (optional) two-body
    ``h_{pqrs}`` integrals under the chosen fermion-to-qubit ``mapping``. The two-body
    term is taken literally as ``sum_{pqrs} h_{pqrs} a_p^d a_q^d a_r a_s`` (the caller
    supplies the exact tensor; e.g. an on-site Hubbard ``U n_0 n_1`` is ``h[0,1,1,0]=U``).
    """
    h1 = np.asarray(one_body, dtype=complex)
    n = h1.shape[0]
    a = _annihilators(n, mapping)
    dim = 2 ** n
    H = np.zeros((dim, dim), dtype=complex)
    for p in range(n):
        for q in range(n):
            if abs(h1[p, q]) > 1e-14:
                H += h1[p, q] * (a[p].conj().T @ a[q])
    if two_body is not None:
        h2 = np.asarray(two_body, dtype=complex)
        for p in range(n):
            for q in range(n):
                for r in range(n):
                    for s in range(n):
                        c = h2[p, q, r, s]
                        if abs(c) > 1e-14:
                            H += c * (a[p].conj().T @ a[q].conj().T @ a[r] @ a[s])
    return H


def number_operator(n: int, mapping: str = "jw") -> np.ndarray:
    """Total particle-number operator ``N = sum_j a_j^dagger a_j`` in the given mapping."""
    a = _annihilators(n, mapping)
    return sum(a[j].conj().T @ a[j] for j in range(n))


def fci_energy(hamiltonian, n_electrons: int, n_orbitals: int = None,
               mapping: str = "jw") -> float:
    """
    Full-configuration-interaction ground energy: the lowest eigenvalue of ``H`` inside
    the ``n_electrons`` particle-number sector (projecting out other fillings). This is
    the exact ground-state energy the VQE targets.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    n = int(round(np.log2(H.shape[0]))) if n_orbitals is None else n_orbitals
    N = number_operator(n, mapping)
    occ = np.rint(np.real(np.diag(N))).astype(int)
    sector = np.where(occ == n_electrons)[0]
    Hs = H[np.ix_(sector, sector)]
    return float(np.linalg.eigvalsh(Hs)[0])


def hartree_fock_energy(one_body, two_body, n_electrons: int) -> float:
    """
    Restricted Hartree-Fock (single Slater determinant) energy: fill the ``n_electrons``
    lowest one-body orbitals and add the mean-field two-body (direct - exchange) terms.
    A variational upper bound on the FCI energy (verified: ``E_HF >= E_FCI``).
    """
    h1 = np.asarray(one_body, dtype=complex)
    n = h1.shape[0]
    # occupy the lowest orbitals of the one-body matrix
    eigvals, vecs = np.linalg.eigh(h1)
    occ = list(range(n_electrons))
    E = sum(eigvals[i].real for i in occ)
    if two_body is not None:
        h2 = np.asarray(two_body, dtype=complex)
        # transform two-body into the HF orbital basis and add direct-exchange pairs
        C = vecs
        g = np.einsum("pa,qb,pqrs,rc,sd->abcd", C.conj(), C.conj(), h2, C, C,
                      optimize=True)
        for i in occ:
            for j in occ:
                E += np.real(g[i, j, j, i] - g[i, j, i, j])
    return float(E)


def hubbard_dimer_hamiltonian(t: float, U: float, mapping: str = "jw"):
    """
    Two-site Hubbard dimer (4 spin-orbitals: site0-up, site0-dn, site1-up, site1-dn):
    hopping ``-t`` between same-spin sites and on-site repulsion ``U``. Its half-filling
    (2-electron) ground energy has the closed form ``(U - sqrt(U^2 + 16 t^2))/2`` --
    the verification target for the two-body builder.
    """
    h1 = np.zeros((4, 4))
    h1[0, 2] = h1[2, 0] = -t          # up hopping
    h1[1, 3] = h1[3, 1] = -t          # down hopping
    h2 = np.zeros((4, 4, 4, 4))
    h2[0, 1, 1, 0] = U                 # U n_{0up} n_{0dn}
    h2[2, 3, 3, 2] = U                 # U n_{1up} n_{1dn}
    return molecular_hamiltonian(h1, h2, mapping)
