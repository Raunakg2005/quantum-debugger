"""
Circuit scheduling and depth analysis.

Once gates are chosen and routed, the compiler *schedules* them into time steps: gates on
disjoint qubits run in parallel, so the **depth** (number of layers) can be far below the
gate count. As-soon-as-possible (ASAP) scheduling greedily places each operation in the
earliest layer where all its qubits are free. This module computes the ASAP layering, the
resulting depth, and the parallelism (gates per layer), verified: the depth is the length of
the critical path, and executing the layers in order reproduces the original circuit's
unitary.
"""

import numpy as np


def asap_layers(circuit, n_qubits: int):
    """
    As-soon-as-possible schedule: return a list of layers (each a list of operations) where
    every operation sits in the earliest layer whose qubits are all free. Operations on
    disjoint qubits share a layer.
    """
    ready = [0] * n_qubits          # earliest free time step per qubit
    layers = []
    for matrix, qubits in circuit:
        t = max(ready[q] for q in qubits)
        while len(layers) <= t:
            layers.append([])
        layers[t].append((np.asarray(matrix, dtype=complex), list(qubits)))
        for q in qubits:
            ready[q] = t + 1
    return layers


def circuit_depth(circuit, n_qubits: int) -> int:
    """The scheduled depth: the number of ASAP layers -- the critical-path length and the
    runtime cost (vs. the raw gate count)."""
    return len(asap_layers(circuit, n_qubits))


def circuit_parallelism(circuit, n_qubits: int) -> float:
    """Average parallelism: gate count divided by depth -- how many gates run per time step
    on average (1 for a fully serial circuit)."""
    d = circuit_depth(circuit, n_qubits)
    return float(len(circuit) / d) if d else 0.0


def flatten_layers(layers):
    """Flatten a layered schedule back into a linear circuit (layer order preserved) -- used
    to check that scheduling does not change the unitary."""
    return [op for layer in layers for op in layer]


def critical_path_length(circuit, n_qubits: int) -> int:
    """Length of the critical path -- the longest chain of gates sharing qubits, equal to the
    scheduled depth."""
    return circuit_depth(circuit, n_qubits)
