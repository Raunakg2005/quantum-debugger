"""
Simon's Algorithm

Given a 2-to-1 function ``f`` with a hidden XOR mask ``s`` (``f(x) = f(y)`` iff
``y = x XOR s``), Simon's algorithm recovers ``s`` with only O(n) quantum queries,
an exponential speedup over the classical O(2^(n/2)). Each run of the circuit
(H^n, oracle, H^n, measure) yields a bit-string ``y`` satisfying ``y . s = 0``
(mod 2); collecting n-1 independent such constraints pins down ``s`` by a GF(2)
null-space solve.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_H = GateLibrary.H


def _default_f(s: int, n: int):
    """A valid 2-to-1 function for mask s: f(x) = min(x, x XOR s) (or 1-to-1 if s=0)."""
    return lambda x: min(x, x ^ s)


def simon_oracle(f, n: int) -> np.ndarray:
    """
    Build the 2n-qubit oracle |x>|b> -> |x>|b XOR f(x)>.

    Input register = qubits 0..n-1, output register = qubits n..2n-1.
    """
    dim = 2 ** (2 * n)
    U = np.zeros((dim, dim), dtype=complex)
    mask = (1 << n) - 1
    for x in range(2**n):
        fx = f(x) & mask
        for b in range(2**n):
            src = x | (b << n)
            dst = x | ((b ^ fx) << n)
            U[dst, src] = 1.0
    return U


def _measure_input_distribution(f, n: int) -> np.ndarray:
    """Probability distribution over the n-bit input register after the circuit."""
    total = 2 * n
    state = QuantumState(total)
    for q in range(n):
        state.apply_gate(_H, [q])
    state.apply_gate(simon_oracle(f, n), list(range(total)))
    for q in range(n):
        state.apply_gate(_H, [q])

    probs = np.abs(state.state_vector) ** 2
    marginal = np.zeros(2**n)
    for index in range(len(probs)):
        marginal[index & ((1 << n) - 1)] += probs[index]
    return marginal


def _gf2_rank(rows):
    """Rank of the given bit-string rows over GF(2)."""
    pivots = []
    for r in rows:
        cur = r
        for p in pivots:
            cur = min(cur, cur ^ p)
        if cur:
            pivots.append(cur)
    return len(pivots)


def _gf2_nullspace_vector(rows, n: int):
    """Return a nonzero vector s (as int) with rows . s = 0 over GF(2), or None."""
    # Reduce the rows to RREF over GF(2); each pivot row keeps only its pivot
    # column plus free columns, so back-substitution is a single lookup.
    pivots = []  # list of (pivot_col, row)
    for r in rows:
        cur = r
        for pc, prow in pivots:
            if (cur >> pc) & 1:
                cur ^= prow
        if cur == 0:
            continue
        pc = cur.bit_length() - 1
        pivots = [
            (opc, oprow ^ cur if (oprow >> pc) & 1 else oprow) for opc, oprow in pivots
        ]
        pivots.append((pc, cur))

    pivot_cols = {pc for pc, _ in pivots}
    free = [c for c in range(n) if c not in pivot_cols]
    if not free:
        return None  # only the trivial solution s = 0
    f = free[0]
    s = 1 << f
    # In RREF, pivot variable pc = XOR of free vars in its row; only s_f = 1 here.
    for pc, prow in pivots:
        if (prow >> f) & 1:
            s |= 1 << pc
    return s


def simon(
    s: int = None, n: int = 3, f=None, max_runs: int = 100, seed: int = 0
) -> dict:
    """
    Run Simon's algorithm and recover the hidden mask.

    Provide either a planted secret ``s`` (a default 2-to-1 ``f`` is built) or a
    custom function ``f``. Returns dict with 'secret' (recovered s), 'equations'
    (the collected y constraints), and 'runs'.
    """
    if f is None:
        assert s is not None, "provide either s or f"
        f = _default_f(s, n)

    rng = np.random.default_rng(seed)
    marginal = _measure_input_distribution(f, n)
    candidates = [y for y in range(2**n) if marginal[y] > 1e-9]
    probs = np.array([marginal[c] for c in candidates], dtype=float)
    probs /= probs.sum()

    # Sample y's (each satisfies y.s = 0), keeping only ones that raise the rank.
    # Stop when rank = n-1: the null space is then exactly {0, s}.
    equations = []
    runs = 0
    while runs < max_runs and _gf2_rank(equations) < n - 1:
        runs += 1
        y = int(rng.choice(candidates, p=probs))
        if y == 0:
            continue
        if _gf2_rank(equations + [y]) > _gf2_rank(equations):
            equations.append(y)

    recovered = _gf2_nullspace_vector(equations, n) if equations else None
    return {"secret": recovered, "equations": equations, "runs": runs}
