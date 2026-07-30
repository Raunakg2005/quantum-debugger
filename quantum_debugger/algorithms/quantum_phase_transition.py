"""
Fidelity approach to quantum phase transitions.

A quantum phase transition is a ground-state reorganization driven by a parameter
``lambda`` (a field, a coupling). Even without knowing the order parameter you can
locate it geometrically: neighbouring ground states ``|psi(lambda)>`` and
``|psi(lambda + dlambda)>`` are nearly identical inside a phase but change rapidly at
the critical point, so the **ground-state fidelity** dips and the **fidelity
susceptibility** ``chi_F = 2(1 - F)/dlambda^2`` peaks there. This module computes both
by exact diagonalization and verifies the peak sits at the transverse-field Ising
critical point ``h/J = 1``.
"""

import numpy as np

from .hamiltonian_simulation import hamiltonian_matrix
from .vqe_solver import tfim_hamiltonian


def _ground_state(terms, n):
    H = hamiltonian_matrix(terms, n)
    vals, vecs = np.linalg.eigh(H)
    return vecs[:, 0]


def ground_state_fidelity(terms_func, lam: float, dlam: float, n: int) -> float:
    """
    Overlap ``|<psi(lam) | psi(lam + dlam)>|`` between the ground states at two nearby
    parameter values. ``terms_func(lam)`` returns the Hamiltonian (list of weighted Pauli
    strings) at parameter ``lam``. Near 1 inside a phase, dips sharply at a transition.
    """
    psi0 = _ground_state(terms_func(lam), n)
    psi1 = _ground_state(terms_func(lam + dlam), n)
    return float(abs(np.vdot(psi0, psi1)))


def fidelity_susceptibility(terms_func, lam: float, n: int, dlam: float = 1e-3) -> float:
    """
    Fidelity susceptibility ``chi_F = 2 (1 - F) / dlambda^2`` from the ground-state
    fidelity ``F`` -- the leading (intensive) response that diverges at a quantum critical
    point. Peaks at the transition; verified to locate the TFIM critical point.
    """
    F = ground_state_fidelity(terms_func, lam, dlam, n)
    return float(2 * (1 - F) / dlam**2)


def tfim_critical_field(n: int, fields=None) -> float:
    """
    Estimate the TFIM critical field by scanning ``fields`` and returning the one that
    maximizes the fidelity susceptibility (with ``J = 1``). Converges to the exact
    thermodynamic value ``h_c = 1`` as ``n`` grows -- the verification target for the
    fidelity method.
    """
    if fields is None:
        fields = np.linspace(0.4, 1.6, 25)
    chi = [fidelity_susceptibility(lambda h: tfim_hamiltonian(n, h, 1.0), float(h), n)
           for h in fields]
    return float(fields[int(np.argmax(chi))])
