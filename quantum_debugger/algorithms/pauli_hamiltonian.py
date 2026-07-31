"""
Pauli decomposition utilities shared by qubit tapering and measurement grouping.

A Hermitian operator on ``n`` qubits is a real combination of Pauli strings,
``H = sum_P c_P P``. Each Pauli is stored in the symplectic ``(x, z)`` representation
(``X^x Z^z`` up to phase), in which two Paulis commute iff their symplectic inner
product ``x1.z2 + z1.x2`` is even. These helpers are the common substrate for the
symmetry-tapering and measurement-grouping routines.
"""

import numpy as np
from itertools import product

_P1 = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
_XZ = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}


def pauli_matrix(label: str) -> np.ndarray:
    """Dense matrix of a Pauli string (little-endian: qubit 0 = last factor)."""
    M = np.array([[1.0]], dtype=complex)
    for ch in reversed(label):
        M = np.kron(M, _P1[ch])
    return M


def decompose(H, atol: float = 1e-9):
    """
    Decompose a Hermitian ``H`` into Pauli terms. Returns a list of
    ``(coeff, label, x, z)`` where ``label`` is the Pauli string, ``x``/``z`` are the
    length-``n`` symplectic bit arrays, and ``coeff`` is real.
    """
    H = np.asarray(H, dtype=complex)
    n = int(round(np.log2(H.shape[0])))
    terms = []
    for labels in product("IXYZ", repeat=n):
        label = "".join(labels)
        c = np.trace(pauli_matrix(label).conj().T @ H) / (2 ** n)
        if abs(c) > atol:
            x = np.array([_XZ[ch][0] for ch in labels], dtype=int)
            z = np.array([_XZ[ch][1] for ch in labels], dtype=int)
            terms.append((float(np.real(c)), label, x, z))
    return terms


def symplectic_commute(x1, z1, x2, z2) -> bool:
    """True iff two Paulis commute (even symplectic inner product)."""
    return int(np.dot(x1, z2) + np.dot(z1, x2)) % 2 == 0


def qubit_wise_commute(label_a: str, label_b: str) -> bool:
    """
    True iff two Pauli strings are *qubit-wise* commuting: on every qubit where both are
    non-identity, they use the same Pauli. Such strings share a common eigenbasis and can
    be measured together with single-qubit rotations.
    """
    for ca, cb in zip(label_a, label_b):
        if ca != "I" and cb != "I" and ca != cb:
            return False
    return True
