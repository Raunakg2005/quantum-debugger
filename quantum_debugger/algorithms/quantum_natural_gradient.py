"""
The quantum geometric tensor, Fisher information, and natural gradient.

Ordinary gradient descent moves in the Euclidean parameter space, but the quantum state
space is curved. The **quantum geometric tensor** (Fubini-Study metric)

    g_ij = Re[<d_i psi|d_j psi> - <d_i psi|psi><psi|d_j psi>]

measures distances between neighbouring states; four times its real part is the **quantum
Fisher information matrix**. Preconditioning the gradient by its inverse gives the **quantum
natural gradient**, which follows the steepest-descent direction *on the state manifold* and
often trains far faster. This module builds the metric from parameter-shifted state
derivatives, verifies it is symmetric positive semi-definite, and applies the natural-gradient
update.
"""

import numpy as np

from .variational_ansatz import hardware_efficient_ansatz, ansatz_num_params


def _state_derivatives(params, n, layers, eps=1e-6):
    base = hardware_efficient_ansatz(params, n, layers)
    derivs = []
    for i in range(len(params)):
        p = np.asarray(params, dtype=float).copy(); p[i] += eps
        m = np.asarray(params, dtype=float).copy(); m[i] -= eps
        derivs.append((hardware_efficient_ansatz(p, n, layers)
                       - hardware_efficient_ansatz(m, n, layers)) / (2 * eps))
    return base, derivs


def quantum_geometric_tensor(params, n: int, layers: int) -> np.ndarray:
    """
    Quantum geometric tensor (Fubini-Study metric)
    ``g_ij = Re[<d_i psi|d_j psi> - <d_i psi|psi><psi|d_j psi>]`` of the ansatz at ``params``.
    Real, symmetric, positive semi-definite (verified).
    """
    psi, d = _state_derivatives(params, n, layers)
    m = len(params)
    g = np.zeros((m, m))
    braket = [np.vdot(d[i], psi) for i in range(m)]
    for i in range(m):
        for j in range(m):
            g[i, j] = np.real(np.vdot(d[i], d[j]) - np.conj(braket[i]) * braket[j])
    return g


def quantum_fisher_matrix(params, n: int, layers: int) -> np.ndarray:
    """Quantum Fisher information matrix ``F = 4 g`` (four times the geometric tensor) -- the
    metric that bounds parameter-estimation and rescales the natural gradient."""
    return 4 * quantum_geometric_tensor(params, n, layers)


def is_positive_semidefinite(M, atol: float = 1e-8) -> bool:
    """True iff a symmetric matrix has all eigenvalues ``>= -atol`` -- the property the metric
    must satisfy."""
    M = np.asarray(M, dtype=float)
    if not np.allclose(M, M.T, atol=1e-8):
        return False
    return bool(np.min(np.linalg.eigvalsh((M + M.T) / 2)) >= -atol)


def natural_gradient(gradient, metric, regularization: float = 1e-6) -> np.ndarray:
    """
    Quantum natural gradient ``g^{-1} grad`` (with Tikhonov ``regularization``) -- the update
    direction on the state manifold, which reduces to the ordinary gradient when the metric is
    the identity.
    """
    g = np.asarray(metric, dtype=float)
    reg = g + regularization * np.eye(g.shape[0])
    return np.linalg.solve(reg, np.asarray(gradient, dtype=float))


def fubini_study_distance(state_a, state_b) -> float:
    """Fubini-Study distance ``arccos|<a|b>|`` between two pure states -- the geodesic metric
    the geometric tensor is the infinitesimal form of."""
    ov = abs(np.vdot(np.asarray(state_a, dtype=complex), np.asarray(state_b, dtype=complex)))
    return float(np.arccos(np.clip(ov, 0, 1)))


def effective_quantum_dimension(metric, atol: float = 1e-8) -> int:
    """
    Effective dimension of the ansatz at a point: the rank of the quantum geometric tensor --
    the number of *independent* directions the parameters actually move the state. Below the
    parameter count when the ansatz is over-parametrized or has redundancies.
    """
    w = np.linalg.eigvalsh(np.asarray(metric, dtype=float))
    return int(np.sum(w > atol))
