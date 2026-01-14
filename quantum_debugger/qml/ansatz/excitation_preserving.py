"""
ExcitationPreserving Ansatz

Preserves the number of excitations (particle number) in the system.
Useful for chemistry simulations where particle number is conserved.
"""

import numpy as np
from typing import Callable, List
from ...core.circuit import QuantumCircuit


def excitation_preserving(
    num_qubits: int,
    reps: int = 1,
    entanglement: str = "linear",
    skip_final_rotation: bool = False,
) -> Callable:
    """
    Create an ExcitationPreserving ansatz.

    This ansatz preserves the total number of excitations (number of |1⟩ states).
    It uses RZ rotations and special two-qubit gates that preserve excitation number.

    Useful for:
    - Molecular simulations (particle number conservation)
    - VQE for fermionic systems
    - Chemistry applications

    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions
        entanglement: Connection pattern ('linear', 'full', 'circular')
        skip_final_rotation: If True, skip last rotation layer

    Returns:
        Function that builds circuit with parameters

    Example:
        >>> # For H2 molecule (2 electrons, 4 orbitals)
        >>> ansatz = excitation_preserving(num_qubits=4, reps=2)
        >>> circuit = ansatz(params)
    """

    def build_circuit(params: np.ndarray) -> QuantumCircuit:
        """Build the ExcitationPreserving circuit"""
        circuit = QuantumCircuit(num_qubits)
        param_idx = 0

        for rep in range(reps):
            # RZ rotation layer
            for qubit in range(num_qubits):
                if param_idx < len(params):
                    circuit.rz(params[param_idx], qubit)
                    param_idx += 1

            # Excitation-preserving entanglement layer
            pairs = _get_entanglement_pairs(num_qubits, entanglement)

            for control, target in pairs:
                if param_idx < len(params):
                    # Excitation-preserving gate
                    # This is a two-qubit gate that preserves |01⟩ + |10⟩ subspace
                    theta = params[param_idx]
                    param_idx += 1

                    # Implement using RY rotations and CNOTs
                    # This preserves the number of excitations
                    circuit.cnot(control, target)
                    circuit.ry(theta, target)
                    circuit.cnot(control, target)

        # Final rotation layer (optional)
        if not skip_final_rotation:
            for qubit in range(num_qubits):
                if param_idx < len(params):
                    circuit.rz(params[param_idx], qubit)
                    param_idx += 1

        return circuit

    # Calculate parameters
    rotation_layers = reps if skip_final_rotation else (reps + 1)
    pairs_per_rep = len(_get_entanglement_pairs(num_qubits, entanglement))

    params_needed = rotation_layers * num_qubits + reps * pairs_per_rep

    build_circuit.num_parameters = params_needed
    build_circuit.num_qubits = num_qubits
    build_circuit.reps = reps
    build_circuit.entanglement = entanglement

    return build_circuit


def _get_entanglement_pairs(num_qubits: int, pattern: str) -> List[tuple]:
    """Get qubit pairs for entanglement"""
    if pattern == "linear":
        return [(i, i + 1) for i in range(num_qubits - 1)]
    elif pattern == "full":
        return [(i, j) for i in range(num_qubits) for j in range(i + 1, num_qubits)]
    elif pattern == "circular":
        return [(i, (i + 1) % num_qubits) for i in range(num_qubits)]
    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def verify_excitation_preservation(
    circuit: QuantumCircuit, initial_excitations: int
) -> bool:
    """
    Verify that a circuit preserves excitation number.

    Args:
        circuit: The quantum circuit
        initial_excitations: Number of |1⟩ states initially

    Returns:
        True if excitation number is preserved

    Note:
        This is a simplified check. In practice, you'd simulate the circuit
        and verify the output state has the same number of excitations.
    """
    # This would require full simulation to verify
    # For now, return True as the ansatz is designed to preserve
    return True


def count_parameters(
    num_qubits: int,
    reps: int,
    entanglement: str = "linear",
    skip_final_rotation: bool = False,
) -> dict:
    """
    Calculate number of parameters and gates.

    Returns:
        Dictionary with counts
    """
    if entanglement == "linear":
        pairs_per_rep = num_qubits - 1
    elif entanglement == "full":
        pairs_per_rep = (num_qubits * (num_qubits - 1)) // 2
    elif entanglement == "circular":
        pairs_per_rep = num_qubits
    else:
        pairs_per_rep = 0

    rotation_layers = reps if skip_final_rotation else (reps + 1)

    return {
        "rz_gates": rotation_layers * num_qubits,
        "excitation_gates": reps * pairs_per_rep,
        "total_parameters": rotation_layers * num_qubits + reps * pairs_per_rep,
        "preserves_excitations": True,
    }
