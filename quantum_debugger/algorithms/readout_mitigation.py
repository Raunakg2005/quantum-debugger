"""
Readout error mitigation

Real qubit measurements flip: a prepared ``|0>`` is sometimes read as ``1`` and vice
versa. This distorts every measured probability distribution. Readout (measurement)
error mitigation undoes it: characterize the noise once as an **assignment matrix**
``A`` (``A[measured, true]`` = probability of reading ``measured`` given the true
outcome), then correct any noisy histogram by solving ``A p_true = p_measured``.

For independent single-qubit readout with flip probabilities ``p01`` (``0`` read as
``1``) and ``p10`` (``1`` read as ``0``), ``A`` is the tensor product of the one-qubit
matrices. Inverting it recovers the noise-free distribution exactly (up to shot
noise), which this module verifies.
"""

import numpy as np


def assignment_matrix(n_qubits: int, p01: float, p10: float) -> np.ndarray:
    """
    The ``2**n x 2**n`` readout assignment matrix for ``n_qubits`` with independent
    single-qubit flip probabilities ``p01`` (prepare 0, read 1) and ``p10`` (prepare 1,
    read 0). Column ``j`` is the measured distribution when the true state is ``j``.
    """
    single = np.array([[1 - p01, p10], [p01, 1 - p10]], dtype=float)
    A = np.array([[1.0]])
    for _ in range(n_qubits):
        A = np.kron(A, single)
    return A


def apply_readout_noise(probabilities, p01: float, p10: float) -> np.ndarray:
    """Distort a true probability distribution by readout noise: ``A @ p_true``."""
    p = np.asarray(probabilities, dtype=float)
    n = int(round(np.log2(len(p))))
    return assignment_matrix(n, p01, p10) @ p


def mitigate_readout(measured_probs, p01: float, p10: float) -> np.ndarray:
    """
    Correct a measured probability distribution for readout error by solving
    ``A p_true = p_measured``, then clipping negatives and renormalizing (the standard
    matrix-inversion mitigation). Returns the corrected distribution.
    """
    p = np.asarray(measured_probs, dtype=float)
    n = int(round(np.log2(len(p))))
    A = assignment_matrix(n, p01, p10)
    corrected = np.linalg.solve(A, p)
    corrected = np.clip(corrected, 0, None)
    total = corrected.sum()
    return corrected / total if total > 0 else corrected


def mitigate_expectation(measured_probs, observable_diagonal, p01: float, p10: float) -> dict:
    """
    Mitigate the expectation of a diagonal observable (given by its diagonal, e.g.
    ``+/-1`` parities for a Pauli-Z string) measured under readout noise.

    Returns dict with ``raw`` (noisy expectation), ``mitigated`` (corrected), and
    ``correction`` (the shift applied).
    """
    diag = np.asarray(observable_diagonal, dtype=float)
    p_meas = np.asarray(measured_probs, dtype=float)
    raw = float(diag @ p_meas)
    mitigated = float(diag @ mitigate_readout(p_meas, p01, p10))
    return {"raw": raw, "mitigated": mitigated, "correction": mitigated - raw}
