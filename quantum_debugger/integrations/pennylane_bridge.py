"""
PennyLane Bridge

Convert between quantum-debugger and PennyLane formats.
"""

from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Check if PennyLane is available
try:
    import pennylane as qml

    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False
    logger.debug("PennyLane not available - install with: pip install pennylane")


def from_pennylane(pennylane_tape) -> List[Tuple]:
    """
    Convert PennyLane tape/circuit to quantum-debugger format.

    Args:
        pennylane_tape: PennyLane QuantumTape or operations list

    Returns:
        List of gate tuples

    Examples:
        >>> import pennylane as qml
        >>> dev = qml.device('default.qubit', wires=2)
        >>> @qml.qnode(dev)
        >>> def circuit():
        ...     qml.Hadamard(wires=0)
        ...     qml.CNOT(wires=[0, 1])
        ...     return qml.expval(qml.PauliZ(0))
        >>> gates = from_pennylane(circuit.tape)
    """
    if not PENNYLANE_AVAILABLE:
        raise ImportError(
            "PennyLane not installed. Install with: pip install pennylane"
        )

    gates = []

    # Get operations from tape
    ops = (
        pennylane_tape.operations
        if hasattr(pennylane_tape, "operations")
        else pennylane_tape
    )

    for op in ops:
        op_name = op.name.lower()
        wires = op.wires.tolist()
        params = op.parameters if hasattr(op, "parameters") else []

        # Map PennyLane names to our format
        name_map = {
            "hadamard": "h",
            "paulix": "x",
            "pauliy": "y",
            "pauliz": "z",
            "cnot": "cnot",
            "cz": "cz",
            "swap": "swap",
            "rx": "rx",
            "ry": "ry",
            "rz": "rz",
            "s": "s",
            "t": "t",
        }

        gate_name = name_map.get(op_name, op_name)

        # Single qubit
        if len(wires) == 1:
            qubit = wires[0]
            if params:
                gates.append((gate_name, qubit, *params))
            else:
                gates.append((gate_name, qubit))

        # Multi qubit
        else:
            gates.append((gate_name, tuple(wires)))

    logger.info(f"Converted PennyLane circuit: {len(gates)} gates")

    return gates


def _detect_num_wires(gates: List[Tuple]) -> int:
    """Auto-detect number of wires from gate list for PennyLane."""
    max_wire = 0
    for gate in gates:
        if isinstance(gate, tuple) and len(gate) >= 2:
            wires = gate[1]
            if isinstance(wires, int):
                max_wire = max(max_wire, wires)
            elif isinstance(wires, (tuple, list)):
                max_wire = max(max_wire, max(wires))
    return max_wire + 1


def _add_single_qubit_gate_pennylane(gate_name: str, wire: int, params: List):
    """Add single qubit gate to PennyLane circuit."""
    gate_map = {
        "h": lambda: qml.Hadamard(wires=wire),
        "x": lambda: qml.PauliX(wires=wire),
        "y": lambda: qml.PauliY(wires=wire),
        "z": lambda: qml.PauliZ(wires=wire),
        "s": lambda: qml.S(wires=wire),
        "t": lambda: qml.T(wires=wire),
    }

    if gate_name in gate_map:
        gate_map[gate_name]()
    elif gate_name == "rx" and params:
        qml.RX(params[0], wires=wire)
    elif gate_name == "ry" and params:
        qml.RY(params[0], wires=wire)
    elif gate_name == "rz" and params:
        qml.RZ(params[0], wires=wire)


def _add_two_qubit_gate_pennylane(gate_name: str, wires_tuple):
    """Add two qubit gate to PennyLane circuit."""
    if gate_name in ["cnot", "cx"]:
        qml.CNOT(wires=list(wires_tuple))
    elif gate_name == "cz":
        qml.CZ(wires=list(wires_tuple))
    elif gate_name == "swap":
        qml.SWAP(wires=list(wires_tuple))


def to_pennylane(gates: List[Tuple], device_name: str = "default.qubit") -> "qml.QNode":
    """
    Convert quantum-debugger format to PennyLane QNode.

    Args:
        gates: List of gate tuples
        device_name: PennyLane device name

    Returns:
        PennyLane QNode function

    Examples:
        >>> gates = [('h', 0), ('cnot', (0, 1))]
        >>> qnode = to_pennylane(gates)
        >>> result = qnode()
    """
    if not PENNYLANE_AVAILABLE:
        raise ImportError(
            "PennyLane not installed. Install with: pip install pennylane"
        )

    # Determine number of wires and create device
    n_wires = _detect_num_wires(gates)
    dev = qml.device(device_name, wires=n_wires)

    def circuit():
        for gate in gates:
            if not isinstance(gate, tuple):
                continue

            gate_name = gate[0]

            # Single qubit gates
            if len(gate) >= 2 and isinstance(gate[1], int):
                wire = gate[1]
                params = gate[2:] if len(gate) > 2 else []
                _add_single_qubit_gate_pennylane(gate_name, wire, params)

            # Two qubit gates
            elif len(gate) >= 2 and isinstance(gate[1], (tuple, list)):
                wires_tuple = gate[1]
                _add_two_qubit_gate_pennylane(gate_name, wires_tuple)

        # Return measurement (default: Z on first qubit)
        return qml.expval(qml.PauliZ(0))

    qnode = qml.QNode(circuit, dev)

    logger.info(f"Created PennyLane QNode: {n_wires} wires")

    return qnode


def is_pennylane_available() -> bool:
    """Check if PennyLane is available."""
    return PENNYLANE_AVAILABLE
