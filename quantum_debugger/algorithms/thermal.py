"""
Gibbs (thermal) states & quantum thermodynamics

At inverse temperature ``beta = 1/(k_B T)`` a system with Hamiltonian ``H`` settles
into the Gibbs state

    rho(beta) = e^{-beta H} / Z,      Z = Tr e^{-beta H},

the maximum-entropy state at fixed average energy. From it follow the standard
thermodynamic potentials, all exact and mutually consistent (verified here):

  * internal energy ``E = Tr(rho H)``,
  * von Neumann entropy ``S = -Tr(rho ln rho)`` (in nats),
  * Helmholtz free energy ``F = -ln(Z)/beta = E - S/beta`` (i.e. ``F = E - T S``),
  * heat capacity ``C = beta^2 (Tr(rho H^2) - E^2)`` (energy-fluctuation form).

Limits: ``beta -> 0`` gives the maximally mixed state ``I/d`` (infinite temperature),
``beta -> infinity`` projects onto the ground state. Applied to the Fermi-Hubbard or
molecular Hamiltonians, this gives their finite-temperature physics.
"""

import numpy as np
from scipy.linalg import expm


def gibbs_state(hamiltonian, beta: float) -> np.ndarray:
    """
    Thermal (Gibbs) density matrix ``e^{-beta H} / Z`` for Hamiltonian ``hamiltonian``
    at inverse temperature ``beta``. Returns the normalized density matrix.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    unnorm = expm(-beta * H)
    return unnorm / np.trace(unnorm).real


def partition_function(hamiltonian, beta: float) -> float:
    """Partition function ``Z = Tr e^{-beta H}``."""
    H = np.asarray(hamiltonian, dtype=complex)
    return float(np.real(np.trace(expm(-beta * H))))


def thermal_properties(hamiltonian, beta: float) -> dict:
    """
    Full thermodynamic summary of the Gibbs state at inverse temperature ``beta``.

    Returns dict with ``energy`` (``E``), ``entropy`` (``S``, nats), ``free_energy``
    (``F = -ln Z / beta``), ``heat_capacity`` (``C``), and ``free_energy_check``
    (``E - S/beta``, equal to ``free_energy``).
    """
    H = np.asarray(hamiltonian, dtype=complex)
    rho = gibbs_state(H, beta)

    energy = float(np.real(np.trace(rho @ H)))
    energy2 = float(np.real(np.trace(rho @ H @ H)))
    vals = np.linalg.eigvalsh(rho).real
    vals = vals[vals > 1e-14]
    entropy = float(-np.sum(vals * np.log(vals)))
    free_energy = -np.log(partition_function(H, beta)) / beta
    heat_capacity = beta**2 * (energy2 - energy**2)

    return {
        "energy": energy,
        "entropy": entropy,
        "free_energy": float(free_energy),
        "heat_capacity": float(heat_capacity),
        "free_energy_check": energy - entropy / beta,
    }
