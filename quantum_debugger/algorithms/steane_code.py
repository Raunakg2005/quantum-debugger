"""
The Steane 7-qubit code [[7,1,3]]

A CSS code built from the classical [7,4,3] Hamming code, correcting an arbitrary
single-qubit error on 7 physical qubits. Three X-type and three Z-type stabilizer
generators (from the Hamming parity-check matrix) detect Z and X errors respectively;
a Y error trips both. Being a CSS code, X and Z errors are decoded independently.

Stabilizer generators (qubit 0 = first character)::

    X-type:  IIIXXXX,  IXXIIXX,  XIXIXIX
    Z-type:  IIIZZZZ,  IZZIIZZ,  ZIZIZIZ

with logical operators ``Z_L = ZZZZZZZ`` and ``X_L = XXXXXXX``. This module encodes a
logical qubit, applies a chosen single-qubit error, extracts the 6-bit syndrome, and
recovers the state exactly.
"""

import numpy as np

from ..stabilizer import stabilizer_to_pauli_matrix as _pauli

_STABILIZERS = [
    "IIIXXXX",
    "IXXIIXX",
    "XIXIXIX",
    "IIIZZZZ",
    "IZZIIZZ",
    "ZIZIZIZ",
]
_Z_L = "ZZZZZZZ"
_X_L = "XXXXXXX"

_N = 7
_DIM = 2**_N
_EYE = np.eye(_DIM, dtype=complex)


def _single_pauli(pauli: str, qubit: int) -> np.ndarray:
    ps = "".join(pauli if i == qubit else "I" for i in range(_N))
    return _pauli(1, ps)


def _build_logical():
    proj = _EYE.copy()
    for s in _STABILIZERS:
        proj = proj @ ((_EYE + _pauli(1, s)) / 2)
    proj = proj @ ((_EYE + _pauli(1, _Z_L)) / 2)
    # First non-vanishing column is |0_L> (column 0 can be zero for some CSS codes).
    norms = np.linalg.norm(proj, axis=0)
    zero_l = proj[:, int(np.argmax(norms))]
    zero_l = zero_l / np.linalg.norm(zero_l)
    one_l = _pauli(1, _X_L) @ zero_l
    return zero_l, one_l


_ZERO_L, _ONE_L = _build_logical()


def _single_errors():
    errs = {"I": _EYE}
    for q in range(_N):
        for p in "XYZ":
            errs[f"{p}{q}"] = _single_pauli(p, q)
    return errs


_ERRORS = _single_errors()


def _syndrome(vec: np.ndarray) -> tuple:
    bits = []
    for s in _STABILIZERS:
        ev = np.vdot(vec, _pauli(1, s) @ vec).real
        bits.append(0 if ev > 0 else 1)
    return tuple(bits)


_DECODER = {_syndrome(E @ _ZERO_L): name for name, E in _ERRORS.items()}


def steane_code(alpha=1.0, beta=0.0, error: str = "I") -> dict:
    """
    Encode ``alpha|0_L> + beta|1_L>`` in the Steane [[7,1,3]] code, apply a single-qubit
    ``error``, extract the syndrome, and recover -- correcting any single-qubit Pauli
    error exactly.

    ``error`` is ``"I"`` or ``"<P><q>"`` with ``P`` in ``X/Y/Z`` and qubit ``q`` in
    ``0..6`` (e.g. ``"Z5"``, ``"X0"``, ``"Y3"``). Returns a dict with:
      * ``fidelity``   -- overlap of the recovered state with the pre-error codeword
      * ``syndrome``   -- the measured 6-bit syndrome
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


def steane_stabilizers() -> list:
    """The six stabilizer generators as Pauli strings (three X-type, three Z-type)."""
    return list(_STABILIZERS)
