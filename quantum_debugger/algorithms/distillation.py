"""
Entanglement distillation (BBPSSW)

Two copies of a noisy Bell pair are converted into ONE higher-fidelity pair using
only local operations and classical communication (LOCC) -- the primitive behind
quantum repeaters and entanglement-based networking.

The BBPSSW protocol (Bennett, Brassard, Popescu, Schumacher, Smolin & Wootters,
Phys. Rev. Lett. 76, 722, 1996): Alice and Bob each hold one half of two Werner
pairs of fidelity ``F``. Each applies a local CNOT from their pair-1 qubit to their
pair-2 qubit, both measure pair 2, and they keep pair 1 iff the outcomes agree
(classical communication). The kept pair has fidelity

    F' = (F^2 + (1-F)^2/9) / (F^2 + 2F(1-F)/3 + 5(1-F)^2/9)

with success probability equal to the denominator. ``F' > F`` for all ``1/2 < F < 1``:
distillation purifies any Werner pair better than a coin flip.

This module runs the actual 4-qubit circuit on the density-matrix engine (exact,
no sampling) and reproduces the closed form to machine precision.
"""

import numpy as np

from ..density_matrix import DensityMatrix, _embed, _P0, _P1
from ..core.gates import GateLibrary

_S2 = np.sqrt(2)
_PHI_P = np.array([1, 0, 0, 1], dtype=complex) / _S2
_PHI_M = np.array([1, 0, 0, -1], dtype=complex) / _S2
_PSI_P = np.array([0, 1, 1, 0], dtype=complex) / _S2
_PSI_M = np.array([0, 1, -1, 0], dtype=complex) / _S2


def werner_state(F: float) -> np.ndarray:
    """
    Two-qubit Werner state of fidelity ``F``: the ``|Phi+>`` component weighted ``F``,
    the other three Bell states sharing ``1 - F`` equally. Entangled iff ``F > 1/2``.
    """
    rho = F * np.outer(_PHI_P, _PHI_P.conj())
    for bell in (_PHI_M, _PSI_P, _PSI_M):
        rho = rho + (1 - F) / 3 * np.outer(bell, bell.conj())
    return rho


def bbpssw_distill(F: float) -> dict:
    """
    One round of BBPSSW distillation on two Werner pairs of fidelity ``F``, run as the
    exact 4-qubit circuit: local CNOTs (Alice: A1 -> A2, Bob: B1 -> B2), measure
    pair 2, keep pair 1 iff the outcomes agree.

    Returns dict with:
      * ``fidelity``            -- the kept pair's fidelity to ``|Phi+>``
      * ``success_probability`` -- chance the round is kept
      * ``analytic``            -- the closed-form ``F'`` (matches ``fidelity`` exactly)
      * ``improved``            -- whether ``fidelity > F``
    """
    # Qubits (little-endian): A1=0, B1=1, A2=2, B2=3.
    dm = DensityMatrix(rho=np.kron(werner_state(F), werner_state(F)))
    dm.apply_unitary(GateLibrary.CNOT, [0, 2])  # Alice
    dm.apply_unitary(GateLibrary.CNOT, [1, 3])  # Bob

    n = 4
    p00 = _embed(_P0, [2], n) @ _embed(_P0, [3], n)
    p11 = _embed(_P1, [2], n) @ _embed(_P1, [3], n)
    kept = p00 @ dm.rho @ p00 + p11 @ dm.rho @ p11
    p_success = float(np.real(np.trace(kept)))

    pair1 = DensityMatrix(rho=kept / p_success).partial_trace([0, 1])
    fidelity = float(np.real(_PHI_P.conj() @ pair1.rho @ _PHI_P))

    denom = F**2 + 2 * F * (1 - F) / 3 + 5 * ((1 - F) / 3) ** 2
    analytic = (F**2 + ((1 - F) / 3) ** 2) / denom

    return {
        "fidelity": fidelity,
        "success_probability": p_success,
        "analytic": analytic,
        "improved": fidelity > F,
    }


def distillation_rounds(F: float, target: float, max_rounds: int = 50) -> dict:
    """
    Iterate the BBPSSW recurrence (with re-twirling to Werner form between rounds,
    the idealized protocol) until the fidelity reaches ``target``.

    Returns dict with ``rounds``, ``fidelities`` (the trajectory, starting at ``F``),
    and ``reached`` (False if ``F <= 1/2`` -- below the distillation threshold -- or
    ``max_rounds`` was hit).

    Each round consumes two pairs to make one, so reaching round ``r`` costs ``2**r``
    input pairs per output pair (ignoring failed rounds).
    """
    fids = [F]
    for _ in range(max_rounds):
        if fids[-1] >= target:
            break
        if fids[-1] <= 0.5:
            return {"rounds": len(fids) - 1, "fidelities": fids, "reached": False}
        Fc = fids[-1]
        denom = Fc**2 + 2 * Fc * (1 - Fc) / 3 + 5 * ((1 - Fc) / 3) ** 2
        fids.append((Fc**2 + ((1 - Fc) / 3) ** 2) / denom)
    return {
        "rounds": len(fids) - 1,
        "fidelities": fids,
        "reached": fids[-1] >= target,
    }
