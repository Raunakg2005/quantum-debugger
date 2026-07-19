"""
Entangled State Preparation

Genuine gate-based circuits that prepare the canonical multi-qubit entangled
states, each exactly verifiable:

  * ``ghz_state(n)``          -- (|0...0> + |1...1>) / sqrt(2)
  * ``w_state(n)``            -- equal superposition of all single-excitation
                                 states, via a cascade of Givens rotations
  * ``graph_state(edges, n)`` -- cluster / graph state (H on all, CZ per edge),
                                 the resource state for measurement-based QC
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_H = GateLibrary.H
_X = GateLibrary.X
_CNOT = GateLibrary.CNOT
_CZ = GateLibrary.CZ


def _givens(phi):
    """Two-qubit Givens rotation moving a single excitation with a positive sign."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array(
        [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=complex
    )


def ghz_state(n: int) -> np.ndarray:
    """Prepare the n-qubit GHZ state and return its state vector."""
    state = QuantumState(n)
    state.apply_gate(_H, [0])
    for q in range(n - 1):
        state.apply_gate(_CNOT, [q, q + 1])
    return state.state_vector


def w_state(n: int) -> np.ndarray:
    """
    Prepare the n-qubit W state (equal superposition of |100..0>, |010..0>, ...)
    via a cascade of Givens rotations that split the single excitation evenly.
    """
    state = QuantumState(n)
    state.apply_gate(_X, [0])
    for j in range(n - 1):
        phi = np.arccos(1 / np.sqrt(n - j))
        state.apply_gate(_givens(phi), [j, j + 1])
    return state.state_vector


def graph_state(edges, n: int) -> np.ndarray:
    """
    Prepare a graph (cluster) state: |+> on every qubit, then CZ on each edge.

    Args:
        edges: list of (i, j) qubit pairs
        n: number of qubits

    Returns:
        the graph state's state vector.
    """
    state = QuantumState(n)
    for q in range(n):
        state.apply_gate(_H, [q])
    for i, j in edges:
        state.apply_gate(_CZ, [i, j])
    return state.state_vector
