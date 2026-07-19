"""
Multi-Controlled-X Synthesis

Decompose Toffoli (CCX) and general n-controlled-X gates into the elementary
1- and 2-qubit gate set (H, T, T-dagger, CNOT). The Toffoli decomposition is the
standard Nielsen-Chuang construction; the n-control MCX is built from a ladder of
Toffolis using ``n_controls - 1`` clean ancilla qubits (returned to |0>).

Each routine returns a list of ``(gate_matrix, qubits)`` operations that can be
applied on the state-vector simulator.
"""

import numpy as np

from ..core.gates import GateLibrary

_H = GateLibrary.H
_CNOT = GateLibrary.CNOT
_T = GateLibrary.PHASE(np.pi / 4)
_TDG = GateLibrary.PHASE(-np.pi / 4)


def toffoli_gates(a: int, b: int, c: int) -> list:
    """
    Decompose the Toffoli gate CCX(controls a, b; target c) into H/T/CNOT.

    Returns a list of (gate_matrix, [qubits]) operations.
    """
    return [
        (_H, [c]),
        (_CNOT, [b, c]),
        (_TDG, [c]),
        (_CNOT, [a, c]),
        (_T, [c]),
        (_CNOT, [b, c]),
        (_TDG, [c]),
        (_CNOT, [a, c]),
        (_T, [b]),
        (_T, [c]),
        (_CNOT, [a, b]),
        (_H, [c]),
        (_T, [a]),
        (_TDG, [b]),
        (_CNOT, [a, b]),
    ]


def mcx_gates(controls: list, target: int, ancillas: list) -> list:
    """
    Decompose an n-controlled-X into Toffolis via a clean-ancilla ladder.

    Needs ``len(controls) - 1`` ancillas (assumed |0>, returned to |0>).

    Returns a list of (gate_matrix, [qubits]) operations.
    """
    controls = list(controls)
    n = len(controls)
    if n == 0:
        return [(GateLibrary.X, [target])]
    if n == 1:
        return [(_CNOT, [controls[0], target])]
    if n == 2:
        return toffoli_gates(controls[0], controls[1], target)

    assert len(ancillas) >= n - 1, "need n_controls - 1 ancillas"

    gates = []
    # Compute AND of the first two controls into ancilla 0.
    forward = [toffoli_gates(controls[0], controls[1], ancillas[0])]
    for i in range(2, n):
        forward.append(toffoli_gates(controls[i], ancillas[i - 2], ancillas[i - 1]))
    for block in forward:
        gates.extend(block)

    # ancilla[n-2] now holds the AND of all controls.
    gates.append((_CNOT, [ancillas[n - 2], target]))

    # Uncompute the ladder in reverse block order. A Toffoli is self-inverse, so
    # re-applying the same block (not its reversed gate list) cancels it.
    for block in reversed(forward):
        gates.extend(block)

    return gates


def apply_gates(state, gates):
    """Apply a list of (gate_matrix, qubits) to a QuantumState."""
    for gate, qubits in gates:
        state.apply_gate(gate, qubits)
    return state
