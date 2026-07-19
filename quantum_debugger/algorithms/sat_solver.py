"""
Grover-Based Constraint / SAT Solver

Use Grover's search to find an input that satisfies an arbitrary boolean predicate
``f(x) -> bool`` over n bits. The predicate defines the marked set; Grover amplifies
it to high probability in about ``(pi/4) sqrt(N/M)`` iterations, and the most likely
outcome is returned as a satisfying assignment (verified classically).

Bit ``q`` of the integer ``x`` maps to qubit ``q`` (``(x >> q) & 1``).
"""

from .grover import grover_search, optimal_iterations


def grover_solve(predicate, n_qubits: int) -> dict:
    """
    Find an ``x`` in ``0..2**n_qubits - 1`` with ``predicate(x)`` True, via Grover.

    Args:
        predicate: callable int -> bool marking the solutions
        n_qubits: number of bits

    Returns:
        dict with 'solution' (int, or None), 'bits' (0/1 per qubit), 'satisfies'
        (predicate check on the returned solution), 'num_solutions',
        'success_probability', and 'iterations'.
    """
    marked = [x for x in range(2**n_qubits) if predicate(x)]
    if not marked:
        return {
            "solution": None,
            "bits": None,
            "satisfies": False,
            "num_solutions": 0,
            "success_probability": 0.0,
            "iterations": 0,
        }

    n_iter = optimal_iterations(n_qubits, len(marked))
    result = grover_search(n_qubits, marked, n_iterations=n_iter)
    best = int(result["best_state"])

    return {
        "solution": best,
        "bits": [(best >> q) & 1 for q in range(n_qubits)],
        "satisfies": bool(predicate(best)),
        "num_solutions": len(marked),
        "success_probability": result["success_probability"],
        "iterations": n_iter,
    }
