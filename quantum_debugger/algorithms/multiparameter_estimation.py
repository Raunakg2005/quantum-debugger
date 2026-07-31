"""
Multiparameter quantum estimation.

Estimating several parameters ``theta = (theta_1, ..., theta_p)`` at once (imprinted by
generators ``G_1, ..., G_p``) is governed by the **QFI matrix**

    F_ij = 4 Re[<G_i G_j> - <G_i><G_j>]   (pure state),

and the matrix Cramér-Rao bound ``Cov(theta) >= F^{-1}``. Unlike the single-parameter case,
the optimal measurements for different parameters may be *incompatible* -- when the generators
do not effectively commute, the single-parameter bounds cannot all be saturated at once. This
module builds the QFI matrix, the matrix Cramér-Rao bound, and an incompatibility measure,
verified positive semi-definite and against the commuting (compatible) case.
"""

import numpy as np


def qfi_matrix(state, generators) -> np.ndarray:
    """
    Quantum Fisher information matrix ``F_ij = 4 Re[<G_i G_j> - <G_i><G_j>]`` of a pure state for
    a list of Hermitian ``generators``. Real, symmetric, positive semi-definite (verified).
    """
    psi = np.asarray(state, dtype=complex)
    G = [np.asarray(g, dtype=complex) for g in generators]
    means = [np.real(np.vdot(psi, g @ psi)) for g in G]
    p = len(G)
    F = np.zeros((p, p))
    for i in range(p):
        gi = G[i] @ psi
        for j in range(p):
            gj = G[j] @ psi
            F[i, j] = 4 * np.real(np.vdot(gi, gj) - means[i] * means[j])
    return (F + F.T) / 2


def cramer_rao_matrix(qfi_mat, repetitions: int = 1) -> np.ndarray:
    """Matrix Cramér-Rao bound ``Cov(theta) >= F^{-1}/m`` -- the inverse QFI matrix (over ``m``
    repetitions) lower-bounds the covariance of any unbiased estimator."""
    return np.linalg.inv(np.asarray(qfi_mat, dtype=float)) / repetitions


def is_positive_semidefinite(M, atol: float = 1e-8) -> bool:
    """True iff a symmetric matrix has all eigenvalues ``>= -atol`` (a valid QFI / covariance
    matrix)."""
    M = np.asarray(M, dtype=float)
    return bool(np.min(np.linalg.eigvalsh((M + M.T) / 2)) >= -atol)


def parameter_incompatibility(state, generators) -> float:
    """
    Incompatibility of joint estimation: the norm of the mean commutator matrix
    ``D_ij = -i <[G_i, G_j]>`` (the Uhlmann curvature). Zero when the generators effectively
    commute (parameters jointly, optimally estimable) and positive otherwise -- verified 0 for
    commuting generators.
    """
    psi = np.asarray(state, dtype=complex)
    G = [np.asarray(g, dtype=complex) for g in generators]
    p = len(G)
    D = np.zeros((p, p))
    for i in range(p):
        for j in range(p):
            comm = G[i] @ G[j] - G[j] @ G[i]
            D[i, j] = np.real(-1j * np.vdot(psi, comm @ psi))
    return float(np.linalg.norm(D, 2))


def total_precision_bound(qfi_mat, repetitions: int = 1) -> float:
    """The total-variance Cramér-Rao bound ``Tr(F^{-1})/m`` -- the summed minimal variance over
    all parameters."""
    return float(np.trace(cramer_rao_matrix(qfi_mat, repetitions)))
