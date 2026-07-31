"""
Fock-space operators for a single bosonic mode.

The harmonic oscillator lives in the infinite-dimensional Fock basis ``|0>, |1>, ...``;
truncating at a photon-number ``cutoff`` makes it computable. This module builds the ladder
operators and the Gaussian/​non-Gaussian state-preparation unitaries -- creation and
annihilation (``[a, a^dagger] = I`` away from the truncation edge), the displacement
operator making coherent states, and the squeeze operator making squeezed vacuum. Verified
against the closed forms: ``a|alpha> = alpha|alpha>``, Poissonian photon statistics
``<n> = |alpha|^2``, and the even-photon structure of squeezed vacuum.
"""

import numpy as np
from scipy.linalg import expm


def annihilation_operator(cutoff: int) -> np.ndarray:
    """Annihilation operator ``a`` truncated at ``cutoff`` levels: ``a|n> = sqrt(n)|n-1>``."""
    return np.diag(np.sqrt(np.arange(1, cutoff)), 1).astype(complex)


def creation_operator(cutoff: int) -> np.ndarray:
    """Creation operator ``a^dagger`` -- the conjugate transpose of the annihilation
    operator."""
    return annihilation_operator(cutoff).conj().T


def number_operator_fock(cutoff: int) -> np.ndarray:
    """Number operator ``N = a^dagger a = diag(0, 1, ..., cutoff-1)``."""
    return np.diag(np.arange(cutoff)).astype(complex)


def coherent_state_fock(alpha: complex, cutoff: int) -> np.ndarray:
    """
    Coherent state ``|alpha> = e^{-|alpha|^2/2} sum_n alpha^n/sqrt(n!) |n>`` truncated at
    ``cutoff`` -- the most classical state, an eigenstate of ``a`` with eigenvalue ``alpha``
    and Poissonian photon statistics ``<n> = |alpha|^2``.
    """
    if abs(alpha) < 1e-12:
        psi = np.zeros(cutoff, dtype=complex); psi[0] = 1.0
        return psi
    n = np.arange(cutoff)
    logc = -abs(alpha) ** 2 / 2 + n * np.log(alpha + 0j) - 0.5 * _log_factorial(n)
    psi = np.exp(logc)
    return psi / np.linalg.norm(psi)


def displacement_operator(alpha: complex, cutoff: int) -> np.ndarray:
    """
    Displacement operator ``D(alpha) = exp(alpha a^dagger - alpha^* a)`` -- the Gaussian
    unitary that maps the vacuum to the coherent state ``|alpha>``.
    """
    a = annihilation_operator(cutoff)
    return expm(alpha * a.conj().T - np.conj(alpha) * a)


def squeeze_operator(r: float, cutoff: int) -> np.ndarray:
    """
    Squeeze operator ``S(r) = exp((r/2)(a^2 - a^{dagger 2}))`` -- maps the vacuum to squeezed
    vacuum, a non-classical state supported only on *even* photon numbers.
    """
    a = annihilation_operator(cutoff)
    return expm(0.5 * r * (a @ a - a.conj().T @ a.conj().T))


def mean_photon_number(state) -> float:
    """Mean photon number ``<n>`` of a Fock-basis state vector."""
    psi = np.asarray(state, dtype=complex)
    n = np.arange(len(psi))
    return float(np.sum(n * np.abs(psi) ** 2))


def _log_factorial(n):
    from scipy.special import gammaln
    return gammaln(np.asarray(n) + 1)
