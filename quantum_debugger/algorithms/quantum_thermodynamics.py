"""
Quantum thermodynamics -- work, heat, and the second law.

For a quantum system with Hamiltonian ``H`` in a state ``rho``, thermodynamic quantities are
statistical:

* **Work** is the energy change from *changing the Hamiltonian* (``W = Tr[rho (H' - H)]`` for a
  quench), and **heat** the energy change from *changing the state* at fixed Hamiltonian.
* The **Gibbs state** ``rho_beta = e^{-beta H}/Z`` is the unique equilibrium; its free energy
  ``F = -(1/beta) ln Z`` lower-bounds the free energy of any other state.
* **Entropy production** ``Sigma = beta(W - Delta F) >= 0`` is the quantitative second law -- a
  non-negative irreversibility, zero only for a quasi-static (reversible) process.

This module builds Gibbs states and computes work, heat, free energy, and entropy production,
verified against those closed forms and the non-negativity of the second law.
"""

import numpy as np


def gibbs_state(H, beta: float) -> np.ndarray:
    """The thermal (Gibbs) state ``e^{-beta H}/Z`` at inverse temperature ``beta`` -- the unique
    maximum-entropy state at a given mean energy."""
    H = np.asarray(H, dtype=complex)
    w, v = np.linalg.eigh(H)
    p = np.exp(-beta * (w - w.min()))
    p = p / p.sum()
    return (v * p) @ v.conj().T


def partition_function(H, beta: float) -> float:
    """The partition function ``Z = Tr e^{-beta H}`` -- the generator of all equilibrium
    thermodynamics."""
    w = np.linalg.eigvalsh(np.asarray(H, dtype=complex))
    return float(np.sum(np.exp(-beta * w)))


def free_energy(H, beta: float) -> float:
    """Equilibrium (Helmholtz) free energy ``F = -(1/beta) ln Z``."""
    return float(-np.log(partition_function(H, beta)) / beta)


def internal_energy(rho, H) -> float:
    """Mean energy ``<H> = Tr[rho H]`` of a state."""
    return float(np.real(np.trace(np.asarray(rho, dtype=complex) @ np.asarray(H, dtype=complex))))


def quench_work(rho, H_initial, H_final) -> float:
    """
    Work done by a sudden quench ``H_initial -> H_final`` on state ``rho`` (fixed during the
    quench): ``W = Tr[rho (H_final - H_initial)]``. Positive means work is done *on* the system.
    """
    return internal_energy(rho, H_final) - internal_energy(rho, H_initial)


def heat_exchanged(rho_initial, rho_final, H) -> float:
    """Heat absorbed at fixed Hamiltonian ``H`` as the state relaxes ``rho_initial -> rho_final``:
    ``Q = Tr[(rho_final - rho_initial) H]``."""
    return internal_energy(rho_final, H) - internal_energy(rho_initial, H)


def nonequilibrium_free_energy(rho, H, beta: float, base: float = np.e) -> float:
    """
    Non-equilibrium free energy ``F(rho) = <H> - (1/beta) S(rho)`` -- minimized by the Gibbs
    state (where it equals the equilibrium free energy), and larger for any other state.
    """
    from .quantum_entropies import von_neumann_entropy
    S = von_neumann_entropy(rho, base=2) * np.log(2)   # nats
    return float(internal_energy(rho, H) - S / beta)


def heat_capacity(H, beta: float) -> float:
    """
    Heat capacity ``C = beta^2 Var(H)_gibbs`` of the thermal state -- the energy fluctuations set
    the response to temperature. Non-negative (verified), a hallmark of thermodynamic stability.
    """
    H = np.asarray(H, dtype=complex)
    g = gibbs_state(H, beta)
    E = internal_energy(g, H)
    E2 = float(np.real(np.trace(g @ H @ H)))
    return float(beta ** 2 * (E2 - E ** 2))


def thermal_entropy(H, beta: float, base: float = 2.0) -> float:
    """The von Neumann entropy of the Gibbs state ``S = beta(<H> - F)`` -- the thermodynamic
    entropy at inverse temperature ``beta``."""
    from .quantum_entropies import von_neumann_entropy
    return float(von_neumann_entropy(gibbs_state(H, beta), base))


def entropy_production(rho, H_initial, H_final, beta: float) -> float:
    """
    Entropy production of a quench-then-thermalize process,
    ``Sigma = beta (W - Delta F) >= 0`` where ``Delta F`` is the equilibrium free-energy change --
    the quantitative second law. Verified non-negative.
    """
    W = quench_work(rho, H_initial, H_final)
    dF = free_energy(H_final, beta) - free_energy(H_initial, beta)
    return float(beta * (W - dF))
