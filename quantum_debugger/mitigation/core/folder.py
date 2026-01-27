"""
Circuit Folding for Noise Amplification

Implements techniques to scale noise levels by inserting gate^(-1) gate sequences.
This allows zero-noise extrapolation by running circuits at multiple noise levels.
"""

import numpy as np
from typing import List, Optional, Dict


class CircuitFolder:
    """
    Circuit folding utilities for noise scaling.

    Folding increases circuit depth while preserving logical operation,
    which amplifies noise proportionally to the circuit length.
    """

    # Gate inverse mapping (self-inverse and simple inverses)
    INVERSE_MAP = {
        "h": "h",  # Hadamard is self-inverse
        "x": "x",  # Pauli-X is self-inverse
        "y": "y",  # Pauli-Y is self-inverse
        "z": "z",  # Pauli-Z is self-inverse
        "s": "sdg",  # S† is inverse of S
        "sdg": "s",  # S is inverse of S†
        "t": "tdg",  # T† is inverse of T
        "tdg": "t",  # T is inverse of T†
        "cnot": "cnot",  # CNOT is self-inverse
        "cx": "cx",  # CX is self-inverse
        "swap": "swap",  # SWAP is self-inverse
        "cz": "cz",  # CZ is self-inverse
    }

    @staticmethod
    def get_inverse_gate(gate):
        """
        Get the inverse of a gate, handling parameterized gates.

        Args:
            gate: Gate object with attributes (name, matrix, qubits, params)

        Returns:
            Inverse Gate object

        Raises:
            ValueError: If gate inverse is not known
        """
        from quantum_debugger.core.gates import Gate

        gate_name = gate.name.lower()

        # Check for simple inverse mappings
        if gate_name in CircuitFolder.INVERSE_MAP:
            inv_name = CircuitFolder.INVERSE_MAP[gate_name]

            # For self-inverse gates, return copy with same matrix
            if inv_name == gate_name:
                return Gate(
                    inv_name, gate.matrix.copy(), gate.qubits.copy(), gate.params.copy()
                )
            else:
                # Map to different gate name (S <-> Sdg, T <-> Tdg)
                # Need to compute inverse matrix
                inv_matrix = np.conjugate(gate.matrix.T)
                return Gate(
                    inv_name, inv_matrix, gate.qubits.copy(), gate.params.copy()
                )

        # Handle parameterized rotation gates
        if gate_name in ["rx", "ry", "rz", "p", "phase"]:
            # Inverse is same gate with negated parameter
            if "angle" in gate.params:
                inv_params = {"angle": -gate.params["angle"]}
                # Compute inverse matrix (rotation by -angle)
                inv_matrix = np.conjugate(gate.matrix.T)
                return Gate(gate_name, inv_matrix, gate.qubits.copy(), inv_params)
            elif gate.params:
                # Generic parameter negation
                inv_params = {k: -v for k, v in gate.params.items()}
                inv_matrix = np.conjugate(gate.matrix.T)
                return Gate(gate_name, inv_matrix, gate.qubits.copy(), inv_params)

        # Handle controlled-phase (CP)
        if gate_name in ["cp", "crz"]:
            if "angle" in gate.params:
                inv_params = {"angle": -gate.params["angle"]}
                inv_matrix = np.conjugate(gate.matrix.T)
                return Gate(gate_name, inv_matrix, gate.qubits.copy(), inv_params)

        # General case: use conjugate transpose of matrix
        inv_matrix = np.conjugate(gate.matrix.T)
        return Gate(
            gate.name + "_inv", inv_matrix, gate.qubits.copy(), gate.params.copy()
        )

    @staticmethod
    def invert_circuit(circuit):
        """
        Create the inverse of an entire circuit.

        Args:
            circuit: QuantumCircuit to invert

        Returns:
            Inverted circuit (gates in reverse order, each inverted)
        """

        # Create new circuit with same parameters
        inv_circuit_gates = []

        # Reverse order and invert each gate
        for gate in reversed(circuit.gates):
            inv_gate = CircuitFolder.get_inverse_gate(gate)
            inv_circuit_gates.append(inv_gate)

        return inv_circuit_gates


