"""
Grover Adaptive Search -- Minimum Finding (Durr-Hoyer)

Find the input minimizing a cost function ``f(x)`` over n bits using Grover search
as a subroutine. Each round marks the states beating the current best value and
uses Grover to sample one of them, lowering the threshold until no better state
remains. This finds the global minimum with O(sqrt(N)) expected oracle queries,
a quadratic speedup over classical brute-force scanning.
"""

import numpy as np

from .grover import grover_search


def grover_minimize(f, n_qubits: int, rounds: int = None, seed: int = 0) -> dict:
    """
    Minimize ``f(x)`` over ``x`` in ``0..2**n_qubits - 1`` with Grover adaptive search.

    Args:
        f: callable int -> comparable cost
        n_qubits: number of bits
        rounds: adaptive rounds (default ~ 2*sqrt(N) + a small constant)
        seed: RNG seed

    Returns:
        dict with 'argmin', 'min_value', 'exact_argmin', 'exact_min', 'found_optimum',
        and 'rounds_used'.
    """
    N = 2**n_qubits
    rng = np.random.default_rng(seed)
    if rounds is None:
        # Durr-Hoyer needs ~O(sqrt(N)) rounds; use a generous constant so the
        # threshold reliably ratchets down to the true minimum.
        rounds = int(8 * np.sqrt(N)) + 10

    # Start from a random threshold.
    best_x = int(rng.integers(N))
    best_val = f(best_x)

    max_iter = max(1, int(np.ceil(np.sqrt(N))))
    used = 0
    for _ in range(rounds):
        marked = [x for x in range(N) if f(x) < best_val]
        if not marked:
            break  # nothing beats the current best -> it is the minimum
        used += 1
        # BBHT randomization: a RANDOM number of Grover iterations avoids the
        # over-rotation trap when many states are marked (a fixed optimal count
        # would amplify the unmarked states and stall). j = 0 means no amplifica-
        # tion -> a uniform sample, which still beats the threshold with prob M/N.
        j = int(rng.integers(0, max_iter + 1))
        if j == 0:
            candidate = int(rng.integers(N))
        else:
            result = grover_search(n_qubits, marked, n_iterations=j)
            probs = np.asarray(result["probabilities"], dtype=float)
            probs = probs / probs.sum()
            candidate = int(rng.choice(N, p=probs))
        if f(candidate) < best_val:
            best_x, best_val = candidate, f(candidate)

    exact_argmin = min(range(N), key=f)
    exact_min = f(exact_argmin)
    return {
        "argmin": best_x,
        "min_value": best_val,
        "exact_argmin": exact_argmin,
        "exact_min": exact_min,
        "found_optimum": best_val == exact_min,
        "rounds_used": used,
    }
