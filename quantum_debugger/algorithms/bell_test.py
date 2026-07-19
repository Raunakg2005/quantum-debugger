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

from itertools import product

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_Z = GateLibrary.Z
_X = GateLibrary.X
_Y = GateLibrary.Y


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


def chsh_game(
    a: float = 0.0,
    a_prime: float = np.pi / 2,
    b: float = np.pi / 4,
    b_prime: float = -np.pi / 4,
) -> dict:
    """
    The CHSH nonlocal game with the optimal quantum strategy.

    A referee sends questions (x, y); the players (sharing a Bell pair) answer
    (a, b) and win iff ``a XOR b == x AND y``. The best classical strategy wins
    with probability 3/4; the quantum strategy wins with ``cos^2(pi/8) ~ 0.854``.

    Player x measures at angle ``a`` (x=0) or ``a'`` (x=1); player y at ``b`` or
    ``b'``. The win probability is computed from the Bell-pair correlators.

    Returns dict with 'quantum_win_probability', 'classical_win_probability' (0.75),
    'tsirelson_win_probability' (cos^2(pi/8)), and 'beats_classical'.
    """
    psi = bell_state()
    angles_a = {0: a, 1: a_prime}
    angles_b = {0: b, 1: b_prime}

    total = 0.0
    for x in (0, 1):
        for y in (0, 1):
            e = correlator(psi, angles_a[x], angles_b[y])
            # Win needs a == b when x AND y == 0, else a != b.
            if (x & y) == 0:
                p_win = (1 + e) / 2
            else:
                p_win = (1 - e) / 2
            total += p_win
    quantum_win = total / 4

    return {
        "quantum_win_probability": quantum_win,
        "classical_win_probability": 0.75,
        "tsirelson_win_probability": float(np.cos(np.pi / 8) ** 2),
        "beats_classical": quantum_win > 0.75 + 1e-9,
    }


def _pauli_string_op(s: str) -> np.ndarray:
    """Dense operator for a Pauli string over X/Y/Z/I (qubit 0 = first char)."""
    table = {"X": _X, "Y": _Y, "Z": _Z, "I": np.eye(2, dtype=complex)}
    mat = np.array([[1.0]], dtype=complex)
    for c in reversed(s):
        mat = np.kron(mat, table[c])
    return mat


def mermin_ghz_test() -> dict:
    """
    The 3-qubit GHZ (Mermin) test of multipartite nonlocality.

    For the GHZ state ``(|000> + |111>)/sqrt(2)`` the Mermin operator
    ``M = XXX - XYY - YXY - YYX`` has expectation 4, while any local
    hidden-variable model is bounded by 2 -- an all-or-nothing (deterministic)
    violation, stronger than CHSH.

    Returns dict with 'quantum_value' (4), 'classical_bound' (2),
    'violation_ratio', and 'violates_classical'.
    """
    ghz = np.zeros(8, dtype=complex)
    ghz[0] = ghz[7] = 1 / np.sqrt(2)
    strings = [("XXX", 1), ("XYY", -1), ("YXY", -1), ("YYX", -1)]
    M = sum(c * _pauli_string_op(s) for s, c in strings)
    quantum = float(np.real(np.vdot(ghz, M @ ghz)))

    # Classical LHV bound: brute force over x_j, y_j in {-1, +1}.
    best = 0.0
    for x0, x1, x2, y0, y1, y2 in product([-1, 1], repeat=6):
        val = x0 * x1 * x2 - x0 * y1 * y2 - y0 * x1 * y2 - y0 * y1 * x2
        best = max(best, abs(val))

    return {
        "quantum_value": quantum,
        "classical_bound": float(best),
        "violation_ratio": quantum / best,
        "violates_classical": quantum > best + 1e-9,
    }
