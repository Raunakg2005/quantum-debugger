"""
QUBO and Ising problem encodings.

Combinatorial optimization runs on a quantum computer by encoding the objective as the
*ground state* of a diagonal Hamiltonian. The two standard forms are

* **QUBO** -- minimize ``x^T Q x`` over binary ``x in {0,1}^n``,
* **Ising** -- minimize ``sum_i h_i s_i + sum_{i<j} J_ij s_i s_j`` over spins
  ``s in {-1,+1}^n``,

related by ``s = 1 - 2x``. Classic problems (MaxCut, number partitioning, vertex cover) map
onto QUBO with a fixed recipe, and a penalty term enforces constraints. This module builds
the encodings, the diagonal Ising Hamiltonian, and the exact (brute-force) optimum, and
verifies that the Hamiltonian's ground state is the true optimizer.
"""

import numpy as np
from itertools import product


def qubo_energy(Q, x) -> float:
    """Objective ``x^T Q x`` of a QUBO for a binary vector ``x``."""
    x = np.asarray(x, dtype=float)
    return float(x @ np.asarray(Q, dtype=float) @ x)


def ising_energy(h, J, s) -> float:
    """Ising energy ``sum h_i s_i + sum_{i<j} J_ij s_i s_j`` for a spin vector ``s`` in
    ``{-1,+1}``."""
    h = np.asarray(h, dtype=float); J = np.asarray(J, dtype=float); s = np.asarray(s, dtype=float)
    return float(h @ s + s @ np.triu(J, 1) @ s)


def qubo_to_ising(Q):
    """
    Convert a QUBO matrix ``Q`` to Ising ``(h, J, offset)`` via ``x = (1 - s)/2``. Returns the
    linear fields, the (upper-triangular) couplings, and the constant offset so that
    ``x^T Q x = sum h_i s_i + sum J_ij s_i s_j + offset``. Verified energy-equivalent.
    """
    Q = np.asarray(Q, dtype=float)
    n = Q.shape[0]
    Qs = (Q + Q.T) / 2                      # symmetrize
    J = np.zeros((n, n))
    h = np.zeros(n)
    offset = 0.0
    for i in range(n):
        offset += Qs[i, i] / 2
        h[i] -= Qs[i, i] / 2
        for j in range(i + 1, n):
            J[i, j] = Qs[i, j] / 2
            h[i] -= Qs[i, j] / 2
            h[j] -= Qs[i, j] / 2
            offset += Qs[i, j] / 2
    return h, J, offset


def ising_hamiltonian(h, J) -> np.ndarray:
    """
    Diagonal Ising Hamiltonian on ``2^n`` states: entry for computational basis state ``b``
    (bit ``i`` -> spin ``s_i = 1 - 2 b_i``) is the Ising energy. Its ground state encodes the
    optimizer.
    """
    h = np.asarray(h, dtype=float); J = np.asarray(J, dtype=float)
    n = len(h)
    diag = np.zeros(2 ** n)
    for b in range(2 ** n):
        s = np.array([1 - 2 * ((b >> i) & 1) for i in range(n)], dtype=float)
        diag[b] = h @ s + s @ np.triu(J, 1) @ s
    return np.diag(diag)


def brute_force_ising(h, J):
    """Exact Ising minimizer by enumeration: returns ``(best_spins, best_energy)`` -- the
    verification target for the quantum encodings."""
    n = len(h)
    best_s, best_e = None, np.inf
    for bits in product([1, -1], repeat=n):
        e = ising_energy(h, J, bits)
        if e < best_e:
            best_e, best_s = e, np.array(bits)
    return best_s, float(best_e)


def brute_force_qubo(Q):
    """Exact QUBO minimizer by enumeration: returns ``(best_x, best_energy)``."""
    n = np.asarray(Q).shape[0]
    best_x, best_e = None, np.inf
    for bits in product([0, 1], repeat=n):
        e = qubo_energy(Q, bits)
        if e < best_e:
            best_e, best_x = e, np.array(bits)
    return best_x, float(best_e)


def max_cut_qubo(edges, n_nodes: int):
    """
    QUBO matrix for MaxCut: maximize the number of cut edges = minimize
    ``sum_{(i,j)} (2 x_i x_j - x_i - x_j)``. The ground state's bit partition is a maximum
    cut. Verified against brute force.
    """
    Q = np.zeros((n_nodes, n_nodes))
    for i, j in edges:
        Q[i, i] -= 1
        Q[j, j] -= 1
        Q[i, j] += 2
    return Q


def number_partition_qubo(numbers):
    """
    QUBO for number partitioning: split ``numbers`` into two sets of equal sum. Encodes
    ``(sum_i a_i (1 - 2 x_i))^2`` (dropping the constant ``(sum a)^2``), so the ground state is
    a *balanced* partition and its energy is ``-(sum a)^2`` for a perfect split. Verified
    against brute force.
    """
    a = np.asarray(numbers, dtype=float)
    n = len(a)
    # (sum a_i (1-2x_i))^2 -> QUBO
    Q = np.zeros((n, n))
    for i in range(n):
        Q[i, i] += a[i] * a[i] * 4 - 4 * a[i] * a.sum()
        for j in range(n):
            if i != j:
                Q[i, j] += 4 * a[i] * a[j]
    return Q


def vertex_cover_qubo(edges, n_nodes: int, penalty: float = 2.0):
    """
    QUBO for minimum vertex cover: minimize the number of chosen vertices ``sum x_i`` subject
    to covering every edge, enforced by a ``penalty`` term ``P(1 - x_i)(1 - x_j)`` per edge.
    Verified: the ground state is a minimum cover.
    """
    Q = np.zeros((n_nodes, n_nodes))
    for i in range(n_nodes):
        Q[i, i] += 1
    for i, j in edges:
        Q[i, i] -= penalty
        Q[j, j] -= penalty
        Q[i, j] += penalty
    return Q
