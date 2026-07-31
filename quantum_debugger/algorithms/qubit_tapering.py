"""
Z2 qubit tapering -- shrinking a Hamiltonian using its symmetries.

Molecular Hamiltonians conserve quantities (electron number, spin parity) that show up
as **Z2 symmetries**: Pauli operators ``tau`` with ``[tau, H] = 0`` and ``tau^2 = I``.
Each independent symmetry lets you fix a ``+/-1`` eigenvalue and remove one qubit --
the Bravyi-Gonzalez-Kitaev-Mezzacapo-Temme tapering. The symmetry generators are found
from the null space (over GF(2)) of the Hamiltonian's Pauli support under the symplectic
form; projecting onto a symmetry sector block-diagonalizes ``H``.

Verified: the recovered generators commute with ``H`` and square to the identity, and
the spectrum of ``H`` equals the union of its symmetry-sector spectra -- so the sector
containing the ground state gives the exact energy on fewer qubits.
"""

import numpy as np

from .pauli_hamiltonian import decompose, pauli_matrix, symplectic_commute
from .css_code import gf2_nullspace


def z2_symmetry_generators(H):
    """
    Independent Z2 symmetry generators of a Hermitian ``H``, returned as Pauli-string
    labels. A Pauli ``tau`` is a symmetry iff it commutes with every term of ``H``; these
    are the kernel (over GF(2)) of the term matrix under the symplectic form.
    """
    terms = decompose(H)
    n = int(round(np.log2(np.asarray(H).shape[0])))
    # A symmetry s=(sx|sz) commutes with term p=(px|pz) iff sx.pz + sz.px = 0.
    # Stack rows [pz | px]; the kernel gives (sx|sz).
    rows = [np.concatenate([z, x]) for (_, _, x, z) in terms]
    M = np.array(rows, dtype=int) if rows else np.zeros((1, 2 * n), dtype=int)
    gens = []
    for v in gf2_nullspace(M):
        sx, sz = v[:n], v[n:]
        if not np.any(sx) and not np.any(sz):
            continue
        label = "".join(
            {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}[(int(sx[q]), int(sz[q]))]
            for q in range(n))
        gens.append(label)
    return gens


def is_symmetry(H, label: str, atol: float = 1e-9) -> bool:
    """True iff the Pauli ``label`` commutes with ``H`` and squares to the identity."""
    tau = pauli_matrix(label)
    H = np.asarray(H)
    commutes = np.allclose(tau @ H - H @ tau, 0, atol=atol)
    involution = np.allclose(tau @ tau, np.eye(tau.shape[0]), atol=atol)
    return bool(commutes and involution)


def sector_projector(label: str, sign: int = 1) -> np.ndarray:
    """Projector onto the ``sign`` (+/-1) eigenspace of the symmetry Pauli ``label``."""
    tau = pauli_matrix(label)
    return (np.eye(tau.shape[0]) + sign * tau) / 2


def taper_energy(H, label: str, sign: int = 1) -> float:
    """
    Lowest eigenvalue of ``H`` restricted to the ``sign`` eigenspace of the symmetry
    ``label`` -- the tapered ground energy in that sector (one fewer effective qubit).
    """
    tau = pauli_matrix(label)
    w, v = np.linalg.eigh(tau)
    basis = v[:, np.isclose(w, sign)]                 # sector basis
    Hs = basis.conj().T @ np.asarray(H) @ basis
    return float(np.linalg.eigvalsh(Hs)[0])


def spectrum_is_union_of_sectors(H, label: str, atol: float = 1e-6) -> bool:
    """
    Verify tapering loses nothing: the full spectrum of ``H`` equals the multiset union
    of its spectra in the ``+1`` and ``-1`` sectors of the symmetry ``label``.
    """
    tau = pauli_matrix(label)
    w, v = np.linalg.eigh(tau)
    full = np.sort(np.linalg.eigvalsh(np.asarray(H)))
    parts = []
    for sign in (+1, -1):
        basis = v[:, np.isclose(w, sign)]
        if basis.shape[1]:
            parts.append(np.linalg.eigvalsh(basis.conj().T @ np.asarray(H) @ basis))
    combined = np.sort(np.concatenate(parts))
    return bool(len(combined) == len(full) and np.allclose(combined, full, atol=atol))
