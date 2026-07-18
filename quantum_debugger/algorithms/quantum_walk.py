"""
Discrete-Time Quantum Walk

A coined quantum walk on a cycle of N = 2**n_position_qubits sites. Each step
applies a Hadamard "coin" to an extra qubit and then a coin-controlled cyclic
shift (coin |1> -> step right, coin |0> -> step left). Unlike a classical random
walk (which spreads diffusively, std ~ sqrt(t)), the quantum walk spreads
*ballistically* (std ~ t).
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary


def _shift_operator(n_position_qubits: int) -> np.ndarray:
    """
    Coin-controlled cyclic shift on (position + coin) qubits.

    Position qubits are 0..n_position_qubits-1 (little-endian); the coin is the
    top qubit. Coin |1> increments the position mod N, coin |0> decrements it.
    """
    N = 2**n_position_qubits
    dim = 2 * N
    S = np.zeros((dim, dim), dtype=complex)
    for index in range(dim):
        pos = index & (N - 1)
        coin = (index >> n_position_qubits) & 1
        new_pos = (pos + 1) % N if coin == 1 else (pos - 1) % N
        new_index = (coin << n_position_qubits) | new_pos
        S[new_index, index] = 1.0
    return S


def quantum_walk(
    n_position_qubits: int,
    steps: int,
    start: int = None,
) -> dict:
    """
    Run a coined quantum walk and return the position distribution.

    Args:
        n_position_qubits: log2 of the number of cycle sites
        steps: Number of walk steps
        start: Starting site (default: the middle, N // 2)

    Returns:
        dict with 'distribution' (probability per site), 'mean', 'std'.
    """
    N = 2**n_position_qubits
    n = n_position_qubits + 1
    coin = n_position_qubits
    if start is None:
        start = N // 2

    state = QuantumState(n)  # |0...0>
    # Set the starting position (coin starts in |0>).
    sv = np.zeros(2**n, dtype=complex)
    sv[start] = 1.0
    state.state_vector = sv

    H = GateLibrary.H
    S = _shift_operator(n_position_qubits)
    all_qubits = list(range(n))

    for _ in range(steps):
        state.apply_gate(H, [coin])
        state.apply_gate(S, all_qubits)

    probs = np.abs(state.state_vector) ** 2
    # Marginalize the coin out to get the position distribution.
    distribution = np.zeros(N)
    for index in range(2**n):
        distribution[index & (N - 1)] += probs[index]

    sites = np.arange(N)
    mean = float(np.sum(sites * distribution))
    var = float(np.sum((sites - mean) ** 2 * distribution))
    return {
        "distribution": distribution,
        "mean": mean,
        "std": float(np.sqrt(var)),
        "steps": steps,
    }
