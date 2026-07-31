"""
Quantum annealing.

Quantum annealing is the physical realization of adiabatic optimization used by hardware
like D-Wave: anneal a Hamiltonian ``H(s) = A(s) (-sum X_i) + B(s) H_problem`` from a strong
transverse field (``A`` large, ``B`` small) to the pure problem Hamiltonian (``A=0``,
``B`` large), with ``s`` running ``0 -> 1``. Slow anneals end in the problem's ground state;
fast anneals leave residual excitation. This module builds the anneal Hamiltonian with a
tunable schedule, runs the anneal, and reports the success probability -- verified to
increase toward 1 with anneal time and to recover the exact spin-glass ground state.
"""

import numpy as np

from .adiabatic_optimization import transverse_field_driver, adiabatic_evolve
from .qubo import ising_hamiltonian, brute_force_ising


def anneal_hamiltonian(ising_h, ising_J, s: float,
                       A=lambda s: 1 - s, B=lambda s: s) -> np.ndarray:
    """
    Anneal Hamiltonian ``A(s) (-sum X_i) + B(s) H_Ising`` at anneal fraction ``s``. Default
    linear schedule ``A(s)=1-s``, ``B(s)=s``.
    """
    n = len(ising_h)
    return A(s) * transverse_field_driver(n) + B(s) * ising_hamiltonian(ising_h, ising_J)


def anneal(ising_h, ising_J, total_time: float, steps: int = 200) -> np.ndarray:
    """
    Run a linear-schedule quantum anneal for an Ising problem, returning the final state.
    Starts in ``|+>^n`` (transverse-field ground state) and ends near the Ising ground state
    for a slow enough anneal.
    """
    n = len(ising_h)
    H0 = transverse_field_driver(n)
    H1 = ising_hamiltonian(ising_h, ising_J)
    return adiabatic_evolve(H0, H1, total_time, steps)


def annealing_success_probability(ising_h, ising_J, total_time: float, steps: int = 200) -> float:
    """
    Probability the anneal ends in the true Ising ground state -- verified to rise toward 1 as
    ``total_time`` increases.
    """
    psi = anneal(ising_h, ising_J, total_time, steps)
    diag = np.real(np.diag(ising_hamiltonian(ising_h, ising_J)))
    ground_indices = np.where(np.isclose(diag, diag.min()))[0]
    return float(sum(abs(psi[i]) ** 2 for i in ground_indices))


def annealed_solution(ising_h, ising_J, total_time: float, steps: int = 200):
    """
    The most probable spin configuration after annealing, as ``(+/-1)`` spins. Verified to
    match the brute-force Ising ground state for a slow anneal.
    """
    psi = anneal(ising_h, ising_J, total_time, steps)
    n = len(ising_h)
    b = int(np.argmax(np.abs(psi) ** 2))
    return np.array([1 - 2 * ((b >> i) & 1) for i in range(n)])


def spectral_gap_at(ising_h, ising_J, s: float) -> float:
    """The instantaneous ground-to-first-excited gap of the anneal Hamiltonian at fraction
    ``s`` -- the quantity that sets a safe anneal time."""
    w = np.linalg.eigvalsh(anneal_hamiltonian(ising_h, ising_J, s))
    return float(w[1] - w[0])
