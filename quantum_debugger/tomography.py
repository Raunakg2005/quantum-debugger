"""
Quantum State Tomography

Reconstructs the density matrix of a 1- or 2-qubit state from *measurements*.
For each Pauli string P in {I, X, Y, Z}^n the expectation <P> is estimated by
rotating each qubit into the corresponding measurement basis, sampling
computational-basis outcomes, and averaging the parity. Linear inversion then
rebuilds rho = (1 / 2**n) * sum_P <P> P.
"""

import itertools

import numpy as np

from .core.quantum_state import QuantumState
from .core.gates import GateLibrary

_PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

# Single-qubit rotation that maps the P eigenbasis to the Z basis.
_S = np.array([[1, 0], [0, 1j]], dtype=complex)
_BASIS_ROTATION = {
    "X": GateLibrary.H,
    "Y": GateLibrary.H @ _S.conj().T,  # H S^dagger: measure Y
    "Z": np.eye(2, dtype=complex),
    "I": np.eye(2, dtype=complex),
}


def _pauli_string_matrix(pauli_string):
    matrix = np.array([[1.0 + 0j]])
    # Qubit 0 is the least-significant index bit; build the tensor product so
    # that ``pauli_string[q]`` acts on qubit q consistently with the simulator.
    for label in reversed(pauli_string):
        matrix = np.kron(matrix, _PAULI[label])
    return matrix


def _estimate_expectation(state_vector, pauli_string, shots, rng):
    """Estimate <P> for a Pauli string from ``shots`` simulated measurements."""
    n = len(pauli_string)
    if all(p == "I" for p in pauli_string):
        return 1.0

    state = QuantumState(n, state_vector=np.array(state_vector))
    for q, label in enumerate(pauli_string):
        rot = _BASIS_ROTATION[label]
        if not np.allclose(rot, np.eye(2)):
            state.apply_gate(rot, [q])

    probs = np.abs(state.state_vector) ** 2
    probs = probs / probs.sum()
    outcomes = rng.choice(len(probs), size=shots, p=probs)

    non_identity = [q for q, label in enumerate(pauli_string) if label != "I"]
    total = 0.0
    for outcome in outcomes:
        parity = sum((int(outcome) >> q) & 1 for q in non_identity) % 2
        total += 1.0 if parity == 0 else -1.0
    return total / shots


def state_tomography(state_vector, shots: int = 4000, seed: int = 0) -> dict:
    """
    Reconstruct the density matrix of a small state from measurements.

    Args:
        state_vector: The (pure) state to characterize
        shots: Measurement shots per Pauli setting
        seed: RNG seed

    Returns:
        dict with 'density_matrix', 'fidelity' (to the true state), and
        'purity' (Tr(rho^2)).
    """
    state_vector = np.asarray(state_vector, dtype=complex)
    n = int(round(np.log2(state_vector.shape[0])))
    if n > 3:
        raise ValueError("state_tomography is intended for <= 3 qubits")

    rng = np.random.default_rng(seed)
    dim = 2**n
    rho = np.zeros((dim, dim), dtype=complex)

    for pauli_string in itertools.product("IXYZ", repeat=n):
        coeff = _estimate_expectation(state_vector, pauli_string, shots, rng)
        rho += coeff * _pauli_string_matrix(pauli_string)
    rho /= dim

    true = np.outer(state_vector, state_vector.conj())
    fidelity = float(np.real(state_vector.conj() @ rho @ state_vector))
    purity = float(np.real(np.trace(rho @ rho)))
    return {
        "density_matrix": rho,
        "true_density_matrix": true,
        "fidelity": fidelity,
        "purity": purity,
    }
