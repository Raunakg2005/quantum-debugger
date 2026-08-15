"""
The [[4,2,2]] error-detecting code

The smallest useful stabilizer code: 4 physical qubits, 2 logical qubits,
distance 2. It cannot *correct* errors, but its two stabilizers

    S1 = XXXX,   S2 = ZZZZ

detect EVERY single-qubit Pauli error (each anticommutes with at least one
stabilizer). Discarding runs with a nontrivial syndrome ("post-selection") leaves
only weight-2+ error events, so the logical error rate drops from O(p) to O(p^2)
-- at the price of an O(p) rejection rate. This detect-and-discard strategy powers
many early fault-tolerance experiments.

Logical operators: ``X1 = XXII``, ``Z1 = ZIZI``, ``X2 = XIXI``, ``Z2 = ZZII``;
codewords ``|00_L> = (|0000> + |1111>)/sqrt(2)`` etc.
"""

import numpy as np

from ..stabilizer import stabilizer_to_pauli_matrix as _pauli
from ..density_matrix import DensityMatrix, depolarizing

_STABS = ["XXXX", "ZZZZ"]
_DIM = 16
_EYE = np.eye(_DIM, dtype=complex)

_X_L1 = "XXII"
_X_L2 = "XIXI"


def four_two_two_codewords() -> dict:
    """
    The four logical basis codewords ``|ab_L>`` of the [[4,2,2]] code, built from
    the stabilizer projector and the logical X operators. Returns a dict mapping
    ``"00", "01", "10", "11"`` to normalized 16-dim state vectors.
    """
    proj = _EYE.copy()
    for s in _STABS:
        proj = proj @ ((_EYE + _pauli(1, s)) / 2)
    v = proj[:, 0]
    zero_zero = v / np.linalg.norm(v)

    out = {"00": zero_zero}
    out["10"] = _pauli(1, _X_L1) @ zero_zero
    out["01"] = _pauli(1, _X_L2) @ zero_zero
    out["11"] = _pauli(1, _X_L1) @ _pauli(1, _X_L2) @ zero_zero
    return out


def detect_single_errors() -> dict:
    """
    Verify the distance-2 property operator-by-operator: every one of the 12
    single-qubit Pauli errors anticommutes with at least one stabilizer, so its
    syndrome is nontrivial and the error is detected.

    Returns dict with ``detected`` (count, = 12), ``total`` (12), and
    ``all_detected``.
    """
    detected = 0
    total = 0
    stab_mats = [_pauli(1, s) for s in _STABS]
    for q in range(4):
        for p in "XYZ":
            total += 1
            E = _pauli(1, "".join(p if i == q else "I" for i in range(4)))
            if any(np.allclose(S @ E, -E @ S, atol=1e-12) for S in stab_mats):
                detected += 1
    return {"detected": detected, "total": total, "all_detected": detected == total}


def postselected_memory(p: float, logical: str = "00") -> dict:
    """
    Detect-and-discard quantum memory: store a codeword under independent
    depolarizing noise of strength ``p`` per qubit, measure both stabilizers, and
    keep the run only if both give +1.

    Returns dict with:
      * ``postselected_fidelity`` -- of the kept state to the codeword;
        infidelity is O(p^2) (every weight-1 error is rejected)
      * ``acceptance_probability`` -- fraction of runs kept (1 - O(p))
      * ``unencoded_fidelity``     -- a bare qubit under the same channel (1 - O(p))
    """
    codewords = four_two_two_codewords()
    if logical not in codewords:
        raise ValueError("logical must be one of '00', '01', '10', '11'")
    psi = codewords[logical]

    dm = DensityMatrix(state_vector=psi)
    kraus = depolarizing(p)
    for q in range(4):
        dm.apply_channel(kraus, [q])

    proj = _EYE.copy()
    for s in _STABS:
        proj = proj @ ((_EYE + _pauli(1, s)) / 2)
    kept = proj @ dm.rho @ proj
    accept = float(np.real(np.trace(kept)))
    kept = kept / accept

    fidelity = float(np.real(psi.conj() @ kept @ psi))

    bare = DensityMatrix(state_vector=np.array([1, 0], dtype=complex))
    bare.apply_channel(kraus, [0])
    bare_fid = float(np.real(bare.rho[0, 0]))

    return {
        "postselected_fidelity": fidelity,
        "acceptance_probability": accept,
        "unencoded_fidelity": bare_fid,
    }
