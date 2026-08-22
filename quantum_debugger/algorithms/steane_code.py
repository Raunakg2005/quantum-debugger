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
from ..core.quantum_state import apply_gate_tensor
from ..core.gates import GateLibrary
from ..density_matrix import DensityMatrix, depolarizing

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


# --- continuous noise: distance-3 quadratic suppression ---------------------

_RECOVERY_CACHE = []


def _recovery_ops():
    """
    Lazily build the exact CPTP recovery: for each of the 64 syndromes, the
    projector ``P_s = prod_i (I + (-1)^{s_i} S_i)/2`` and the decoder's correction
    (the matching weight-<=1 Pauli where one exists, identity otherwise).
    """
    if _RECOVERY_CACHE:
        return _RECOVERY_CACHE
    stab_mats = [_pauli(1, s) for s in _STABILIZERS]
    for code in range(64):
        syndrome = tuple((code >> i) & 1 for i in range(6))
        proj = _EYE.copy()
        for bit, S in zip(syndrome, stab_mats):
            proj = proj @ ((_EYE + (-1 if bit else 1) * S) / 2)
        corr = _ERRORS[_DECODER.get(syndrome, "I")]
        _RECOVERY_CACHE.append((proj, corr))
    return _RECOVERY_CACHE


def steane_code_noisy(p: float, alpha=1.0, beta=0.0) -> dict:
    """
    Run the Steane code against an independent depolarizing channel of strength ``p``
    on every physical qubit, with the exact CPTP syndrome recovery, on the 7-qubit
    density matrix. Because the code has distance 3, every weight-0 and weight-1
    error is corrected and the logical error is **quadratically suppressed**:
    ``1 - F ~ O(p^2)`` while a bare qubit fails at ``O(p)``.

    Returns dict with:
      * ``corrected``     -- logical fidelity after recovery
      * ``uncorrected``   -- a bare qubit under the same channel (``1 - 2p/3`` for |0>)
      * ``weight1_bound`` -- ``(1-p)^7 + 7p(1-p)^6``, the guaranteed floor from
                             correcting all weight-<=1 errors (``corrected`` exceeds it
                             because some higher-weight errors are also fixed)
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm
    encoded = alpha * _ZERO_L + beta * _ONE_L

    dm = DensityMatrix(state_vector=encoded)
    kraus = depolarizing(p)
    for q in range(_N):
        dm.apply_channel(kraus, [q])

    new = np.zeros_like(dm.rho)
    for proj, corr in _recovery_ops():
        M = corr @ proj
        new += M @ dm.rho @ M.conj().T
    dm.rho = new

    corrected = float(np.real(encoded.conj() @ dm.rho @ encoded))

    single = DensityMatrix(state_vector=np.array([alpha, beta], dtype=complex))
    single.apply_channel(kraus, [0])
    psi = np.array([alpha, beta], dtype=complex)
    uncorrected = float(np.real(psi.conj() @ single.rho @ psi))

    return {
        "corrected": corrected,
        "uncorrected": uncorrected,
        "weight1_bound": (1 - p) ** 7 + 7 * p * (1 - p) ** 6,
    }


# --- transversal logical gates ---------------------------------------------

_H_GATE = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_S_GATE = np.array([[1, 0], [0, 1j]], dtype=complex)

# Physical gate applied to all 7 qubits -> the logical gate it enacts. For the
# Steane code, transversal S implements logical S-DAGGER (and vice versa), because
# the |1_L> codewords have Hamming weight 3 mod 4; H and the Paulis map to themselves.
_X_GATE = np.array([[0, 1], [1, 0]], dtype=complex)
_Z_GATE = np.array([[1, 0], [0, -1]], dtype=complex)

_TRANSVERSAL = {
    "X": (_X_GATE, _X_GATE),
    "Z": (_Z_GATE, _Z_GATE),
    "H": (_H_GATE, _H_GATE),
    "S": (_S_GATE, _S_GATE.conj().T),
    "Sdg": (_S_GATE.conj().T, _S_GATE),
}


def _encode(alpha, beta):
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    return (alpha * _ZERO_L + beta * _ONE_L) / norm


def steane_transversal(gate: str, alpha=1.0, beta=0.0) -> dict:
    """
    Apply a physical gate to **all 7 qubits** of an encoded ``alpha|0_L> + beta|1_L>``
    and identify the logical gate this enacts -- without ever decoding. This is the
    defining fault-tolerance property of the Steane code: transversal gates cannot
    spread an error within a block.

    ``gate`` is one of ``"X"``, ``"Z"``, ``"H"``, ``"S"``, ``"Sdg"``. Transversal
    X/Z/H enact logical X/Z/H; transversal S enacts logical **S-dagger** (and vice
    versa), a hallmark of the code's weight structure.

    Returns dict with ``logical_action`` (the logical gate name) and ``fidelity`` of
    the transversally-acted state to that logical action's encoding (1.0 exactly).
    """
    if gate not in _TRANSVERSAL:
        raise ValueError(f"gate must be one of {sorted(_TRANSVERSAL)}")
    U, logical = _TRANSVERSAL[gate]

    encoded = _encode(alpha, beta)
    acted = encoded
    for q in range(_N):
        acted = apply_gate_tensor(np, acted, U, [q], _N)

    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    la, lb = logical @ np.array([alpha / norm, beta / norm])
    ideal = _encode(la, lb)

    names = {"X": "X", "Z": "Z", "H": "H", "S": "Sdg", "Sdg": "S"}
    return {
        "logical_action": names[gate],
        "fidelity": float(abs(np.vdot(ideal, acted)) ** 2),
    }


def steane_transversal_cnot(control=(1.0, 0.0), target=(1.0, 0.0)) -> dict:
    """
    Bitwise CNOT between two Steane code blocks (14 physical qubits): CNOT from qubit
    ``i`` of block A to qubit ``i`` of block B, for all 7 pairs. Being a CSS code,
    this enacts a perfect **logical CNOT** (control A, target B) -- the workhorse of
    fault-tolerant computation, since each physical CNOT touches one qubit per block.

    ``control`` and ``target`` are the logical amplitude pairs ``(alpha, beta)`` of the
    two blocks. Returns dict with ``fidelity`` of the 14-qubit state after the 7
    physical CNOTs to the encoding of ``CNOT (|control_L> |target_L>)`` (1.0 exactly).
    """
    a, b = control
    c, d = target
    na = np.sqrt(abs(a) ** 2 + abs(b) ** 2)
    nb = np.sqrt(abs(c) ** 2 + abs(d) ** 2)
    a, b, c, d = a / na, b / na, c / nb, d / nb

    basis = {0: _ZERO_L, 1: _ONE_L}

    def enc2(i, j):  # block A = qubits 0..6, block B = qubits 7..13 (little-endian)
        return np.kron(basis[j], basis[i])

    vec = (
        a * c * enc2(0, 0)
        + a * d * enc2(0, 1)
        + b * c * enc2(1, 0)
        + b * d * enc2(1, 1)
    )
    for q in range(_N):
        vec = apply_gate_tensor(np, vec, GateLibrary.CNOT, [q, _N + q], 2 * _N)

    # Logical CNOT: (i, j) -> (i, j XOR i).
    ideal = (
        a * c * enc2(0, 0)
        + a * d * enc2(0, 1)
        + b * c * enc2(1, 1)
        + b * d * enc2(1, 0)
    )
    return {"fidelity": float(abs(np.vdot(ideal, vec)) ** 2)}
