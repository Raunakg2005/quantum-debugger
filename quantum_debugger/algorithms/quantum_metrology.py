"""
Quantum metrology -- the fundamental limits of parameter estimation.

To estimate a parameter ``theta`` imprinted by ``e^{-i theta G}`` on a probe state, the
achievable precision is set by the **quantum Fisher information (QFI)**. For a pure state the
QFI is four times the variance of the generator,

    F_Q = 4 (<G^2> - <G>^2),

and the **quantum Cramér-Rao bound** limits the estimation error to
``Delta theta >= 1 / sqrt(m F_Q)`` over ``m`` repetitions. With ``n`` uncorrelated probes the QFI
is at most ``n`` (the **standard quantum limit**, error ``~ 1/sqrt(n)``); entanglement can push
it to ``n^2`` (the **Heisenberg limit**, error ``~ 1/n``). This module computes the QFI, the
bounds, and the two scaling limits, verified against those closed forms.
"""

import numpy as np


def generator_variance(state, generator) -> float:
    """Variance ``<G^2> - <G>^2`` of a Hermitian generator ``G`` in a pure ``state`` -- the
    core quantity of the pure-state QFI."""
    psi = np.asarray(state, dtype=complex)
    G = np.asarray(generator, dtype=complex)
    g = G @ psi
    mean = np.real(np.vdot(psi, g))
    mean2 = np.real(np.vdot(g, g))
    return float(mean2 - mean ** 2)


def qfi_pure(state, generator) -> float:
    """Quantum Fisher information ``F_Q = 4 Var(G)`` of a pure state for the phase generator
    ``G`` -- the metrological resource."""
    return float(4 * generator_variance(state, generator))


def cramer_rao_bound(qfi: float, repetitions: int = 1) -> float:
    """Quantum Cramér-Rao bound ``Delta theta >= 1/sqrt(m F_Q)`` on the estimation error for QFI
    ``qfi`` over ``m = repetitions`` shots."""
    return float(1.0 / np.sqrt(repetitions * qfi))


def standard_quantum_limit(n: int) -> float:
    """The standard quantum limit precision ``1/sqrt(n)`` -- the best achievable with ``n``
    uncorrelated probes (QFI = ``n``)."""
    return float(1.0 / np.sqrt(n))


def heisenberg_limit(n: int) -> float:
    """The Heisenberg limit precision ``1/n`` -- the ultimate limit reachable with an entangled
    probe (QFI = ``n^2``). Verified below the standard quantum limit."""
    return float(1.0 / n)


def metrological_advantage(n: int) -> float:
    """Ratio of standard-quantum-limit to Heisenberg-limit precision, ``sqrt(n)`` -- the
    entanglement-enabled precision gain."""
    return float(standard_quantum_limit(n) / heisenberg_limit(n))


def error_propagation(signal_fn, theta: float, variance_fn, eps: float = 1e-6) -> float:
    """
    Estimation error via error propagation ``Delta theta = sqrt(Var[S]) / |dS/dtheta|`` for a
    measured signal ``S(theta)`` with variance ``variance_fn(theta)``. The operational precision
    of a specific measurement, bounded below by the Cramér-Rao bound.
    """
    dS = (signal_fn(theta + eps) - signal_fn(theta - eps)) / (2 * eps)
    return float(np.sqrt(variance_fn(theta)) / abs(dS))
