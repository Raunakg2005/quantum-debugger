"""
Passive states and ergotropy -- the extractable work in a quantum state.

Not all of a state's energy can be extracted as work by a cyclic (unitary) process. A state is
**passive** when no unitary can lower its energy -- which happens exactly when its populations are
sorted in *decreasing* order against *increasing* energy levels (higher population on lower
energy). The maximal work extractable by a unitary is the **ergotropy**

    W_erg = Tr[rho H] - Tr[rho_passive H] ,

where ``rho_passive`` has ``rho``'s eigenvalues rearranged into passive order. Gibbs states are
completely passive (zero ergotropy even with many copies). This module builds the passive
rearrangement, computes the ergotropy, and verifies it is non-negative and zero for passive /
thermal states.
"""

import numpy as np


def passive_state(rho, H) -> np.ndarray:
    """
    The passive counterpart of ``rho`` for Hamiltonian ``H``: the same eigenvalue spectrum
    rearranged so the largest populations sit on the lowest energy levels. No unitary can extract
    work from it.
    """
    rho = np.asarray(rho, dtype=complex)
    H = np.asarray(H, dtype=complex)
    pops = np.sort(np.real(np.linalg.eigvalsh(rho)))[::-1]     # descending populations
    energies, vecs = np.linalg.eigh(H)                         # ascending energies
    return (vecs * pops) @ vecs.conj().T


def ergotropy(rho, H) -> float:
    """
    Ergotropy: the maximum work extractable from ``rho`` by a cyclic unitary,
    ``Tr[rho H] - Tr[rho_passive H]``. Non-negative, and zero iff ``rho`` is already passive
    (verified).
    """
    H = np.asarray(H, dtype=complex)
    E = np.real(np.trace(np.asarray(rho, dtype=complex) @ H))
    Ep = np.real(np.trace(passive_state(rho, H) @ H))
    return float(E - Ep)


def is_passive(rho, H, atol: float = 1e-9) -> bool:
    """True iff ``rho`` is passive (zero ergotropy) -- no work extractable by any unitary."""
    return bool(ergotropy(rho, H) < atol)


def max_extractable_work(rho, H) -> float:
    """Alias for the ergotropy -- the most work a single copy of ``rho`` can yield to a unitary
    work source."""
    return ergotropy(rho, H)


def bound_energy(rho, H) -> float:
    """The bound (non-extractable) energy ``Tr[rho_passive H]`` -- the part of the mean energy no
    unitary can turn into work. Mean energy = ergotropy + bound energy."""
    return float(np.real(np.trace(passive_state(rho, H) @ np.asarray(H, dtype=complex))))


def gibbs_is_passive(H, beta: float, atol: float = 1e-9) -> bool:
    """Verify a Gibbs state is passive (zero ergotropy) -- the equilibrium state stores no
    extractable work."""
    from .quantum_thermodynamics import gibbs_state
    return is_passive(gibbs_state(H, beta), H, atol)
