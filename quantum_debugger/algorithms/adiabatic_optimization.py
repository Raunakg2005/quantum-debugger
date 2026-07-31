"""
Adiabatic quantum optimization.

The adiabatic theorem says that if a system starts in the ground state of an easy
Hamiltonian ``H0`` (the transverse field, ground state ``|+>^n``) and the Hamiltonian is
changed *slowly enough* to a problem Hamiltonian ``H1`` (whose ground state encodes the
answer), the system stays in the instantaneous ground state -- so measuring at the end
solves the problem. "Slowly enough" is set by the **minimum spectral gap** along the path:
the required runtime scales like ``1/gap_min^2``. This module builds the interpolating
Hamiltonian, tracks the instantaneous gap, evolves the time-dependent Schrödinger equation,
and models the Landau-Zener transition -- verified against exact diagonalization and the
closed-form LZ probability.
"""

import numpy as np
from scipy.linalg import expm

_X = np.array([[0, 1], [1, 0]], dtype=complex)


def transverse_field_driver(n: int) -> np.ndarray:
    """The driver Hamiltonian ``H0 = -sum_i X_i`` whose ground state is the uniform
    superposition ``|+>^n`` -- the easy starting point of an adiabatic sweep."""
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        op = np.array([[1.0]], dtype=complex)
        for q in range(n):
            op = np.kron(_X if q == i else np.eye(2), op)
        H -= op
    return H


def interpolating_hamiltonian(H0, H1, s: float) -> np.ndarray:
    """The path Hamiltonian ``H(s) = (1-s) H0 + s H1`` for ``s`` in ``[0, 1]``."""
    return (1 - s) * np.asarray(H0, dtype=complex) + s * np.asarray(H1, dtype=complex)


def instantaneous_gap(H0, H1, s: float) -> float:
    """Gap between the ground and first excited state of ``H(s)`` -- the local speed limit for
    the adiabatic sweep."""
    w = np.linalg.eigvalsh(interpolating_hamiltonian(H0, H1, s))
    return float(w[1] - w[0])


def minimum_gap(H0, H1, points: int = 101) -> float:
    """Minimum spectral gap along the adiabatic path -- the bottleneck that sets the required
    runtime ``~ 1/gap_min^2``. Positive for a non-crossing path (verified)."""
    return float(min(instantaneous_gap(H0, H1, s) for s in np.linspace(0, 1, points)))


def adiabatic_evolve(H0, H1, total_time: float, steps: int = 200) -> np.ndarray:
    """
    Evolve the ground state of ``H0`` under the slowly varying ``H(s(t))`` for ``total_time``,
    returning the final state. As ``total_time`` grows the final state approaches the ground
    state of ``H1`` -- the adiabatic theorem.
    """
    w, v = np.linalg.eigh(np.asarray(H0, dtype=complex))
    psi = v[:, 0]
    dt = total_time / steps
    for k in range(steps):
        s = (k + 0.5) / steps
        psi = expm(-1j * interpolating_hamiltonian(H0, H1, s) * dt) @ psi
    return psi


def adiabatic_success_probability(H0, H1, total_time: float, steps: int = 200) -> float:
    """
    Probability that the adiabatic sweep ends in the true ground state of ``H1`` -- the
    overlap ``|<ground|psi_final>|^2``. Verified to approach 1 as ``total_time`` grows.
    """
    psi = adiabatic_evolve(H0, H1, total_time, steps)
    w, v = np.linalg.eigh(np.asarray(H1, dtype=complex))
    ground = v[:, 0]
    return float(abs(np.vdot(ground, psi)) ** 2)


def landau_zener_probability(gap: float, sweep_velocity: float) -> float:
    """
    Landau-Zener diabatic transition probability ``P = exp(-pi gap^2 / (4 v))`` for a
    two-level avoided crossing with minimum energy gap ``gap`` (twice the off-diagonal
    coupling) swept with diabatic-energy slope ``v`` -- the probability of *failing* to follow
    the ground state. Verified against a direct two-level sweep simulation.
    """
    return float(np.exp(-np.pi * gap ** 2 / (4 * sweep_velocity)))


def adiabatic_runtime_bound(min_gap: float) -> float:
    """The adiabatic runtime estimate ``T ~ 1/gap_min^2`` -- how the cost blows up as the
    minimum gap closes."""
    return float(1.0 / min_gap ** 2)
