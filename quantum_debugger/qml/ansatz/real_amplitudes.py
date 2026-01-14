"""
RealAmplitudes Ansatz

A hardware-efficient ansatz using only RY rotations and CNOT entanglement.
This ansatz produces only real amplitudes in the output state vector.
"""

import numpy as np
from typing import Callable, List
from ...core.circuit import QuantumCircuit


def real_amplitudes(
    num_qubits: int, reps: int = 1, entanglement: str = "linear"
) -> Callable:
    """
    Create a RealAmplitudes ansatz circuit.

    This ansatz uses RY rotation gates exclusively, which means the resulting
    state vector will have only real-valued amplitudes (no imaginary components).

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions of the structure
        entanglement: Entanglement pattern:
            - 'linear': Linear chain (0-1, 1-2, 2-3, ...)
            - 'full': All-to-all connections
            - 'circular': Circular chain (includes last-to-first)

    Returns:
        Function that builds the circuit with given parameters

    Example:
        >>> ansatz = real_amplitudes(num_qubits=3, reps=2)
        >>> circuit = ansatz(params)  # params is array of angles
    """

    def build_circuit(params: np.ndarray) -> QuantumCircuit:
        """Build the RealAmplitudes circuit"""
        circuit = QuantumCircuit(num_qubits)

        param_idx = 0

        for rep in range(
            reps + 1
        ):  # reps+1 to have rotation layer after last entanglement
            # Rotation layer - RY on all qubits
            for qubit in range(num_qubits):
                if param_idx < len(params):
                    circuit.ry(params[param_idx], qubit)
                    param_idx += 1

            # Entanglement layer (skip after last rotation layer)
            if rep < reps:
                if entanglement == "linear":
                    # Linear chain: 0-1, 1-2, 2-3, ...
                    for i in range(num_qubits - 1):
                        circuit.cnot(i, i + 1)

                elif entanglement == "full":
                    # All-to-all connections
                    for i in range(num_qubits):
                        for j in range(i + 1, num_qubits):
                            circuit.cnot(i, j)

                elif entanglement == "circular":
                    # Circular chain: includes last-to-first
                    for i in range(num_qubits):
                        circuit.cnot(i, (i + 1) % num_qubits)

                else:
                    raise ValueError(f"Unknown entanglement pattern: {entanglement}")

        return circuit

    # Calculate required number of parameters
    params_needed = (reps + 1) * num_qubits
    build_circuit.num_parameters = params_needed
    build_circuit.num_qubits = num_qubits
    build_circuit.reps = reps
    build_circuit.entanglement = entanglement

    return build_circuit


def count_parameters(num_qubits: int, reps: int) -> int:
    """
    Calculate number of parameters needed for RealAmplitudes ansatz.

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions

    Returns:
        Total number of parameters
    """
    return (reps + 1) * num_qubits


def get_entanglement_gates(num_qubits: int, pattern: str) -> List[tuple]:
    """
    Get list of entanglement gate positions for a given pattern.

    Args:
        num_qubits: Number of qubits
        pattern: Entanglement pattern ('linear', 'full', 'circular')

    Returns:
        List of (control, target) qubit pairs
    """
    gates = []

    if pattern == "linear":
        gates = [(i, i + 1) for i in range(num_qubits - 1)]
    elif pattern == "full":
        gates = [(i, j) for i in range(num_qubits) for j in range(i + 1, num_qubits)]
    elif pattern == "circular":
        gates = [(i, (i + 1) % num_qubits) for i in range(num_qubits)]
    else:
        raise ValueError(f"Unknown pattern: {pattern}")

    return gates
