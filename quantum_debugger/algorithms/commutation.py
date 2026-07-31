"""
Gate commutation analysis.

Two operations that act on disjoint qubits, or whose matrices commute, can be reordered
without changing the circuit's unitary. Commutation is what lets a scheduler move gates past
each other to expose parallelism or bring cancelling gates together. This module tests
whether two IR operations commute (disjoint support, or commuting matrices on shared qubits)
and reorders a circuit by bubbling a chosen operation earlier through commuting neighbours.
Verified against :func:`circuits_equivalent`.
"""

import numpy as np

from .circuit_ir import _embed


def operations_commute(op_a, op_b, n_qubits: int, atol: float = 1e-9) -> bool:
    """
    True iff two IR operations commute: trivially if their qubit supports are disjoint, else
    iff their embedded matrices commute. Reordering commuting operations preserves the
    unitary.
    """
    ma, qa = op_a
    mb, qb = op_b
    if set(qa).isdisjoint(qb):
        return True
    A = _embed(ma, qa, n_qubits)
    B = _embed(mb, qb, n_qubits)
    return bool(np.allclose(A @ B - B @ A, 0, atol=atol))


def commute_forward(circuit, index: int, n_qubits: int):
    """
    Move the operation at ``index`` as early as possible by swapping it past earlier
    operations it commutes with. Returns the reordered circuit -- an equivalent one, verified.
    """
    circuit = [(np.asarray(m, dtype=complex), list(q)) for m, q in circuit]
    i = index
    while i > 0 and operations_commute(circuit[i - 1], circuit[i], n_qubits):
        circuit[i - 1], circuit[i] = circuit[i], circuit[i - 1]
        i -= 1
    return circuit


def commutation_graph(circuit, n_qubits: int):
    """
    Adjacency (boolean) matrix of which operations commute -- the dependency structure a
    scheduler uses to find independent gates.
    """
    m = len(circuit)
    G = np.zeros((m, m), dtype=bool)
    for i in range(m):
        for j in range(m):
            if i != j:
                G[i, j] = operations_commute(circuit[i], circuit[j], n_qubits)
    return G
