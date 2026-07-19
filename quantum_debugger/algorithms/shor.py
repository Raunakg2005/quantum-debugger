"""
Shor's Algorithm -- Quantum Period Finding

The quantum core of Shor's factoring algorithm: find the period r of
f(x) = a^x mod N, i.e. the smallest r > 0 with a^r = 1 (mod N). Quantum Phase
Estimation is run on the modular-multiplication unitary U|y> = |a*y mod N>; the
measured phase s/r is turned into r by a continued-fraction expansion. Given r
(even, with a^(r/2) != -1 mod N), gcd(a^(r/2) +/- 1, N) yields a factor of N.
"""

from fractions import Fraction
from math import gcd

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary
from ..core.circuit import QuantumCircuit
from .qft import apply_inverse_qft


def _modmul_unitary(a: int, N: int, n: int) -> np.ndarray:
    """Permutation unitary U|y> = |a*y mod N> (identity on y >= N)."""
    dim = 2**n
    U = np.zeros((dim, dim), dtype=complex)
    for y in range(dim):
        U[(a * y) % N if y < N else y, y] = 1.0
    return U


def _controlled_power(U: np.ndarray, power: int) -> np.ndarray:
    Up = np.linalg.matrix_power(U, power)
    dim = U.shape[0]
    C = np.zeros((2 * dim, 2 * dim), dtype=complex)
    for s_in in range(dim):
        C[2 * s_in, 2 * s_in] = 1.0
        for s_out in range(dim):
            C[2 * s_out + 1, 2 * s_in + 1] = Up[s_out, s_in]
    return C


def period_finding(a: int, N: int, n_count: int = 8) -> dict:
    """
    Estimate the period r of a^x mod N with quantum phase estimation.

    Returns:
        dict with 'period' (best estimate, or None), 'phase', 'measured'.
    """
    n = int(np.ceil(np.log2(N)))
    U = _modmul_unitary(a, N, n)
    total = n + n_count

    # Work register initialized to |1>; counting register in superposition.
    state = QuantumState(total)
    sv = np.zeros(2**total, dtype=complex)
    sv[1] = 1.0  # work = 1, counting = 0
    state.state_vector = sv

    H = GateLibrary.H
    work = list(range(n))
    for j in range(n_count):
        state.apply_gate(H, [n + j])
    for j in range(n_count):
        control = n + j
        state.apply_gate(_controlled_power(U, 2**j), [control] + work)

    inv = QuantumCircuit(total)
    apply_inverse_qft(inv, qubits=list(reversed(range(n, n + n_count))))
    for g in inv.gates:
        state.apply_gate(g.matrix, g.qubits)

    probs = np.abs(state.state_vector) ** 2
    counting_probs = np.zeros(2**n_count)
    for index in range(len(probs)):
        counting_probs[index >> n] += probs[index]

    # Try the most probable non-zero measurements; recover r by continued fractions.
    order = np.argsort(counting_probs)[::-1]
    for measured in order[:8]:
        measured = int(measured)
        if measured == 0:
            continue
        phase = measured / (2**n_count)
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        if r > 0 and pow(a, r, N) == 1:
            return {"period": r, "phase": phase, "measured": measured}

    return {"period": None, "phase": None, "measured": None}


def shor_factor(N: int, a: int = None, n_count: int = 8, seed: int = 0) -> dict:
    """
    Attempt to factor ``N`` with Shor's algorithm (quantum period finding).

    Args:
        N: composite integer to factor
        a: base coprime to N (default: chosen automatically)
        n_count: counting qubits for phase estimation
        seed: RNG seed for base selection

    Returns:
        dict with 'factors' (a nontrivial pair or None), 'a', and 'period'.
    """
    if N % 2 == 0:
        return {"factors": (2, N // 2), "a": None, "period": None}

    rng = np.random.default_rng(seed)
    candidates = [a] if a is not None else list(range(2, N))
    if a is None:
        rng.shuffle(candidates)

    for base in candidates:
        if gcd(base, N) != 1:
            factor = gcd(base, N)
            return {"factors": (factor, N // factor), "a": base, "period": None}

        result = period_finding(base, N, n_count)
        r = result["period"]
        if r is None or r % 2 != 0:
            continue
        y = pow(base, r // 2, N)
        if y == N - 1:
            continue
        f1, f2 = gcd(y - 1, N), gcd(y + 1, N)
        for f in (f1, f2):
            if 1 < f < N:
                return {"factors": (f, N // f), "a": base, "period": r}

    return {"factors": None, "a": None, "period": None}
