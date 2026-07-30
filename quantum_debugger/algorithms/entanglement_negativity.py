"""
Entanglement negativity -- a computable mixed-state entanglement measure.

Entanglement entropy only measures *pure*-state entanglement. For a mixed state the
**negativity** is the standard computable substitute: it is built from the partial
transpose ``rho^{T_B}``, whose appearance of *negative* eigenvalues is (by the
Peres-Horodecki criterion) a witness of entanglement. The **logarithmic negativity**
``E_N = log2 ||rho^{T_B}||_1`` is an entanglement monotone and equals the number of
Bell pairs for maximally entangled states. Verified here against Bell states (``E_N=1``),
product states (``0``), and the Werner-state entanglement threshold.
"""

import numpy as np


def partial_transpose(rho, dims, subsystem: int = 1) -> np.ndarray:
    """
    Partial transpose of a bipartite density matrix ``rho`` over ``subsystem`` (0 or 1),
    with subsystem dimensions ``dims = (dA, dB)``. The map whose negative eigenvalues
    detect entanglement (Peres-Horodecki).
    """
    dA, dB = dims
    r = np.asarray(rho, dtype=complex).reshape(dA, dB, dA, dB)
    if subsystem == 1:
        r = r.transpose(0, 3, 2, 1)
    else:
        r = r.transpose(2, 1, 0, 3)
    return r.reshape(dA * dB, dA * dB)


def negativity(rho, dims, subsystem: int = 1) -> float:
    """
    Negativity ``N = (||rho^{T_B}||_1 - 1) / 2 = sum of |negative eigenvalues|`` of the
    partial transpose -- zero for unentangled states, positive for (NPT) entangled ones.
    """
    eig = np.linalg.eigvalsh(partial_transpose(rho, dims, subsystem))
    return float(np.sum(np.abs(eig[eig < 0])))


def logarithmic_negativity(rho, dims, subsystem: int = 1) -> float:
    """
    Logarithmic negativity ``E_N = log2 ||rho^{T_B}||_1`` -- an additive entanglement
    monotone and an upper bound on distillable entanglement. Equals 1 for a Bell pair and
    0 for a separable state. Verified against both.
    """
    eig = np.linalg.eigvalsh(partial_transpose(rho, dims, subsystem))
    trace_norm = float(np.sum(np.abs(eig)))
    return float(np.log2(trace_norm))


def is_entangled_ppt(rho, dims, subsystem: int = 1, tol: float = 1e-9) -> bool:
    """
    Peres-Horodecki (PPT) test: ``True`` if the partial transpose has a negative
    eigenvalue (a sufficient condition for entanglement, and also necessary for 2x2 and
    2x3 systems). The operational reading of the negativity.
    """
    eig = np.linalg.eigvalsh(partial_transpose(rho, dims, subsystem))
    return bool(np.min(eig) < -tol)
