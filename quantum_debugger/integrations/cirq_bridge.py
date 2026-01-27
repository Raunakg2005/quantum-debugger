"""
Cirq Bridge

Convert between quantum-debugger and Cirq (Google) formats.
"""

import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Check if Cirq is available
try:
    import cirq

    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False
    logger.debug("Cirq not available - install with: pip install cirq")


def from_cirq(cirq_circuit) -> List[Tuple]:
    """
    Convert Cirq circuit to quantum-debugger format.

    Args:
        cirq_circuit: Cirq Circuit

    Returns:
        List of gate tuples

    Examples:
        >>> import cirq
        >>> qubits = cirq.LineQubit.range(2)
        >>> circuit = cirq.Circuit()
        >>> circuit.append(cirq.H(qubits[0]))
        >>> circuit.append(cirq.CNOT(qubits[0], qubits[1]))
        >>> gates = from_cirq(circuit)
    """
    if not CIRQ_AVAILABLE:
        raise ImportError("Cirq not installed. Install with: pip install cirq")

    gates = []

    # Build qubit index map
    all_qubits = sorted(cirq_circuit.all_qubits())
    qubit_map = {q: i for i, q in enumerate(all_qubits)}

    for moment in cirq_circuit:
        for op in moment:
            gate = op.gate
            qubits = [qubit_map[q] for q in op.qubits]

            # Determine gate name
            gate_name = str(gate).lower().split("(")[0]

            # Map Cirq names
            name_map = {
                "h": "h",
                "x": "x",
                "y": "y",
                "z": "z",
                "s": "s",
                "t": "t",
                "cnot": "cnot",
                "cx": "cnot",
                "cz": "cz",
                "swap": "swap",
            }

            mapped_name = name_map.get(gate_name, gate_name)

            # Rotation gates
            if "rx" in gate_name or "ry" in gate_name or "rz" in gate_name:
                # Extract angle
                if hasattr(gate, "exponent"):
                    angle = gate.exponent * np.pi
                    if "rx" in gate_name:
                        gates.append(("rx", qubits[0], angle))
                    elif "ry" in gate_name:
                        gates.append(("ry", qubits[0], angle))
                    elif "rz" in gate_name:
                        gates.append(("rz", qubits[0], angle))
                continue

            # Single qubit
            if len(qubits) == 1:
                gates.append((mapped_name, qubits[0]))

            # Two qubit
            elif len(qubits) == 2:
                gates.append((mapped_name, tuple(qubits)))

    logger.info(f"Converted Cirq circuit: {len(gates)} gates")

    return gates


def to_cirq(gates: List[Tuple]) -> "cirq.Circuit":
    """
    Convert quantum-debugger format to Cirq circuit.

    Args:
        gates: List of gate tuples

    Returns:
        Cirq Circuit

    Examples:
        >>> gates = [('h', 0), ('cnot', (0, 1))]
        >>> circuit = to_cirq(gates)
        >>> print(circuit)
    """
    if not CIRQ_AVAILABLE:
        raise ImportError("Cirq not installed. Install with: pip install cirq")

    # Determine number of qubits
    max_qubit = 0
    for gate in gates:
        if isinstance(gate, tuple) and len(gate) >= 2:
            qubits = gate[1]
            if isinstance(qubits, int):
                max_qubit = max(max_qubit, qubits)
            elif isinstance(qubits, (tuple, list)):
                max_qubit = max(max_qubit, max(qubits))

    # Create qubits
    qubits = cirq.LineQubit.range(max_qubit + 1)
    circuit = cirq.Circuit()

    for gate in gates:
        if not isinstance(gate, tuple):
            continue

        gate_name = gate[0]

        # Single qubit gates
        if len(gate) >= 2 and isinstance(gate[1], int):
            qubit_idx = gate[1]
            q = qubits[qubit_idx]
            params = gate[2:] if len(gate) > 2 else []

            if gate_name == "h":
                circuit.append(cirq.H(q))
            elif gate_name == "x":
                circuit.append(cirq.X(q))
            elif gate_name == "y":
                circuit.append(cirq.Y(q))
            elif gate_name == "z":
                circuit.append(cirq.Z(q))
            elif gate_name == "s":
                circuit.append(cirq.S(q))
            elif gate_name == "t":
                circuit.append(cirq.T(q))
            elif gate_name == "rx" and params:
                circuit.append(cirq.rx(params[0])(q))
            elif gate_name == "ry" and params:
                circuit.append(cirq.ry(params[0])(q))
            elif gate_name == "rz" and params:
                circuit.append(cirq.rz(params[0])(q))

        # Two qubit gates
        elif len(gate) >= 2 and isinstance(gate[1], (tuple, list)):
            qubit_indices = gate[1]
            if len(qubit_indices) == 2:
                q1, q2 = qubits[qubit_indices[0]], qubits[qubit_indices[1]]

                if gate_name in ["cnot", "cx"]:
                    circuit.append(cirq.CNOT(q1, q2))
                elif gate_name == "cz":
                    circuit.append(cirq.CZ(q1, q2))
                elif gate_name == "swap":
                    circuit.append(cirq.SWAP(q1, q2))

    logger.info(f"Created Cirq circuit: {len(qubits)} qubits, {len(circuit)} moments")

    return circuit


def is_cirq_available() -> bool:
    """Check if Cirq is available."""
    return CIRQ_AVAILABLE