def global_fold(circuit, scale_factor: float):
    """
    Global circuit folding: C → C + C† + C

    Amplifies noise by factor approximately equal to scale_factor.

    Args:
        circuit: QuantumCircuit to fold
        scale_factor: Target noise scaling (>= 1.0)
                     scale=1.0: original circuit
                     scale=3.0: C + C† + C (2 folds)
                     scale=5.0: C + (C† + C) * 2

    Returns:
        Folded circuit with amplified noise

    Example:
        >>> circuit = QuantumCircuit(2)
        >>> circuit.h(0).cnot(0, 1)
        >>> folded = global_fold(circuit, scale_factor=3.0)
        >>> # folded has 3x the gates and ~3x the noise
    """
    if scale_factor < 1.0:
        raise ValueError(f"Scale factor must be >= 1.0, got {scale_factor}")

    if scale_factor == 1.0:
        return circuit

    from copy import deepcopy

    folded = deepcopy(circuit)
    num_folds = int((scale_factor - 1) / 2)

    for _ in range(num_folds):
        # Append C† (inverted gates)
        inv_gates = CircuitFolder.invert_circuit(circuit)
        folded.gates.extend(inv_gates)

        # Append C (original gates)
        folded.gates.extend(deepcopy(circuit.gates))

    return folded


def local_fold(circuit, scale_factor: float, gate_indices: Optional[List[int]] = None):
    """
    Local circuit folding: fold only specific gates.

    Better for targeted error mitigation of high-error gates (e.g., CNOT).

    Args:
        circuit: QuantumCircuit to fold
        scale_factor: Target noise scaling
        gate_indices: Indices of gates to fold. If None, fold two-qubit gates

    Returns:
        Locally folded circuit

    Example:
        >>> circuit = create_vqe_circuit()
        >>> # Fold only CNOT gates (highest error rate)
        >>> folded = local_fold(circuit, scale_factor=2.0)
    """
    if scale_factor < 1.0:
        raise ValueError(f"Scale factor must be >= 1.0, got {scale_factor}")

    if scale_factor == 1.0:
        return circuit

    from copy import deepcopy

    # If no indices specified, fold two-qubit gates (highest error)
    if gate_indices is None:
        gate_indices = [
            i
            for i, gate in enumerate(circuit.gates)
            if len(gate.qubits) > 1  # Two-qubit gates
        ]

    if not gate_indices:
        # No gates to fold, return original
        return circuit

    # Calculate how many times to fold each gate
    num_folds = int((scale_factor - 1) / 2)

    folded = type(circuit)(circuit.num_qubits, circuit.num_classical)

    for i, gate in enumerate(circuit.gates):
        # Add original gate
        folded.gates.append(deepcopy(gate))

        # If this gate should be folded, add G† G pairs
        if i in gate_indices:
            inv_gate = CircuitFolder.get_inverse_gate(gate)
            for _ in range(num_folds):
                folded.gates.append(inv_gate)
                folded.gates.append(deepcopy(gate))

    return folded


def adaptive_fold(
    circuit, scale_factor: float, gate_error_rates: Optional[Dict[str, float]] = None
):
    """
    Adaptive folding: fold gates proportional to their error rates.

    Gates with higher error rates are folded more aggressively.

    Args:
        circuit: QuantumCircuit to fold
        scale_factor: Target noise scaling
        gate_error_rates: Dict mapping gate names to error rates
                         If None, uses default hardware error rates

    Returns:
        Adaptively folded circuit

    Example:
        >>> error_rates = {'cnot': 0.01, 'h': 0.0003, 'rx': 0.0005}
        >>> folded = adaptive_fold(circuit, 2.0, error_rates)
    """
    if gate_error_rates is None:
        # Default error rates (typical for superconducting qubits)
        gate_error_rates = {
            "cnot": 10.0,  # Highest error (normalized)
            "cx": 10.0,
            "cz": 8.0,
            "swap": 8.0,
            "rx": 1.0,
            "ry": 1.0,
            "rz": 1.0,
            "p": 1.0,
            "h": 0.5,
            "x": 0.5,
            "y": 0.5,
            "z": 0.1,  # Lowest error (virtual gate)
            "s": 0.5,
            "t": 0.5,
        }

    # Sort gates by error rate
    gate_errors = []
    for i, gate in enumerate(circuit.gates):
        error_rate = gate_error_rates.get(gate.name.lower(), 1.0)
        gate_errors.append((i, error_rate))

    # Sort by error rate (descending)
    gate_errors.sort(key=lambda x: x[1], reverse=True)

    # Select top gates to fold based on cumulative error contribution
    total_error = sum(err for _, err in gate_errors)
    cumulative_error = 0
    gates_to_fold = []

    for idx, error in gate_errors:
        cumulative_error += error
        gates_to_fold.append(idx)

        # Stop when we've covered enough high-error gates
        if cumulative_error / total_error > 0.7:  # Fold top 70% error contributors
            break

    # Use local folding on selected gates
    return local_fold(circuit, scale_factor, gates_to_fold)
