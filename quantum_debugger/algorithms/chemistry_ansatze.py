"""
Particle-number-conserving ansätze for electronic-structure VQE.

Chemistry ansätze must respect the physics: the number of electrons is fixed, so every
gate should commute with the total number operator ``N``. This module builds the
standard family on top of the :mod:`fermion_mappings` operators:

* the **Hartree-Fock** reference determinant (the classical mean-field starting point),
* **Givens rotations** ``exp(theta (a_p^d a_q - a_q^d a_p))`` -- orbital-rotation
  single excitations that stay in the fixed-particle subspace,
* the **UCCSD** cluster unitary ``exp(T - T^dagger)`` with single and double
  excitations -- the workhorse chemistry ansatz.

Each construction is verified to be unitary and to conserve the particle number
(``[U, N] = 0``); the UCCSD/Givens circuits keep a Hartree-Fock input at exactly the
right electron count.
"""

import numpy as np
from scipy.linalg import expm

from .fermion_mappings import jordan_wigner_annihilation
from .molecular_hamiltonian import number_operator


def hartree_fock_state(n_orbitals: int, n_electrons: int) -> np.ndarray:
    """
    Hartree-Fock reference determinant: the computational-basis state with the lowest
    ``n_electrons`` spin-orbitals occupied (little-endian, orbital 0 = least significant).
    The classical starting point for every chemistry VQE.
    """
    idx = sum(1 << j for j in range(n_electrons))
    psi = np.zeros(2 ** n_orbitals, dtype=complex)
    psi[idx] = 1.0
    return psi


def givens_rotation(theta: float, p: int, q: int, n: int) -> np.ndarray:
    """
    Orbital-rotation (Givens) gate ``exp(theta (a_p^dagger a_q - a_q^dagger a_p))`` on
    ``n`` spin-orbitals -- a particle-conserving single-excitation rotation between
    orbitals ``p`` and ``q``. Verified unitary and commuting with ``N``.
    """
    a = [jordan_wigner_annihilation(j, n) for j in range(n)]
    kappa = a[p].conj().T @ a[q] - a[q].conj().T @ a[p]
    return expm(theta * kappa)


def uccsd_operator(singles, doubles, n: int) -> np.ndarray:
    """
    Unitary Coupled-Cluster Singles and Doubles operator ``exp(T - T^dagger)`` on ``n``
    spin-orbitals. ``singles`` is a list of ``(theta, p, q)`` (excitation
    ``a_p^d a_q``) and ``doubles`` a list of ``(theta, p, q, r, s)`` (excitation
    ``a_p^d a_q^d a_r a_s``). The resulting operator is unitary and conserves particle
    number. Verified against both properties.
    """
    a = [jordan_wigner_annihilation(j, n) for j in range(n)]
    dim = 2 ** n
    T = np.zeros((dim, dim), dtype=complex)
    for theta, p, q in singles:
        T += theta * (a[p].conj().T @ a[q])
    for theta, p, q, r, s in doubles:
        T += theta * (a[p].conj().T @ a[q].conj().T @ a[r] @ a[s])
    return expm(T - T.conj().T)


def conserves_particle_number(op, n: int, atol: float = 1e-9) -> bool:
    """True iff ``[op, N] = 0`` -- the operator keeps the electron count fixed."""
    N = number_operator(n)
    op = np.asarray(op)
    return np.allclose(op @ N - N @ op, 0, atol=atol)


def is_unitary(op, atol: float = 1e-9) -> bool:
    """True iff ``op^dagger op = I``."""
    op = np.asarray(op)
    return np.allclose(op.conj().T @ op, np.eye(op.shape[0]), atol=atol)


def apply_ansatz(reference, operator) -> np.ndarray:
    """Apply an ansatz ``operator`` to a ``reference`` state, returning the new state."""
    return np.asarray(operator) @ np.asarray(reference)
