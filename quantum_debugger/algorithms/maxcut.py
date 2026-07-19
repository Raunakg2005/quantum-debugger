"""
QAOA MaxCut Solver

An application-level wrapper over the QAOA ansatz that returns an actual *solution*
to a MaxCut instance -- the node partition, its cut value, the brute-force optimum,
and the approximation ratio -- rather than just an expected cost. Multiple random
restarts make the result robust.

MaxCut: partition the graph's nodes into two sets to maximize the number of edges
crossing between them.
"""

import numpy as np

from ..qml.algorithms.qaoa import QAOA


def _cut_value(graph, bitstring: int) -> int:
    """Number of edges whose endpoints are on opposite sides of the partition."""
    return sum(1 for i, j in graph if ((bitstring >> i) & 1) != ((bitstring >> j) & 1))


def brute_force_maxcut(graph, n_nodes: int) -> dict:
    """Exact MaxCut by enumerating all 2**n partitions (small graphs only)."""
    best_value, best_partition = -1, 0
    for assignment in range(2**n_nodes):
        v = _cut_value(graph, assignment)
        if v > best_value:
            best_value, best_partition = v, assignment
    return {
        "cut_value": best_value,
        "partition": [(best_partition >> q) & 1 for q in range(n_nodes)],
    }


def solve_maxcut(
    graph,
    p: int = 2,
    restarts: int = 5,
    max_iterations: int = 150,
    seed: int = 0,
) -> dict:
    """
    Solve a MaxCut instance with QAOA and return the best partition found.

    Args:
        graph: list of edges [(i, j), ...]
        p: number of QAOA layers
        restarts: random restarts (best kept)
        max_iterations: classical optimizer iterations per restart
        seed: RNG seed

    Returns:
        dict with 'partition' (0/1 per node), 'cut_value', 'optimal_cut'
        (brute force), 'approximation_ratio', and 'probability' of the returned
        bitstring in the final state.
    """
    rng = np.random.default_rng(seed)
    qaoa = QAOA(graph=graph, p=p, max_iterations=max_iterations)
    n = qaoa.num_qubits

    best = None
    for _ in range(restarts):
        np.random.seed(int(rng.integers(1_000_000)))
        init = np.random.rand(2 * p) * np.pi
        result = qaoa.run(initial_params=init)
        if best is None or result["best_value"] > best["best_value"]:
            best = result

    gamma = best["optimal_params"][:p]
    beta = best["optimal_params"][p:]
    statevector = qaoa._simulate_qaoa(gamma, beta)
    probs = np.abs(statevector) ** 2
    bitstring = int(np.argmax(probs))

    cut = _cut_value(graph, bitstring)
    exact = brute_force_maxcut(graph, n)
    optimal_cut = exact["cut_value"]

    return {
        "partition": [(bitstring >> q) & 1 for q in range(n)],
        "cut_value": cut,
        "optimal_cut": optimal_cut,
        "approximation_ratio": cut / optimal_cut if optimal_cut else 1.0,
        "probability": float(probs[bitstring]),
        "expected_cut": best["best_value"],
    }
