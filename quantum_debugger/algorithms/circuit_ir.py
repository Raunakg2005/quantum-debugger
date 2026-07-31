"""
A minimal circuit intermediate representation (IR) for the compiler.

Every compiler pass here operates on the same simple IR: a circuit on ``n`` qubits is a list
of *operations*, each a ``(matrix, qubits)`` pair applying a ``2^k x 2^k`` unitary to ``k``
named qubits (little-endian, qubit 0 = least significant). The IR knows how to build the
full ``2^n`` unitary of a circuit and to test whether two circuits are *equivalent* (equal up
to a global phase). That equivalence test is the correctness oracle every optimization pass
is verified against: a pass may only rewrite a circuit into an equivalent one.
"""

import numpy as np


def op(matrix, qubits):
    """Construct an IR operation: a gate ``matrix`` acting on the listed ``qubits``."""
    return (np.asarray(matrix, dtype=complex), list(qubits))


def _embed(matrix, qubits, n) -> np.ndarray:
    """Embed a ``k``-qubit gate acting on ``qubits`` into the ``2^n`` space (little-endian)."""
    k = len(qubits)
    full = np.zeros((2 ** n, 2 ** n), dtype=complex)
    other = [q for q in range(n) if q not in qubits]
    for basis in range(2 ** n):
        # split basis index into gate-qubit bits and spectator bits
        gate_in = 0
        for a, q in enumerate(qubits):
            gate_in |= ((basis >> q) & 1) << a
        spec = tuple((basis >> q) & 1 for q in other)
        for gate_out in range(2 ** k):
            amp = matrix[gate_out, gate_in]
            if amp == 0:
                continue
            out = 0
            for a, q in enumerate(qubits):
                out |= ((gate_out >> a) & 1) << q
            for b, q in enumerate(other):
                out |= spec[b] << q
            full[out, basis] += amp
    return full


def circuit_unitary(circuit, n_qubits: int) -> np.ndarray:
    """The full ``2^n x 2^n`` unitary of a circuit (product of its embedded operations, in
    order)."""
    U = np.eye(2 ** n_qubits, dtype=complex)
    for matrix, qubits in circuit:
        U = _embed(matrix, qubits, n_qubits) @ U
    return U


def circuits_equivalent(c1, c2, n_qubits: int, atol: float = 1e-9) -> bool:
    """
    True iff two circuits implement the same unitary up to a global phase -- the correctness
    oracle for every optimization pass.
    """
    U = circuit_unitary(c1, n_qubits)
    V = circuit_unitary(c2, n_qubits)
    i = np.unravel_index(np.argmax(np.abs(V)), V.shape)
    if abs(U[i]) < atol:
        return False
    return bool(np.allclose(U * (V[i] / U[i]), V, atol=atol))


def gate_count(circuit) -> int:
    """Total number of operations in a circuit."""
    return len(circuit)


def two_qubit_count(circuit) -> int:
    """Number of two-(or more)-qubit operations -- the dominant hardware cost."""
    return sum(1 for _, qubits in circuit if len(qubits) >= 2)
