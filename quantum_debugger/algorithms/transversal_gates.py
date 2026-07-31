"""
Transversal logical gates and the Eastin-Knill obstruction.

A logical gate is *transversal* when it is a tensor product of single-qubit gates, one
per physical qubit -- the gold standard for fault tolerance, since a fault on one qubit
cannot spread within a block. The Steane ``[[7,1,3]]`` code has a transversal Clifford
group: ``H^{\\otimes 7}``, ``S^{\\otimes 7}`` (up to inverse), and block-wise ``CNOT``
enact logical ``H``, ``S``, ``CNOT``. But by the **Eastin-Knill theorem** no code has a
transversal *universal* set: for Steane, ``T^{\\otimes 7}`` does not even preserve the
code space. This module builds the Steane code words and verifies each transversal gate's
logical action -- and the Eastin-Knill obstruction to a transversal ``T``.
"""

import numpy as np

from .steane_code import steane_stabilizers

_P1 = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex),
}


def _tensor(label):
    M = np.array([[1.0]], dtype=complex)
    for ch in reversed(label):     # little-endian
        M = np.kron(M, _P1[ch])
    return M


def transversal_gate(single_qubit_gate: str, n: int) -> np.ndarray:
    """Transversal gate ``g^{\\otimes n}`` -- the same single-qubit gate on every qubit."""
    return _tensor(single_qubit_gate * n)


def steane_codewords():
    """
    The logical basis states ``|0_L>, |1_L>`` of the Steane code, built by projecting onto
    the joint ``+1`` stabilizer eigenspace and applying the transversal (logical) ``X``.
    """
    stabs = steane_stabilizers()
    dim = 2 ** 7
    P = np.eye(dim, dtype=complex)
    for s in stabs:
        P = P @ (np.eye(dim) + _tensor(s)) / 2
    zero = np.zeros(dim, dtype=complex); zero[0] = 1.0
    v0 = P @ zero; v0 = v0 / np.linalg.norm(v0)
    v1 = transversal_gate("X", 7) @ v0
    return v0, v1


def preserves_code_space(gate, atol: float = 1e-9) -> bool:
    """True iff ``gate`` maps the Steane code space to itself (both code words stay in the
    logical subspace) -- the prerequisite for being a logical operation."""
    v0, v1 = steane_codewords()
    proj = np.outer(v0, v0.conj()) + np.outer(v1, v1.conj())
    for v in (gate @ v0, gate @ v1):
        if np.linalg.norm(proj @ v - v) > atol:
            return False
    return True


def logical_action(gate) -> np.ndarray:
    """
    The ``2 x 2`` logical operation a code-space-preserving transversal ``gate`` implements,
    read off in the ``{|0_L>, |1_L>}`` basis.
    """
    v0, v1 = steane_codewords()
    B = np.column_stack([v0, v1])
    return B.conj().T @ gate @ B


def steane_transversal_hadamard_is_logical_h(atol: float = 1e-6) -> bool:
    """Verify ``H^{\\otimes 7}`` enacts the logical Hadamard on the Steane code words."""
    L = logical_action(transversal_gate("H", 7))
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    return preserves_code_space(transversal_gate("H", 7)) and _equal_up_to_phase(L, H, atol)


def steane_transversal_s_is_logical_phase(atol: float = 1e-6) -> bool:
    """Verify ``S^{\\otimes 7}`` enacts a logical phase gate (``S`` or ``S^dagger``)."""
    L = logical_action(transversal_gate("S", 7))
    S = np.diag([1, 1j]); Sd = np.diag([1, -1j])
    return preserves_code_space(transversal_gate("S", 7)) and (
        _equal_up_to_phase(L, S, atol) or _equal_up_to_phase(L, Sd, atol))


def eastin_knill_obstruction(atol: float = 1e-6) -> bool:
    """
    Demonstrate the Eastin-Knill theorem for Steane: the transversal ``T^{\\otimes 7}`` does
    **not** preserve the code space, so ``T`` cannot be implemented transversally. Returns
    ``True`` when the obstruction holds (``T^{\\otimes 7}`` leaves the logical subspace).
    """
    return not preserves_code_space(transversal_gate("T", 7), atol)


def _equal_up_to_phase(A, B, atol):
    A = np.asarray(A); B = np.asarray(B)
    idx = np.unravel_index(np.argmax(np.abs(B)), B.shape)
    if abs(A[idx]) < atol:
        return False
    phase = A[idx] / B[idx]
    return bool(np.allclose(A, phase * B, atol=atol))
