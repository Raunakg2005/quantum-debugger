"""
Probabilistic error cancellation via the Pauli-transfer-matrix (PTM) inverse.

A single-qubit channel is a ``4 x 4`` real matrix in the Pauli basis (its PTM). If the
noise channel ``N`` is invertible, applying ``N^{-1}`` as a *quasiprobability* map
cancels the error exactly in expectation. ``N^{-1}`` is generally not a physical
channel, so it is realized as a signed combination of physical operations; the cost is
the one-norm ``gamma = ||N^{-1}||_1`` (the sampling overhead), which is ``1`` only for
the identity and grows with the noise. This module builds PTMs from Kraus operators,
inverts them, cancels the noise on an observable, and reports the overhead -- each step
verified against the exact noiseless value / a closed form.
"""

import numpy as np

_PAULI = [
    np.eye(2, dtype=complex),
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
]


def channel_ptm(kraus_ops) -> np.ndarray:
    """
    Pauli transfer matrix of a single-qubit channel: ``R_ij = (1/2) Tr[P_i N(P_j)]`` for
    Pauli basis ``{I, X, Y, Z}``. A real ``4 x 4`` matrix that composes by multiplication
    and acts on the Pauli (Bloch) representation of a state.
    """
    K = [np.asarray(k, dtype=complex) for k in kraus_ops]
    R = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            NPj = sum(k @ _PAULI[j] @ k.conj().T for k in K)
            R[i, j] = np.real(0.5 * np.trace(_PAULI[i] @ NPj))
    return R


def invert_channel_ptm(ptm) -> np.ndarray:
    """
    Inverse PTM ``N^{-1}`` -- the quasiprobability map that cancels the channel. Verified
    by ``N^{-1} N = I`` (the identity PTM).
    """
    return np.linalg.inv(np.asarray(ptm, dtype=float))


# Hadamard sign matrix relating Pauli-channel error rates to PTM diagonal (M = M^T,
# M^2 = 4I, so the inverse map is M/4).
_M = np.array([[1, 1, 1, 1],
               [1, 1, -1, -1],
               [1, -1, 1, -1],
               [1, -1, -1, 1]], dtype=float)


def pauli_quasiprobabilities(ptm) -> np.ndarray:
    """
    Quasiprobabilities ``(c_I, c_X, c_Y, c_Z)`` of the *inverse* of a Pauli channel
    (diagonal PTM): the signed weights with which one applies ``I, X, Y, Z`` conjugations
    to cancel the noise, ``N^{-1}(rho) = sum_i c_i P_i rho P_i``. They sum to 1 (trace
    preserving) but some are negative -- that is why PEC needs sign-weighted sampling.
    """
    r = np.diag(np.asarray(ptm, dtype=float))
    if not np.allclose(np.asarray(ptm, dtype=float), np.diag(r), atol=1e-9):
        raise ValueError("Pauli quasiprobabilities require a diagonal (Pauli-channel) PTM")
    r_inv = np.array([1.0, 1.0 / r[1], 1.0 / r[2], 1.0 / r[3]])
    return (_M @ r_inv) / 4.0


def pec_sampling_overhead(ptm) -> float:
    """
    PEC sampling overhead ``gamma = sum_i |c_i|`` -- the one-norm of the inverse channel's
    quasiprobability decomposition into Pauli operations, i.e. the multiplicative shot
    cost of cancelling the noise. Equals ``1`` exactly for the identity and grows with the
    noise; for depolarizing it matches :func:`depolarizing_overhead`.
    """
    return float(np.sum(np.abs(pauli_quasiprobabilities(ptm))))


def depolarizing_overhead(p: float) -> float:
    """
    Closed-form PEC overhead of the single-qubit depolarizing channel (depolarizing
    parameter ``p``): ``gamma = (1 + p/2) / (1 - p)``. Used to verify
    :func:`pec_sampling_overhead` against a known value.
    """
    return (1 + p / 2) / (1 - p)


def bloch_vector(rho) -> np.ndarray:
    """Pauli representation ``(1, <X>, <Y>, <Z>)`` of a single-qubit density matrix."""
    rho = np.asarray(rho, dtype=complex)
    return np.array([np.real(np.trace(P @ rho)) for P in _PAULI])


def pec_mitigate_ptm(noisy_rho, noise_kraus, observable) -> float:
    """
    Cancel a single-qubit channel on an observable by applying the inverse PTM to the
    noisy state's Pauli vector and reading off the expectation. Recovers the exact
    noiseless ``Tr[O rho_ideal]`` (in expectation) -- verified against the ideal value.
    """
    R_inv = invert_channel_ptm(channel_ptm(noise_kraus))
    v_noisy = bloch_vector(noisy_rho)
    v_corrected = R_inv @ v_noisy
    # Reconstruct the corrected (quasi-)state and take the expectation.
    rho_corr = 0.5 * sum(c * P for c, P in zip(v_corrected, _PAULI))
    O = np.asarray(observable, dtype=complex)
    return float(np.real(np.trace(O @ rho_corr)))
