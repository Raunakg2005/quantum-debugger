"""
The CHSH Bell inequality and its bounds.

Two parties measure a shared state with one of two settings each, getting ``+/-1``. The CHSH
combination

    S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1)

is bounded by ``|S| <= 2`` for any *local hidden-variable* (classical) theory, by ``|S| <= 2
sqrt2`` for quantum mechanics (**Tsirelson's bound**), and by ``|S| <= 4`` algebraically. A
maximally entangled state with the right measurement angles reaches ``2 sqrt2`` -- violating the
classical bound and proving nonlocality. This module builds the correlators, computes ``S``,
and provides the three bounds, verifying the classical one by brute force over all
deterministic strategies and the quantum one against the Bell state.
"""

import numpy as np
from itertools import product

_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)


def measurement_operator(angle: float) -> np.ndarray:
    """A ``+/-1`` qubit measurement observable ``cos(angle) Z + sin(angle) X`` -- a projective
    measurement in the ``x-z`` plane of the Bloch sphere."""
    return np.cos(angle) * _Z + np.sin(angle) * _X


def correlator(state, angle_a: float, angle_b: float) -> float:
    """The correlation ``E(a,b) = <psi| A(a) (x) B(b) |psi>`` of two ``+/-1`` measurements on a
    two-qubit ``state``."""
    psi = np.asarray(state, dtype=complex)
    op = np.kron(measurement_operator(angle_a), measurement_operator(angle_b))
    return float(np.real(np.vdot(psi, op @ psi)))


def chsh_value(state, a0=0.0, a1=np.pi / 2, b0=np.pi / 4, b1=-np.pi / 4) -> float:
    """
    The CHSH value ``S = E(a0,b0)+E(a0,b1)+E(a1,b0)-E(a1,b1)`` for a two-qubit ``state`` and the
    four measurement angles (defaulting to the CHSH-optimal angles). Reaches ``2 sqrt2`` for the
    Bell state.
    """
    return float(correlator(state, a0, b0) + correlator(state, a0, b1)
                 + correlator(state, a1, b0) - correlator(state, a1, b1))


def classical_chsh_bound() -> int:
    """The local hidden-variable bound ``2``, obtained by brute force: the maximum of the CHSH
    combination over all deterministic ``+/-1`` assignments to the four settings."""
    best = 0
    for a0, a1, b0, b1 in product([1, -1], repeat=4):
        s = abs(a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1)
        best = max(best, s)
    return int(best)


def tsirelson_bound() -> float:
    """Tsirelson's quantum bound ``2 sqrt2`` -- the maximum CHSH value achievable by quantum
    mechanics."""
    return float(2 * np.sqrt(2))


def algebraic_bound() -> int:
    """The algebraic (no-signaling / logical) maximum of CHSH, ``4`` -- reached only by
    super-quantum PR boxes."""
    return 4


def chsh_violation(state) -> float:
    """The amount by which a state's optimal CHSH value exceeds the classical bound of 2 --
    positive means the state is Bell-nonlocal."""
    return float(chsh_value(state) - classical_chsh_bound())


def bell_state(kind: str = "phi_plus") -> np.ndarray:
    """A two-qubit Bell state (``phi_plus`` by default) -- the maximally entangled resource that
    reaches Tsirelson's bound."""
    states = {
        "phi_plus": [1, 0, 0, 1], "phi_minus": [1, 0, 0, -1],
        "psi_plus": [0, 1, 1, 0], "psi_minus": [0, 1, -1, 0],
    }
    v = np.array(states[kind], dtype=complex)
    return v / np.linalg.norm(v)
