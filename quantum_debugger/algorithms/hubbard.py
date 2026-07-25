"""
The Fermi-Hubbard model (via Jordan-Wigner)

The simplest model of interacting electrons on a lattice:

    H = -t sum_{<i,j>, s} (c_{i,s}-dagger c_{j,s} + h.c.) + U sum_i n_{i,up} n_{i,down},

a kinetic hopping term (strength ``t``) competing with an on-site Coulomb repulsion
(``U``). Built here on qubits through the :mod:`jordan_wigner` transform, with two
spin-orbitals per site (mode ``2i`` = site ``i`` spin-up, ``2i+1`` = spin-down).

The half-filled two-site "dimer" is exactly solvable, and its singlet ground-state
energy

    E_0 = ( U - sqrt(U^2 + 16 t^2) ) / 2

interpolates between the non-interacting bonding energy ``-2t`` (``U = 0``) and the
Heisenberg antiferromagnet ``-4 t^2 / U`` at large ``U`` -- the Mott transition in
miniature. This module reproduces that curve exactly from the many-body spectrum.
"""

import numpy as np

from .jordan_wigner import jw_annihilation, jw_creation, jw_number, jw_total_number


def fermi_hubbard_hamiltonian(
    n_sites: int, t: float = 1.0, u: float = 0.0, periodic: bool = False
) -> np.ndarray:
    """
    Fermi-Hubbard Hamiltonian on ``n_sites`` sites (``2 * n_sites`` spin-orbitals) as
    a dense ``2**(2 n_sites) x 2**(2 n_sites)`` matrix. Hopping ``t`` links same-spin
    orbitals on neighbouring sites (a ring if ``periodic``); ``u`` is the on-site
    repulsion between opposite spins.
    """
    n_modes = 2 * n_sites
    dim = 2**n_modes
    H = np.zeros((dim, dim), dtype=complex)

    bonds = n_sites if periodic else n_sites - 1
    for i in range(bonds):
        j = (i + 1) % n_sites
        for spin in (0, 1):
            a_i, a_j = 2 * i + spin, 2 * j + spin
            term = jw_creation(a_i, n_modes) @ jw_annihilation(a_j, n_modes)
            H += -t * (term + term.conj().T)

    for i in range(n_sites):
        H += u * (jw_number(2 * i, n_modes) @ jw_number(2 * i + 1, n_modes))

    return H


def hubbard_ground_energy(
    n_sites: int, t: float = 1.0, u: float = 0.0, n_particles=None, periodic: bool = False
) -> float:
    """
    Ground-state energy of the Fermi-Hubbard model, optionally within a fixed
    particle-number sector ``n_particles`` (default: over all sectors, which for
    ``u >= 0`` is the empty lattice, energy 0 -- so pass ``n_particles = n_sites`` for
    the physically interesting half-filled case).
    """
    H = fermi_hubbard_hamiltonian(n_sites, t, u, periodic)
    if n_particles is None:
        return float(np.linalg.eigvalsh(H).real.min())
    N = jw_total_number(2 * n_sites)
    sector = [k for k in range(H.shape[0]) if abs(np.real(N[k, k]) - n_particles) < 1e-9]
    return float(np.linalg.eigvalsh(H[np.ix_(sector, sector)]).real.min())


def hubbard_dimer_energy(t: float = 1.0, u: float = 0.0) -> dict:
    """
    The exactly-solvable half-filled two-site Hubbard dimer.

    Returns dict with ``ground_energy`` (from the many-body spectrum), ``analytic``
    (``(U - sqrt(U^2 + 16 t^2)) / 2``), and ``heisenberg_limit`` (``-4 t^2 / U``, the
    large-``U`` antiferromagnetic exchange the ground energy approaches).
    """
    e0 = hubbard_ground_energy(2, t, u, n_particles=2)
    analytic = (u - np.sqrt(u**2 + 16 * t**2)) / 2
    return {
        "ground_energy": e0,
        "analytic": float(analytic),
        "heisenberg_limit": float(-4 * t**2 / u) if u > 0 else float("-inf"),
    }
