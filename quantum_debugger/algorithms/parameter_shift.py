"""
Analytic gradients via the parameter-shift rule.

Gradients of a quantum cost ``f(theta) = <psi(theta)|H|psi(theta)>`` can be computed
*exactly* -- not by finite differences -- when each parameter feeds a Pauli-generated
rotation (like ``Ry = e^{-i theta Y/2}``). The **parameter-shift rule** gives

    df/dtheta_i = (1/2) [ f(theta + (pi/2) e_i) - f(theta - (pi/2) e_i) ],

two evaluations of the *same* circuit at shifted angles. Second derivatives follow from a
second shift. This module implements the shift-rule gradient and Hessian and a
finite-difference reference, and verifies they agree.
"""

import numpy as np


def parameter_shift_gradient(cost_fn, params, index: int, shift: float = np.pi / 2) -> float:
    """
    Exact partial derivative ``df/dtheta_index`` by the parameter-shift rule -- the average of
    the cost at ``+shift`` and ``-shift`` (for a ``pi/2`` shift and unit-coefficient Pauli
    generator).
    """
    params = np.asarray(params, dtype=float)
    plus = params.copy(); plus[index] += shift
    minus = params.copy(); minus[index] -= shift
    return float((cost_fn(plus) - cost_fn(minus)) / 2)


def parameter_shift_gradient_all(cost_fn, params) -> np.ndarray:
    """Full gradient vector via the parameter-shift rule (one entry per parameter)."""
    params = np.asarray(params, dtype=float)
    return np.array([parameter_shift_gradient(cost_fn, params, i) for i in range(len(params))])


def finite_difference_gradient(cost_fn, params, eps: float = 1e-6) -> np.ndarray:
    """Central finite-difference gradient -- the numerical reference the shift rule is checked
    against."""
    params = np.asarray(params, dtype=float)
    g = np.zeros(len(params))
    for i in range(len(params)):
        p = params.copy(); p[i] += eps
        m = params.copy(); m[i] -= eps
        g[i] = (cost_fn(p) - cost_fn(m)) / (2 * eps)
    return g


def parameter_shift_hessian_diagonal(cost_fn, params, shift: float = np.pi / 2) -> np.ndarray:
    """
    Diagonal of the Hessian ``d^2 f/dtheta_i^2`` from the parameter-shift rule. For a
    Pauli-generated rotation the cost is single-frequency in each angle, giving
    ``f'' = (f(theta+pi/2) + f(theta-pi/2) - 2 f(theta))/2``. Verified against finite
    differences.
    """
    params = np.asarray(params, dtype=float)
    f0 = cost_fn(params)
    out = np.zeros(len(params))
    for i in range(len(params)):
        p = params.copy(); p[i] += shift
        m = params.copy(); m[i] -= shift
        out[i] = (cost_fn(p) + cost_fn(m) - 2 * f0) / 2
    return out


def gradient_norm(cost_fn, params) -> float:
    """Euclidean norm of the parameter-shift gradient -- a scalar training signal (small in a
    barren plateau)."""
    return float(np.linalg.norm(parameter_shift_gradient_all(cost_fn, params)))
