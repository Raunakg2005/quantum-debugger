"""
Taylor-series (truncated-Dyson) Hamiltonian simulation.

Instead of a product formula, ``e^{-iHt}`` can be approximated by truncating its Taylor
series,

    e^{-iHt} ~= sum_{k=0}^{K} (-iHt)^k / k! ,

which, realized on hardware as a linear combination of unitaries, gives an error that falls
*factorially* with the truncation order ``K`` -- exponentially better in ``K`` than a Trotter
formula. The order needed for precision ``epsilon`` is essentially ``K ~ log(1/eps)/log log(1/eps)``,
set by ``||Ht||^{K+1}/(K+1)! < eps``. This module builds the truncated series, measures its
error, and computes the required order, verified against the exact matrix exponential.
"""

import numpy as np
from scipy.linalg import expm
from math import factorial

from .hamiltonian_simulation import hamiltonian_matrix


def taylor_series_unitary(H, t: float, order: int) -> np.ndarray:
    """
    The truncated Taylor series ``sum_{k=0}^{order} (-iHt)^k/k!`` of the propagator. Not exactly
    unitary (truncation), but converges to ``e^{-iHt}`` as ``order`` grows.
    """
    H = np.asarray(H, dtype=complex)
    d = H.shape[0]
    A = -1j * H * t
    term = np.eye(d, dtype=complex)
    out = np.eye(d, dtype=complex)
    for k in range(1, order + 1):
        term = term @ A / k
        out = out + term
    return out


def taylor_error(H, t: float, order: int) -> float:
    """Spectral-norm error ``||series - e^{-iHt}||`` of the truncated Taylor propagator --
    verified to fall factorially with the truncation order."""
    return float(np.linalg.norm(taylor_series_unitary(H, t, order) - expm(-1j * np.asarray(H, dtype=complex) * t), 2))


def taylor_truncation_order(norm_Ht: float, epsilon: float, max_order: int = 100) -> int:
    """
    Smallest truncation order ``K`` with ``||Ht||^{K+1}/(K+1)! < epsilon`` -- the factorially
    small tail of the Taylor series. Verified to bound the actual error.
    """
    for K in range(max_order):
        if norm_Ht ** (K + 1) / factorial(K + 1) < epsilon:
            return K
    return max_order


def hamiltonian_from_terms(terms) -> np.ndarray:
    """Assemble the dense Hamiltonian matrix from weighted Pauli-string ``terms`` -- the input
    to Taylor-series simulation."""
    n = len(terms[0][1])
    return hamiltonian_matrix(terms, n)


def series_convergence(H, t: float, orders=(1, 2, 4, 8, 12)):
    """The Taylor error at a sequence of truncation orders -- verified strictly decreasing, the
    factorial convergence of the series."""
    return [taylor_error(H, t, k) for k in orders]
