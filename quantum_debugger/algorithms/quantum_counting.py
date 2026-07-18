"""
Quantum Counting

Estimates the number M of marked states in a search space of size N = 2**n
without knowing M in advance, by running Quantum Phase Estimation on the Grover
iterate G. G rotates by 2*theta with sin(theta) = sqrt(M/N); reading its phase
back gives M = N * sin^2(pi * phi).
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary
from .qft import apply_inverse_qft
from ..core.circuit import QuantumCircuit


def _grover_iterate(n_qubits: int, marked) -> np.ndarray:
    """Grover iterate G = D @ O_f as a 2**n x 2**n unitary."""
    N = 2**n_qubits

    # Oracle: phase-flip marked states.
    O = np.eye(N, dtype=complex)
    for m in marked:
        O[m, m] = -1.0

    # Diffusion D = 2|s><s| - I, |s> = uniform superposition.
    s = np.ones(N, dtype=complex) / np.sqrt(N)
    D = 2.0 * np.outer(s, s.conj()) - np.eye(N)

    return D @ O


def _controlled_power(G: np.ndarray, power: int) -> np.ndarray:
    """Controlled-G^power on (control gate-qubit 0 + search qubits 1..n)."""
    Gp = np.linalg.matrix_power(G, power)
    dim = G.shape[0]
    C = np.zeros((2 * dim, 2 * dim), dtype=complex)
    for s_in in range(dim):
        C[2 * s_in, 2 * s_in] = 1.0  # control = 0 -> identity
        for s_out in range(dim):
            C[2 * s_out + 1, 2 * s_in + 1] = Gp[s_out, s_in]  # control = 1 -> G^power
    return C


def quantum_counting(n_qubits: int, marked, n_counting: int = 4) -> dict:
    """
    Estimate the number of marked states.

    Args:
        n_qubits: Number of search qubits (N = 2**n_qubits)
        marked: Iterable of marked basis-state indices
        n_counting: Number of counting qubits (precision)

    Returns:
        dict with 'estimated_count', 'true_count', 'phase', 'theta'.
    """
    marked = [int(m) for m in marked]
    N = 2**n_qubits
    G = _grover_iterate(n_qubits, marked)

    total = n_qubits + n_counting
    state = QuantumState(total)  # |0...0>

    # A|0> on the search register (uniform superposition) and H on counting.
    H = GateLibrary.H
    for q in range(n_qubits):
        state.apply_gate(H, [q])
    for j in range(n_counting):
        state.apply_gate(H, [n_qubits + j])

    # Controlled-G^(2^j) with counting qubit (n_qubits + j) as control.
    search = list(range(n_qubits))
    for j in range(n_counting):
        control = n_qubits + j
        CG = _controlled_power(G, 2**j)
        state.apply_gate(CG, [control] + search)

    # Inverse QFT on the counting register.
    inv = QuantumCircuit(total)
    apply_inverse_qft(
        inv, qubits=list(reversed(range(n_qubits, n_qubits + n_counting)))
    )
    for g in inv.gates:
        state.apply_gate(g.matrix, g.qubits)

    # Read out the counting register (marginalize the search register).
    probs = np.abs(state.state_vector) ** 2
    counting_probs = np.zeros(2**n_counting)
    for index in range(len(probs)):
        counting_probs[index >> n_qubits] += probs[index]

    best = int(np.argmax(counting_probs))
    phi = best / (2**n_counting)
    theta = np.pi * phi
    estimated = N * (np.sin(theta) ** 2)

    return {
        "estimated_count": estimated,
        "true_count": len(marked),
        "phase": phi,
        "theta": theta,
        "counting_probabilities": counting_probs,
    }
