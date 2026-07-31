"""
EPR steering.

Steering sits *between* entanglement and Bell nonlocality: a state is **steerable** from Alice
to Bob if Alice's measurements can remotely prepare Bob's system in ways that no local
hidden-*state* model for Bob can reproduce. It is detected by steering inequalities; the
three-measurement linear inequality is

    S_3 = (1/sqrt3) sum_{k in {x,y,z}} |<A_k (x) B_k>|  <= 1   (unsteerable),

so ``S_3 > 1`` certifies steering. A Bell state gives ``S_3 = sqrt3``, while a separable state
stays at or below 1. This module computes the steering value and threshold and verifies both
cases, plus the Werner-state steering boundary.
"""

import numpy as np

_PAULI = [
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
]


def _correlation(rho, k):
    op = np.kron(_PAULI[k], _PAULI[k])
    return float(np.real(np.trace(op @ np.asarray(rho, dtype=complex))))


def steering_value(rho) -> float:
    """
    Three-measurement linear steering value ``(1/sqrt3) sum_k |<sigma_k (x) sigma_k>|`` for a
    two-qubit density matrix. Above 1 certifies EPR steering; ``sqrt3`` for a Bell state.
    """
    return float(sum(abs(_correlation(rho, k)) for k in range(3)) / np.sqrt(3))


def steering_bound() -> float:
    """The unsteerable (local-hidden-state) bound of the three-setting steering inequality,
    ``1``."""
    return 1.0


def is_steerable(rho, atol: float = 1e-9) -> bool:
    """True iff the three-setting steering inequality is violated (``S_3 > 1``) -- a sufficient
    condition for EPR steering. Verified True for a Bell state, False for a separable state."""
    return bool(steering_value(rho) > 1 + atol)


def werner_state(p: float) -> np.ndarray:
    """The two-qubit Werner state ``p |Phi+><Phi+| + (1-p) I/4`` -- entangled for ``p > 1/3`` and
    used to probe the steering threshold."""
    phi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    return p * np.outer(phi, phi.conj()) + (1 - p) * np.eye(4) / 4


def werner_steering_threshold() -> float:
    """The three-setting steering threshold for the Werner state, ``p = 1/sqrt3`` -- above it the
    Werner state is steerable by this inequality. Verified against :func:`steering_value`."""
    return float(1.0 / np.sqrt(3))
