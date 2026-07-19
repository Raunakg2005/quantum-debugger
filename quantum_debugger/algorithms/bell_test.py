"""
Bell / CHSH Inequality Test

Demonstrates quantum nonlocality: a shared Bell pair measured along cleverly
chosen angles violates the classical CHSH bound ``|S| <= 2``, reaching Tsirelson's
quantum bound ``2 * sqrt(2) ~ 2.828``. No local hidden-variable theory can produce
this correlation.

Each party measures the observable ``M(theta) = cos(theta) Z + sin(theta) X``.
For the Bell state ``|Phi+>`` the correlator is ``E(a, b) = cos(a - b)``, and the
CHSH combination ``S = E(a,b) + E(a,b') + E(a',b) - E(a',b')`` is maximized at
``2 sqrt(2)`` (angles a=0, a'=pi/2, b=pi/4, b'=-pi/4).
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_Z = GateLibrary.Z
_X = GateLibrary.X


def bell_state() -> np.ndarray:
    """Return the Bell state |Phi+> = (|00> + |11>)/sqrt(2)."""
    state = QuantumState(2)
    state.apply_gate(GateLibrary.H, [0])
    state.apply_gate(GateLibrary.CNOT, [0, 1])
    return state.state_vector


def measurement_observable(theta: float) -> np.ndarray:
    """Single-qubit observable M(theta) = cos(theta) Z + sin(theta) X."""
    return np.cos(theta) * _Z + np.sin(theta) * _X


def correlator(psi: np.ndarray, a: float, b: float) -> float:
    """Expectation <psi| M(a) (x) M(b) |psi>."""
    M = np.kron(measurement_observable(a), measurement_observable(b))
    return float(np.real(np.vdot(psi, M @ psi)))


def chsh_value(
    a: float = 0.0,
    a_prime: float = np.pi / 2,
    b: float = np.pi / 4,
    b_prime: float = -np.pi / 4,
    psi: np.ndarray = None,
) -> dict:
    """
    Compute the CHSH correlator ``S`` for a Bell pair and the given angles.

    Returns dict with 'S', the four correlators, the classical bound (2), and
    Tsirelson's quantum bound (2 sqrt(2)). The default angles achieve |S| = 2 sqrt(2).
    """
    if psi is None:
        psi = bell_state()
    e_ab = correlator(psi, a, b)
    e_ab2 = correlator(psi, a, b_prime)
    e_a2b = correlator(psi, a_prime, b)
    e_a2b2 = correlator(psi, a_prime, b_prime)
    S = e_ab + e_ab2 + e_a2b - e_a2b2
    return {
        "S": S,
        "correlators": {
            "E(a,b)": e_ab,
            "E(a,b')": e_ab2,
            "E(a',b)": e_a2b,
            "E(a',b')": e_a2b2,
        },
        "classical_bound": 2.0,
        "tsirelson_bound": 2 * np.sqrt(2),
        "violates_classical": abs(S) > 2.0 + 1e-9,
    }
