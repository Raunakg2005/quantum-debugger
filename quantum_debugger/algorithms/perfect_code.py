"""
The 5-qubit perfect code [[5,1,3]]

The smallest quantum error-correcting code that corrects an *arbitrary* single-qubit
error (any of X, Y, Z on any of the 5 physical qubits). It is a "perfect" code: its
four stabilizer generators produce 16 distinct syndromes, exactly matching the 1
error-free case plus the 15 single-qubit Pauli errors, with none left over.

Stabilizer generators (cyclic), qubit 0 = first character::

    S1 = X Z Z X I
    S2 = I X Z Z X
    S3 = X I X Z Z
    S4 = Z X I X Z

with logical operators ``Z_L = ZZZZZ`` and ``X_L = XXXXX``. This module encodes a
logical qubit, applies a chosen single-qubit error, extracts the syndrome, and
recovers the state exactly.

Reference: Laflamme, Miquel, Paz & Zurek, "Perfect Quantum Error Correction Code"
(Phys. Rev. Lett. 77, 198, 1996).
"""

import numpy as np

from ..stabilizer import stabilizer_to_pauli_matrix as _pauli

_STABILIZERS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
_Z_L = "ZZZZZ"
_X_L = "XXXXX"

_DIM = 32
_EYE = np.eye(_DIM, dtype=complex)


def _single_pauli(pauli: str, qubit: int) -> np.ndarray:
    ps = "".join(pauli if i == qubit else "I" for i in range(5))
    return _pauli(1, ps)


def _build_logical():
    """Logical basis states |0_L>, |1_L> via the stabilizer projector."""
    proj = _EYE.copy()
    for s in _STABILIZERS:
        proj = proj @ ((_EYE + _pauli(1, s)) / 2)
    proj = proj @ ((_EYE + _pauli(1, _Z_L)) / 2)
    zero_l = proj[:, 0]
    zero_l = zero_l / np.linalg.norm(zero_l)
    one_l = _pauli(1, _X_L) @ zero_l
    return zero_l, one_l


_ZERO_L, _ONE_L = _build_logical()


def _single_errors():
    errs = {"I": _EYE}
    for q in range(5):
        for p in "XYZ":
            errs[f"{p}{q}"] = _single_pauli(p, q)
    return errs


_ERRORS = _single_errors()


def _syndrome(vec: np.ndarray) -> tuple:
    """Syndrome (4 bits) of a state: 0 if it +1-stabilizes S_i, else 1."""
    bits = []
    for s in _STABILIZERS:
        ev = np.vdot(vec, _pauli(1, s) @ vec).real
        bits.append(0 if ev > 0 else 1)
    return tuple(bits)


# Decoder lookup table: syndrome -> the error name that produces it.
_DECODER = {_syndrome(E @ _ZERO_L): name for name, E in _ERRORS.items()}


def five_qubit_code(alpha=1.0, beta=0.0, error: str = "I") -> dict:
    """
    Encode ``alpha|0_L> + beta|1_L>`` in the 5-qubit perfect code, apply a single-qubit
    ``error``, extract the syndrome, and recover -- correcting *any* single-qubit
    Pauli error exactly.

    ``error`` is ``"I"`` or ``"<P><q>"`` with ``P`` in ``X/Y/Z`` and qubit ``q`` in
    ``0..4`` (e.g. ``"X2"``, ``"Z0"``, ``"Y4"``). Returns a dict with:
      * ``fidelity``   -- overlap of the recovered state with the pre-error codeword
                          (1.0 for any correctable single-qubit error)
      * ``syndrome``   -- the measured 4-bit syndrome
      * ``correction`` -- the error name the decoder applied
    """
    if error not in _ERRORS:
        raise ValueError(f"error must be 'I' or one of {sorted(_ERRORS)[:-1]}")

    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm
    encoded = alpha * _ZERO_L + beta * _ONE_L

    corrupted = _ERRORS[error] @ encoded
    syndrome = _syndrome(corrupted)
    correction = _DECODER[syndrome]
    recovered = _ERRORS[correction] @ corrupted

    return {
        "fidelity": float(abs(np.vdot(encoded, recovered)) ** 2),
        "syndrome": syndrome,
        "correction": correction,
    }


def five_qubit_stabilizers() -> list:
    """The four stabilizer generators of the code as Pauli strings (qubit 0 first)."""
    return list(_STABILIZERS)
