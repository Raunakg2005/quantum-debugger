"""
StronglyEntangling Ansatz

Creates strongly entangled states using arbitrary rotations and entanglement.
Inspired by Pennylane's StronglyEntanglingLayers.
"""

import numpy as np
from typing import Callable
from ...core.circuit import QuantumCircuit


def strongly_entangling(num_qubits: int, reps: int = 1) -> Callable:
    """
    Create a StronglyEntangling ansatz.

    This ansatz creates highly entangled states through:
    1. Arbitrary single-qubit rotations (RX, RY, RZ on each qubit)
    2. Circular CNOT entanglement (each qubit entangled with next)

    Produces very expressive circuits capable of representing
    a large variety of quantum states.

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions (layers)

    Returns:
        Function that builds circuit with parameters

    Example:
        >>> ansatz = strongly_entangling(num_qubits=4, reps=3)
        >>> # Requires 4*3*3 = 36 parameters for 3 reps
        >>> params = np.random.uniform(0, 2*np.pi, 36)
        >>> circuit = ansatz(params)
    """

    def build_circuit(params: np.ndarray) -> QuantumCircuit:
        """Build the StronglyEntangling circuit"""
        circuit = QuantumCircuit(num_qubits)
        param_idx = 0

        for rep in range(reps):
            # Layer of arbitrary rotations (RX, RY, RZ on each qubit)
            for qubit in range(num_qubits):
                # RZ rotation
                if param_idx < len(params):
                    circuit.rz(params[param_idx], qubit)
                    param_idx += 1

                # RY rotation
                if param_idx < len(params):
                    circuit.ry(params[param_idx], qubit)
                    param_idx += 1

                # RZ rotation (second)
                if param_idx < len(params):
                    circuit.rz(params[param_idx], qubit)
                    param_idx += 1

            # Entanglement layer - Circular CNOTs
            for qubit in range(num_qubits):
                next_qubit = (qubit + 1) % num_qubits
                circuit.cnot(qubit, next_qubit)

        return circuit

    # Calculate required parameters
    # Each layer uses 3 rotations per qubit
    params_needed = reps * num_qubits * 3

    build_circuit.num_parameters = params_needed
    build_circuit.num_qubits = num_qubits
    build_circuit.reps = reps

    return build_circuit


def count_parameters(num_qubits: int, reps: int) -> int:
    """
    Calculate total number of parameters.

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions

    Returns:
        Total parameters needed
    """
    return reps * num_qubits * 3


def count_gates(num_qubits: int, reps: int) -> dict:
    """
    Count gates in StronglyEntangling ansatz.

    Returns:
        Dictionary with gate counts
    """
    return {
        "rz_gates": reps * num_qubits * 2,  # 2 RZ per qubit per layer
        "ry_gates": reps * num_qubits,  # 1 RY per qubit per layer
        "cnot_gates": reps * num_qubits,  # Circular CNOTs
        "total_gates": reps * num_qubits * 4,
        "parameters": reps * num_qubits * 3,
        "expressiveness": "high",
    }


def estimate_state_space_coverage(num_qubits: int, reps: int) -> float:
    """
    Estimate fraction of Hilbert space accessible.

    This is a rough estimate. The actual coverage depends on
    the specific parameter values.

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions

    Returns:
        Estimated coverage fraction (0 to 1)
    """
    # Hilbert space dimension
    dim = 2**num_qubits

    # Number of parameters (degrees of freedom)
    params = count_parameters(num_qubits, reps)

    # Rough estimate: coverage ≈ min(1, params / dim)
    # This is a heuristic, not exact
    coverage = min(1.0, params / dim)

    return coverage


def initialize_parameters(
    num_qubits: int, reps: int, strategy: str = "random"
) -> np.ndarray:
    """
    Initialize parameters for the ansatz.

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions
        strategy: Initialization strategy:
            - 'random': Uniform random in [0, 2π]
            - 'zeros': All zeros
            - 'small': Small random values near zero

    Returns:
        Array of initial parameters
    """
    n_params = count_parameters(num_qubits, reps)

    if strategy == "random":
        return np.random.uniform(0, 2 * np.pi, n_params)
    elif strategy == "zeros":
        return np.zeros(n_params)
    elif strategy == "small":
        return np.random.normal(0, 0.1, n_params)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
