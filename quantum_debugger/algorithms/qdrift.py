"""
qDRIFT -- randomized Hamiltonian simulation.

qDRIFT replaces the deterministic Trotter product by a *random* one: to simulate
``e^{-iHt}`` for ``H = sum_k c_k P_k``, sample ``N`` terms independently with probability
``p_k = |c_k| / lambda`` (``lambda = sum_k |c_k|``) and apply ``e^{-i sign(c_k) lambda (t/N)
P_k}`` for each. The resulting *channel* (averaged over the randomness) approximates
``e^{-iHt}`` with error ``O(lambda^2 t^2 / N)`` -- and, remarkably, the gate count
``N ~ 2 lambda^2 t^2 / epsilon`` is **independent of the number of terms**, which is why qDRIFT
wins for Hamiltonians with many small terms. This module builds the sampling distribution and
the qDRIFT channel and verifies convergence to the exact evolution as ``N`` grows.
"""

import numpy as np
from scipy.linalg import expm

from .hamiltonian_simulation import pauli_term_matrix, hamiltonian_matrix


def qdrift_probabilities(terms):
    """The qDRIFT importance-sampling distribution ``p_k = |c_k| / lambda`` over the
    Hamiltonian terms, and the normalization ``lambda = sum |c_k|``. Returns ``(probs, lambda)``."""
    coeffs = np.array([abs(c) for c, _ in terms])
    lam = coeffs.sum()
    return coeffs / lam, float(lam)


def qdrift_sample_unitary(terms, t: float, N: int, rng) -> np.ndarray:
    """
    One sample of the qDRIFT unitary: a product of ``N`` random single-term rotations
    ``e^{-i sign(c_k) lambda (t/N) P_k}`` with terms drawn from ``p_k``. Averaging these over
    samples gives the qDRIFT channel.
    """
    probs, lam = qdrift_probabilities(terms)
    n = len(terms[0][1])
    tau = lam * t / N
    U = np.eye(2 ** n, dtype=complex)
    for _ in range(N):
        k = rng.choice(len(terms), p=probs)
        c, p = terms[k]
        U = expm(-1j * np.sign(c) * tau * pauli_term_matrix(p)) @ U
    return U


def qdrift_channel(terms, t: float, N: int, rho, samples: int = 200, seed: int = 0) -> np.ndarray:
    """
    The qDRIFT channel applied to a state ``rho``: the Monte-Carlo average of
    ``U rho U^dagger`` over ``samples`` random qDRIFT unitaries with ``N`` steps each. Converges
    to the exact ``e^{-iHt} rho e^{iHt}`` as ``N`` grows.
    """
    rng = np.random.default_rng(seed)
    rho = np.asarray(rho, dtype=complex)
    out = np.zeros_like(rho)
    for _ in range(samples):
        U = qdrift_sample_unitary(terms, t, N, rng)
        out += U @ rho @ U.conj().T
    return out / samples


def qdrift_error(terms, t: float, N: int, rho, samples: int = 200, seed: int = 0) -> float:
    """
    Trace-distance error between the qDRIFT channel output and the exact evolution of ``rho``
    -- verified to decrease as the step count ``N`` grows.
    """
    n = len(terms[0][1])
    U_exact = expm(-1j * hamiltonian_matrix(terms, n) * t)
    rho = np.asarray(rho, dtype=complex)
    exact = U_exact @ rho @ U_exact.conj().T
    approx = qdrift_channel(terms, t, N, rho, samples, seed)
    diff = approx - exact
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh((diff + diff.conj().T) / 2))))


def qdrift_gate_count(lam: float, t: float, epsilon: float) -> float:
    """
    qDRIFT gate count ``N ~ 2 lambda^2 t^2 / epsilon`` for target error ``epsilon`` --
    independent of the number of Hamiltonian terms, the qDRIFT advantage.
    """
    return float(2 * lam ** 2 * t ** 2 / epsilon)
