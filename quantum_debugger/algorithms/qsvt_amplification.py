"""
Amplitude amplification and Chebyshev approximation -- the amplitude-space and
approximation-theory sides of QSVT.

* **Amplitude amplification** is QSVT applied to a *scalar* amplitude. If a state
  has success amplitude ``a = sin(theta)`` on the "good" subspace, interleaving the
  two reflections (Grover's operator) rotates it to ``sin((2k+1) theta)`` after ``k``
  steps -- an odd Chebyshev-type polynomial of ``a`` that QSVT reproduces. This
  module gives the amplified amplitude / optimal step count and verifies them against
  an explicit two-dimensional reflection simulation.

* **Chebyshev approximation** is the classical engine underneath every QSVT matrix
  function: the near-minimax polynomial that a QSP phase sequence realizes. The
  utility here returns the polynomial and its max-norm error and demonstrates the
  geometric convergence that makes the whole framework efficient.
"""

import numpy as np
from numpy.polynomial import chebyshev as _cheb


def amplitude_amplification_qsvt(a: float, iterations: int) -> dict:
    """
    Amplitude amplification as scalar QSVT. Starting from success amplitude
    ``a = sin(theta)``, ``k`` Grover steps produce amplitude ``sin((2k+1) theta)`` -- an
    odd degree-``(2k+1)`` polynomial of ``a``. Returns the amplified amplitude, success
    probability, and the step count that maximizes it (``~pi/(4 theta)``).

    Verified against an explicit simulation of the two reflections on the
    good/bad plane (see the tests): the analytic amplitude matches the simulated one to
    machine precision.
    """
    a = float(np.clip(a, -1.0, 1.0))
    theta = np.arcsin(abs(a))
    amp = np.sin((2 * iterations + 1) * theta)
    optimal = 0 if theta == 0 else int(round((np.pi / (2 * theta) - 1) / 2))
    return {
        "amplitude": float(amp),
        "probability": float(amp**2),
        "theta": float(theta),
        "optimal_iterations": max(optimal, 0),
    }


def grover_amplitude_simulated(a: float, iterations: int) -> float:
    """
    Directly simulate ``iterations`` steps of the amplitude-amplification operator
    ``G = -R_start R_good`` on the two-dimensional good/bad plane and return the good
    amplitude -- the reference that :func:`amplitude_amplification_qsvt` is checked
    against. ``|start> = a|good> + sqrt(1-a^2)|bad>``.
    """
    a = float(np.clip(a, -1.0, 1.0))
    good = np.array([1.0, 0.0])
    start = np.array([a, np.sqrt(1 - a**2)])
    R_good = np.eye(2) - 2 * np.outer(good, good)          # flip sign of |good>
    R_start = np.eye(2) - 2 * np.outer(start, start)       # reflect about |start>
    G = -R_start @ R_good
    psi = start.copy()
    for _ in range(iterations):
        psi = G @ psi
    return float(psi[0])


def chebyshev_approximation(func, degree: int, domain=(-1.0, 1.0)):
    """
    Near-minimax Chebyshev approximation of ``func`` on ``domain`` -- the classical
    polynomial a QSP phase sequence realizes and QSVT applies to a matrix. Returns a
    dict with the ``poly`` callable, its Chebyshev ``coeffs``, and the ``max_error`` on a
    dense grid. For analytic ``func`` the error falls geometrically with ``degree``
    (verified in the tests), which is exactly why QSVT is efficient.
    """
    a, b = domain
    nodes = np.cos(np.pi * (np.arange(degree + 1) + 0.5) / (degree + 1))
    xs_fit = ((b - a) * nodes + (a + b)) / 2
    coeffs = _cheb.chebfit(nodes, func(xs_fit), degree)

    def poly(x):
        t = (2 * np.asarray(x, dtype=float) - (a + b)) / (b - a)
        return _cheb.chebval(t, coeffs)

    grid = np.linspace(a, b, 2000)
    max_error = float(np.max(np.abs(poly(grid) - func(grid))))
    return {"poly": poly, "coeffs": coeffs, "max_error": max_error}
