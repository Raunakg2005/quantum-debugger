"""
Quantum Error Correction under continuous noise (density-matrix, exact)

The routines in :mod:`error_correction` inject a single *discrete* Pauli error and
recover it on the state-vector engine. Real devices instead apply *continuous*
noise -- every physical qubit independently suffers an error channel with some
probability ``p`` per cycle. This module runs a QEC code against that continuous
noise on the density-matrix engine and returns the exact logical fidelity (no
Monte-Carlo sampling).

For the 3-qubit repetition (bit-flip) code correcting an independent bit-flip
channel of strength ``p`` on each qubit, the recovery succeeds whenever 0 or 1 of
the 3 qubits flips, so the logical fidelity of a computational-basis codeword is

    F_corrected(p) = (1 - p)**3 + 3 p (1 - p)**2

which exceeds the un-encoded single-qubit fidelity ``1 - p`` for all ``p < 1/2``
(the code threshold). ``bit_flip_code_noisy`` reproduces this exactly from the
density-matrix simulation, and ``repetition_code_logical_error`` gives the
closed-form logical error rate for any odd code distance.
"""

import numpy as np

from ..density_matrix import DensityMatrix, bit_flip, phase_flip
from ..stabilizer import stabilizer_to_pauli_matrix

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def _recovery_channel(rho, stabilizers, corrections):
    """
    Apply an exact CPTP recovery: for each syndrome ``s`` build the projector
    ``P_s = prod_k (I + sign_k S_k) / 2`` onto that syndrome subspace, apply the
    matching correction unitary ``C_s``, and sum ``C_s P_s rho P_s C_s-dagger``.

    ``stabilizers`` is a list of Pauli strings (qubit 0 = first char); ``corrections``
    maps a syndrome tuple (of +/-1 eigenvalues) to a correction Pauli string.
    """
    dim = rho.shape[0]
    identity = np.eye(dim, dtype=complex)
    stab_mats = [stabilizer_to_pauli_matrix(1, s) for s in stabilizers]

    out = np.zeros_like(rho)
    for syndrome, corr in corrections.items():
        proj = identity
        for sign, S in zip(syndrome, stab_mats):
            proj = proj @ ((identity + sign * S) / 2)
        C = stabilizer_to_pauli_matrix(1, corr)
        out += C @ proj @ rho @ proj.conj().T @ C.conj().T
    return out


# 3-qubit bit-flip code: stabilizers Z0Z1, Z1Z2; syndrome -> qubit to flip back.
_BITFLIP_STABS = ["ZZI", "IZZ"]
_BITFLIP_RECOVERY = {
    (1, 1): "III",    # no error
    (-1, 1): "XII",   # error on qubit 0
    (-1, -1): "IXI",  # error on qubit 1
    (1, -1): "IIX",   # error on qubit 2
}


def bit_flip_code_noisy(p: float, alpha: float = 1.0, beta: float = 0.0) -> dict:
    """
    Encode a logical qubit ``alpha|0_L> + beta|1_L>`` in the 3-qubit bit-flip code,
    apply an independent bit-flip channel of strength ``p`` to each physical qubit,
    recover, and return the logical fidelity -- all exactly on the density matrix.

    Returns a dict with:
      * ``corrected``   -- logical fidelity after syndrome recovery
      * ``uncorrected`` -- fidelity of a lone qubit under the same channel (``1 - p``)
      * ``analytic``    -- closed form ``(1-p)**3 + 3 p (1-p)**2`` (for a codeword)
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm

    # Logical codeword alpha|000> + beta|111> (little-endian: |111> = index 7).
    sv = np.zeros(8, dtype=complex)
    sv[0], sv[7] = alpha, beta
    dm = DensityMatrix(state_vector=sv)
    ideal = sv.copy()

    for q in range(3):
        dm.apply_channel(bit_flip(p), [q])

    dm.rho = _recovery_channel(dm.rho, _BITFLIP_STABS, _BITFLIP_RECOVERY)

    single = DensityMatrix(state_vector=np.array([alpha, beta], dtype=complex))
    single.apply_channel(bit_flip(p), [0])

    return {
        "corrected": dm.fidelity(ideal),
        "uncorrected": single.fidelity(np.array([alpha, beta], dtype=complex)),
        "analytic": (1 - p) ** 3 + 3 * p * (1 - p) ** 2,
    }


def phase_flip_code_noisy(p: float, alpha: float = 1.0, beta: float = 0.0) -> dict:
    """
    Phase-flip analogue of :func:`bit_flip_code_noisy`. The 3-qubit phase-flip code
    is the bit-flip code conjugated by Hadamards, so it protects against an
    independent phase-flip channel of strength ``p`` with the identical logical
    fidelity ``(1-p)**3 + 3 p (1-p)**2``.
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm

    sv = np.zeros(8, dtype=complex)
    sv[0], sv[7] = alpha, beta
    dm = DensityMatrix(state_vector=sv)
    # Move to the Hadamard basis so a phase-flip channel looks like a bit flip.
    for q in range(3):
        dm.apply_unitary(_H, [q])
    ideal = dm.rho.copy()

    for q in range(3):
        dm.apply_channel(phase_flip(p), [q])

    # Recovery in the X-basis: stabilizers X0X1, X1X2, corrections are Z flips.
    stabs = ["XXI", "IXX"]
    recovery = {(1, 1): "III", (-1, 1): "ZII", (-1, -1): "IZI", (1, -1): "IIZ"}
    dm.rho = _recovery_channel(dm.rho, stabs, recovery)

    return {
        "corrected": dm.fidelity(DensityMatrix(rho=ideal)),
        "analytic": (1 - p) ** 3 + 3 * p * (1 - p) ** 2,
    }


def repetition_code_logical_error(p: float, distance: int = 3) -> float:
    """
    Exact logical error rate of the ``distance``-qubit repetition code under an
    independent bit-flip channel of strength ``p``, using majority-vote decoding.

    A logical error occurs iff more than half the physical qubits flip:

        P_L = sum_{k > distance/2} C(distance, k) p**k (1 - p)**(distance - k)

    ``distance`` must be odd. Below threshold (``p < 1/2``) increasing the distance
    suppresses ``P_L`` -- the defining feature of a good code.
    """
    if distance % 2 == 0:
        raise ValueError("distance must be odd for majority-vote decoding")
    from math import comb

    return sum(
        comb(distance, k) * p**k * (1 - p) ** (distance - k)
        for k in range(distance // 2 + 1, distance + 1)
    )
