"""
Grover's Search Algorithm

Amplitude amplification that finds marked computational-basis states in an
unstructured search of size N = 2**n_qubits in about (pi/4) * sqrt(N/M) queries.
The oracle (phase-flip the marked states) and the diffusion operator (inversion
about the mean) are both built from real gates -- H, X, and a multi-controlled-Z.
"""

from typing import List, Optional, Union

import numpy as np

from ..core.circuit import QuantumCircuit


def _add_mcz(circuit: QuantumCircuit, qubits: List[int]) -> None:
    """Multi-controlled-Z: phase-flip the all-ones state of ``qubits``."""
    k = len(qubits)
    dim = 2**k
    matrix = np.eye(dim, dtype=complex)
    matrix[dim - 1, dim - 1] = -1.0
    circuit._add_gate("MCZ", matrix, list(qubits))


def _oracle(circuit: QuantumCircuit, n: int, marked: List[int]) -> None:
    """Phase-flip each marked basis state (little-endian bit order)."""
    for target in marked:
        flips = [q for q in range(n) if not ((target >> q) & 1)]
        for q in flips:
            circuit.x(q)
        _add_mcz(circuit, list(range(n)))
        for q in flips:
            circuit.x(q)


def _diffusion(circuit: QuantumCircuit, n: int) -> None:
    """Inversion about the mean: H^n X^n (MCZ) X^n H^n."""
    for q in range(n):
        circuit.h(q)
    for q in range(n):
        circuit.x(q)
    _add_mcz(circuit, list(range(n)))
    for q in range(n):
        circuit.x(q)
    for q in range(n):
        circuit.h(q)


def optimal_iterations(n_qubits: int, n_marked: int = 1) -> int:
    """Optimal number of Grover iterations, round((pi/4) sqrt(N/M) - 1/2)."""
    N = 2**n_qubits
    return max(1, int(round((np.pi / 4.0) * np.sqrt(N / n_marked) - 0.5)))


def grover(
    n_qubits: int,
    marked_states: Union[int, List[int]],
    n_iterations: Optional[int] = None,
) -> QuantumCircuit:
    """
    Build the Grover-search circuit for the given marked states.

    Args:
        n_qubits: Number of search qubits (search space N = 2**n_qubits)
        marked_states: A basis-state index or list of indices to find
        n_iterations: Grover iterations (default: the optimal count)

    Returns:
        The circuit; run it and measure to obtain a marked state with high prob.
    """
    if isinstance(marked_states, (int, np.integer)):
        marked_states = [int(marked_states)]
    marked_states = [int(m) for m in marked_states]

    if n_iterations is None:
        n_iterations = optimal_iterations(n_qubits, len(marked_states))

    circuit = QuantumCircuit(n_qubits)
    for q in range(n_qubits):
        circuit.h(q)
    for _ in range(n_iterations):
        _oracle(circuit, n_qubits, marked_states)
        _diffusion(circuit, n_qubits)
    return circuit


def grover_search(
    n_qubits: int,
    marked_states: Union[int, List[int]],
    n_iterations: Optional[int] = None,
) -> dict:
    """
    Run Grover search and return the outcome distribution.

    Returns:
        dict with 'probabilities' (over all states), 'best_state', and
        'success_probability' (total probability on the marked states).
    """
    if isinstance(marked_states, (int, np.integer)):
        marked_states = [int(marked_states)]
    marked_states = [int(m) for m in marked_states]

    circuit = grover(n_qubits, marked_states, n_iterations)
    probs = circuit.get_statevector().get_probabilities()
    return {
        "probabilities": probs,
        "best_state": int(np.argmax(probs)),
        "success_probability": float(sum(probs[m] for m in marked_states)),
        "iterations": (
            n_iterations
            if n_iterations is not None
            else optimal_iterations(n_qubits, len(marked_states))
        ),
    }
