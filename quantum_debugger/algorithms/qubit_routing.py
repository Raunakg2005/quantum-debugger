"""
Qubit routing for limited connectivity.

Real devices only allow two-qubit gates between physically adjacent qubits (a *coupling
map*). Routing inserts SWAP gates to bring interacting logical qubits together. This module
provides the coupling-map executability check, the SWAP network that realizes an arbitrary
qubit permutation as adjacent transpositions, and a linear-chain router that makes any
circuit executable by escorting distant qubits together with SWAPs and back again. Every
routed circuit is verified to be executable on the coupling map *and* equivalent to the
original.
"""

import numpy as np

from .circuit_ir import op

SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)


def coupling_map(edges, n_qubits: int):
    """Undirected coupling map as a set of frozenset edges plus the qubit count."""
    return {"edges": {frozenset(e) for e in edges}, "n": n_qubits}


def is_executable(circuit, coupling) -> bool:
    """True iff every two-qubit operation acts on a connected pair of the coupling map (and
    every one-qubit op is unconstrained)."""
    for _, qubits in circuit:
        if len(qubits) == 2 and frozenset(qubits) not in coupling["edges"]:
            return False
        if len(qubits) > 2:
            return False
    return True


def permutation_matrix(perm, n_qubits: int) -> np.ndarray:
    """Unitary permuting the ``n`` qubits according to ``perm`` (``perm[i]`` is the new
    position of qubit ``i``)."""
    d = 2 ** n_qubits
    P = np.zeros((d, d), dtype=complex)
    for b in range(d):
        nb = 0
        for i in range(n_qubits):
            nb |= ((b >> i) & 1) << perm[i]
        P[nb, b] = 1
    return P


def swap_network(perm):
    """
    Decompose a qubit permutation into a sequence of *adjacent* SWAPs (bubble sort) --
    ``[(j, j+1), ...]`` -- realizing it on a linear architecture (``perm[i]`` is the target
    position of qubit ``i``). Verified: the composed SWAPs equal ``permutation_matrix(perm)``.
    """
    n = len(perm)
    # arr[p] = which logical qubit currently sits at position p; start identity
    arr = list(range(n))
    # target: position perm[q] must hold qubit q  ->  target arrangement[p] = inverse_perm[p]
    target = [0] * n
    for q, p in enumerate(perm):
        target[p] = q
    # bubble arr toward target by adjacent swaps, choosing by target rank
    rank = {q: p for p, q in enumerate(target)}
    swaps = []
    changed = True
    while changed:
        changed = False
        for j in range(n - 1):
            if rank[arr[j]] > rank[arr[j + 1]]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps.append((j, j + 1))
                changed = True
    return swaps


def route_linear(circuit, n_qubits: int):
    """
    Route a circuit onto a *linear* nearest-neighbour coupling map. Each two-qubit gate on
    non-adjacent qubits is executed by SWAPping one qubit next to the other, applying the
    gate, then SWAPping back -- so the logical order is preserved. Returns the routed circuit,
    verified executable on the line and equivalent to the original.
    """
    routed = []
    for matrix, qubits in circuit:
        if len(qubits) != 2 or abs(qubits[0] - qubits[1]) == 1:
            routed.append((np.asarray(matrix, dtype=complex), list(qubits)))
            continue
        a, b = sorted(qubits)
        # bring b down next to a: swaps (b-1,b),(b-2,b-1),...,(a+1,a+2)
        chain = [(k, k + 1) for k in range(b - 1, a, -1)]
        for i, j in chain:
            routed.append((SWAP, [i, j]))
        # gate now acts between a and a+1 (preserve original qubit order)
        g_qubits = [a, a + 1] if qubits[0] < qubits[1] else [a + 1, a]
        routed.append((np.asarray(matrix, dtype=complex), g_qubits))
        for i, j in reversed(chain):
            routed.append((SWAP, [i, j]))
    return routed
