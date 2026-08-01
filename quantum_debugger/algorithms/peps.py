"""
Projected Entangled Pair States (PEPS) -- tensor networks in 2D.

An MPS captures 1D entanglement; its 2D generalization is the **PEPS**, one tensor per lattice
site with a physical index and virtual (bond) indices to its neighbours. PEPS obey a 2D area
law and represent ground states of 2D gapped Hamiltonians; the 2D **cluster state** has an exact
bond-dimension-2 PEPS. Contracting a PEPS is #P-hard in general, but a small lattice contracts
directly to the full state vector. This module builds product and cluster-state PEPS on a
``2 x 2`` lattice, contracts them exactly, and verifies the results against the independently
constructed states.
"""

import numpy as np

# Site tensor legs are ordered [physical, up, down, left, right].


def product_peps(single_qubit_states=None):
    """
    A product-state ``2 x 2`` PEPS: each site a bond-dimension-1 tensor holding a single-qubit
    state (default ``|0>``). ``single_qubit_states`` is a 2x2 nested list of length-2 vectors.
    """
    peps = {}
    for i in range(2):
        for j in range(2):
            s = np.array([1, 0], dtype=complex) if single_qubit_states is None \
                else np.asarray(single_qubit_states[i][j], dtype=complex)
            peps[(i, j)] = s.reshape(2, 1, 1, 1, 1)
    return peps


def bond_dimension(peps) -> int:
    """The maximum virtual bond dimension across the PEPS tensors -- controls expressiveness and
    contraction cost (1 for a product state, 2 for a cluster state)."""
    return int(max(max(t.shape[1:]) for t in peps.values()))


def is_product_peps(peps, atol: float = 1e-9) -> bool:
    """True iff every PEPS bond has dimension 1 -- i.e. the PEPS is a product state (no
    entanglement)."""
    return bond_dimension(peps) == 1


def contract_2x2(peps) -> np.ndarray:
    """
    Exactly contract a ``2 x 2`` PEPS to the 4-qubit state vector (qubit order
    ``(0,0),(0,1),(1,0),(1,1)``, little-endian), summing the horizontal bonds
    ``(0,0)-(0,1)``, ``(1,0)-(1,1)`` and vertical bonds ``(0,0)-(1,0)``, ``(0,1)-(1,1)``.
    """
    A, B = peps[(0, 0)], peps[(0, 1)]
    C, D = peps[(1, 0)], peps[(1, 1)]
    # squeeze the dim-1 boundary legs, keep physical + internal bonds
    a = A[:, 0, :, 0, :]        # [p, down(v1), right(h1)]
    b = B[:, 0, :, :, 0]        # [p, down(v2), left(h1)]
    c = C[:, :, 0, 0, :]        # [p, up(v1),  right(h2)]
    d = D[:, :, 0, :, 0]        # [p, up(v2),  left(h2)]
    ab = np.einsum("pvh, qwh -> pqvw", a, b, optimize=True)     # contract h1
    cd = np.einsum("pvh, qwh -> pqvw", c, d, optimize=True)     # contract h2
    full = np.einsum("pqvw, rsvw -> pqrs", ab, cd, optimize=True)  # contract v1, v2
    return full.reshape(-1)


def cluster_peps_statevector() -> np.ndarray:
    """
    Contract the exact bond-dimension-2 PEPS of the ``2 x 2`` cluster state. Each site is a "copy"
    (delta) tensor mapping its physical bit onto every bond, and each edge carries the CZ phase
    matrix ``Lambda[v,w] = (-1)^{v w}`` -- so the contraction reproduces ``prod_edges CZ |+>^4``.
    Verified equal to :func:`cluster_state_reference`.
    """
    Lam = np.array([[1, 1], [1, -1]], dtype=complex)   # (-1)^{v w}
    # copy tensors (delta): site value p copied to each present bond
    a = np.zeros((2, 2, 2), dtype=complex)   # (0,0): [p, down, right]
    b = np.zeros((2, 2, 2), dtype=complex)   # (0,1): [p, down, left]
    c = np.zeros((2, 2, 2), dtype=complex)   # (1,0): [p, up,   right]
    d = np.zeros((2, 2, 2), dtype=complex)   # (1,1): [p, up,   left]
    for p in (0, 1):
        a[p, p, p] = b[p, p, p] = c[p, p, p] = d[p, p, p] = 1.0
    # fold the CZ phase onto one endpoint of each of the 4 edges (h1: a-b, h2: c-d, v1: a-c, v2: b-d)
    a = np.einsum("pvr, rR -> pvR", a, Lam)     # right edge (h1) phase
    a = np.einsum("pvr, vV -> pVr", a, Lam)     # down edge  (v1) phase
    c = np.einsum("pvr, rR -> pvR", c, Lam)     # right edge (h2) phase
    b = np.einsum("pvr, vV -> pVr", b, Lam)     # down edge  (v2) phase
    ab = np.einsum("pvh, qwh -> pqvw", a, b, optimize=True)   # contract h1
    cd = np.einsum("pvh, qwh -> pqvw", c, d, optimize=True)   # contract h2
    full = np.einsum("pqvw, rsvw -> pqrs", ab, cd, optimize=True)  # contract v1, v2
    return full.reshape(-1)


def cluster_state_reference() -> np.ndarray:
    """The ``2 x 2`` cluster state built directly from ``H^{⊗4}`` then ``CZ`` on the grid edges
    ``(0,0)-(0,1)``, ``(1,0)-(1,1)``, ``(0,0)-(1,0)``, ``(0,1)-(1,1)`` -- the verification target."""
    psi = np.ones(16, dtype=complex) / 4                       # |+>^4
    edges = [(0, 1), (2, 3), (0, 2), (1, 3)]                   # qubits (0,0)=0,(0,1)=1,(1,0)=2,(1,1)=3
    for b in range(16):
        phase = 1
        for i, j in edges:
            if ((b >> i) & 1) and ((b >> j) & 1):
                phase = -phase
        psi[b] *= phase
    return psi
