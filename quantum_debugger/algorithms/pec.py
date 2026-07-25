"""
Probabilistic Error Cancellation (PEC)

A noise channel cannot be undone by a physical operation -- its inverse is not
completely positive. But it *can* be written as a signed combination of physical
operations, a **quasi-probability** decomposition

    N^{-1} = sum_i b_i O_i,      sum_i b_i = 1,   some b_i < 0.

Running each ``O_i`` with probability ``|b_i| / gamma`` (``gamma = sum |b_i|``) and
weighting the result by ``sign(b_i) * gamma`` gives an unbiased estimate of the
noise-free expectation. The price is a variance blow-up by ``gamma^2`` -- the sampling
overhead.

For a Pauli-diagonal single-qubit channel ``N(rho) = sum_i a_i P_i rho P_i`` (the form
of bit/phase-flip and depolarizing noise), the inverse is another Pauli-diagonal map
whose coefficients follow from inverting the Pauli-transfer eigenvalues. This module
builds that inverse and verifies it cancels the noise exactly.
"""

import numpy as np

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULIS = (_I, _X, _Y, _Z)


def _ptm_eigenvalues(coeffs):
    """Pauli-transfer eigenvalues (e_I, e_X, e_Y, e_Z) of ``sum_i a_i P_i . P_i``."""
    a0, a1, a2, a3 = coeffs
    return np.array([
        a0 + a1 + a2 + a3,          # identity component (= 1 for a channel)
        a0 + a1 - a2 - a3,          # X
        a0 - a1 + a2 - a3,          # Y
        a0 - a1 - a2 + a3,          # Z
    ])


def _coeffs_from_ptm(e):
    """Inverse of :func:`_ptm_eigenvalues`: Pauli-conjugation coefficients from PTM."""
    return np.array([
        (e[0] + e[1] + e[2] + e[3]) / 4,
        (e[0] + e[1] - e[2] - e[3]) / 4,
        (e[0] - e[1] + e[2] - e[3]) / 4,
        (e[0] - e[1] - e[2] + e[3]) / 4,
    ])


def invert_pauli_channel(coeffs) -> dict:
    """
    Quasi-probability inverse of the Pauli-diagonal channel ``sum_i coeffs[i] P_i . P_i``.

    Returns dict with ``quasi_probabilities`` (the ``b_i``, summing to 1, some negative)
    and ``overhead`` (``gamma = sum |b_i|``, the sampling-cost multiplier ``>= 1``).
    """
    e = _ptm_eigenvalues(coeffs)
    if np.any(np.abs(e) < 1e-12):
        raise ValueError("channel is not invertible (a Pauli-transfer eigenvalue is 0)")
    b = _coeffs_from_ptm(1.0 / e)
    return {"quasi_probabilities": b, "overhead": float(np.sum(np.abs(b)))}


def depolarizing_coeffs(p: float):
    """Pauli-diagonal coefficients ``(a_I, a_X, a_Y, a_Z)`` of ``depolarizing(p)``."""
    return np.array([1 - 3 * p / 4, p / 4, p / 4, p / 4])


def apply_pauli_channel(rho, coeffs) -> np.ndarray:
    """Apply ``sum_i coeffs[i] P_i rho P_i`` to a single-qubit density matrix."""
    R = np.asarray(rho, dtype=complex)
    return sum(c * (P @ R @ P.conj().T) for c, P in zip(coeffs, _PAULIS))


def pec_mitigate(noisy_rho, channel_coeffs, observable, ideal_state=None) -> dict:
    """
    Cancel the noise ``channel_coeffs`` on a single-qubit ``noisy_rho`` and estimate the
    observable's noise-free expectation via PEC (apply the quasi-probability inverse,
    then read the observable).

    Returns dict with ``raw`` (noisy expectation), ``mitigated`` (PEC-corrected),
    ``overhead`` (``gamma``), and -- if ``ideal_state`` is given -- ``ideal``,
    ``raw_error``, ``mitigated_error``, ``improved``.
    """
    R = np.asarray(noisy_rho, dtype=complex)
    O = np.asarray(observable, dtype=complex)
    inv = invert_pauli_channel(channel_coeffs)
    corrected = apply_pauli_channel(R, inv["quasi_probabilities"])

    raw = float(np.real(np.trace(O @ R)))
    mitigated = float(np.real(np.trace(O @ corrected)))
    result = {"raw": raw, "mitigated": mitigated, "overhead": inv["overhead"]}
    if ideal_state is not None:
        psi = np.asarray(ideal_state, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        ideal = float(np.real(psi.conj() @ O @ psi))
        result.update(
            ideal=ideal,
            raw_error=abs(raw - ideal),
            mitigated_error=abs(mitigated - ideal),
            improved=abs(mitigated - ideal) < abs(raw - ideal) + 1e-12,
        )
    return result
