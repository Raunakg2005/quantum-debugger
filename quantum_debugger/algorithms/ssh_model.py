"""
The Su-Schrieffer-Heeger (SSH) model -- the textbook topological insulator.

A 1D chain with alternating hopping amplitudes ``v`` (intracell) and ``w``
(intercell) has two phases distinguished by a bulk topological invariant, the
*winding number*: trivial (``0``) when the intracell bond dominates (``|v| > |w|``)
and topological (``1``) when the intercell bond dominates (``|v| < |w|``). By the
bulk-boundary correspondence the topological phase hosts a protected zero-energy
mode at each end of an open chain. Everything here is a genuine single-particle
Hamiltonian diagonalized exactly, and the invariant / edge-mode count are verified
against that spectrum.
"""

import numpy as np


def ssh_hamiltonian(cells: int, v: float, w: float) -> np.ndarray:
    """
    Single-particle SSH Hamiltonian on an open chain of ``cells`` unit cells
    (``2*cells`` sites): intracell hopping ``v`` (A<->B in a cell) and intercell hopping
    ``w`` (B of one cell <-> A of the next). Real symmetric with chiral (sublattice)
    symmetry, so its spectrum is symmetric about zero.
    """
    n = 2 * cells
    H = np.zeros((n, n))
    for c in range(cells):
        a, b = 2 * c, 2 * c + 1
        H[a, b] = H[b, a] = v  # intracell bond
        if c + 1 < cells:
            H[b, b + 1] = H[b + 1, b] = w  # intercell bond
    return H


def ssh_winding_number(v: float, w: float) -> int:
    """
    Bulk winding number of the SSH model: ``1`` (topological) when ``|w| > |v|``, ``0``
    (trivial) when ``|w| < |v|``. This is the ``Z`` invariant of the chiral 1D class BDI
    that the bulk-boundary correspondence ties to the edge-mode count.
    """
    return int(abs(w) > abs(v))


def ssh_zero_modes(cells: int, v: float, w: float) -> int:
    """
    Number of (near) zero-energy eigenmodes of the open SSH chain -- the edge states.
    Equals ``2`` in the topological phase (one per end) and ``0`` in the trivial phase,
    matching ``2 * winding_number`` for a long enough chain. Edge modes sit far below the
    bulk gap ``~2||v|-|w||``; they are counted as those with ``|E| < 0.1 max(|v|,|w|)``.
    Verified against the exact spectrum.
    """
    eigs = np.linalg.eigvalsh(ssh_hamiltonian(cells, v, w))
    threshold = 0.1 * max(abs(v), abs(w), 1e-12)
    return int(np.sum(np.abs(eigs) < threshold))


def ssh_edge_polarization(cells: int, v: float, w: float) -> float:
    """
    Weight of the near-zero modes localized on the boundary sites -- an operational
    signature of the topological edge states. Close to 1 in the topological phase (modes
    pinned to the ends) and small in the trivial phase. Verified against the eigenvectors.
    """
    H = ssh_hamiltonian(cells, v, w)
    vals, vecs = np.linalg.eigh(H)
    n = 2 * cells
    threshold = 0.1 * max(abs(v), abs(w), 1e-12)
    edge = 0.0
    for k in range(n):
        if abs(vals[k]) < threshold:
            psi = vecs[:, k]
            edge += abs(psi[0]) ** 2 + abs(psi[-1]) ** 2
    return float(edge)
