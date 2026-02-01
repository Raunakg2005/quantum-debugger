"""
Qiskit Bridge

Convert between quantum-debugger and Qiskit circuit formats.
"""

from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Check if Qiskit is available
try:
    from qiskit import QuantumCircuit

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger.debug("Qiskit not available - install with: pip install qiskit")


def from_qiskit(qiskit_circuit) -> List[Tuple]:
    """
    Convert Qiskit circuit to quantum-debugger format.

    Args:
        qiskit_circuit: Qiskit QuantumCircuit

    Returns:
        List of gate tuples in quantum-debugger format

    Examples:
        >>> from qiskit import QuantumCircuit
        >>> qc = QuantumCircuit(2)
        >>> qc.h(0)
        >>> qc.cx(0, 1)
        >>> gates = from_qiskit(qc)
        >>> print(gates)  # [('h', 0), ('cnot', (0, 1))]
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit not installed. Install with: pip install qiskit")

    gates = []

    for instruction, qubits, _ in qiskit_circuit.data:
        gate_name = instruction.name.lower()
        qubit_indices = tuple(q._index for q in qubits)

        # Single qubit gate
        if len(qubit_indices) == 1:
            qubit = qubit_indices[0]

            # Parameterized gates
            if hasattr(instruction, "params") and instruction.params:
                params = instruction.params
                if gate_name in ["rx", "ry", "rz", "p", "u1", "u2", "u3"]:
                    gates.append((gate_name, qubit, *params))
                else:
                    gates.append((gate_name, qubit))
            else:
                gates.append((gate_name, qubit))

        # Two qubit gate
        elif len(qubit_indices) == 2:
            # Map Qiskit names to our names
            name_map = {"cx": "cnot", "cz": "cz", "swap": "swap"}
            mapped_name = name_map.get(gate_name, gate_name)

            gates.append((mapped_name, qubit_indices))

        else:
            # Multi-qubit gate
            gates.append((gate_name, qubit_indices))

    logger.info(
        f"Converted Qiskit circuit: {len(gates)} gates, {qiskit_circuit.num_qubits} qubits"
    )

    return gates


def _detect_num_qubits(gates: List[Tuple]) -> int:
    """Auto-detect number of qubits from gate list."""
    max_qubit = 0
    for gate in gates:
        if isinstance(gate, tuple) and len(gate) >= 2:
            qubits = gate[1]
            if isinstance(qubits, int):
                max_qubit = max(max_qubit, qubits)
            elif isinstance(qubits, (tuple, list)):
                max_qubit = max(max_qubit, max(qubits))
    return max_qubit + 1


def _add_single_qubit_gate(qc: "QuantumCircuit", gate_name: str, qubit: int, params: List):
    """Add single qubit gate to Qiskit circuit."""
    gate_map = {
        "h": lambda: qc.h(qubit),
        "x": lambda: qc.x(qubit),
        "y": lambda: qc.y(qubit),
        "z": lambda: qc.z(qubit),
        "s": lambda: qc.s(qubit),
        "t": lambda: qc.t(qubit),
        "s_dagger": lambda: qc.sdg(qubit),
        "t_dagger": lambda: qc.tdg(qubit),
    }

    if gate_name in gate_map:
        gate_map[gate_name]()
    elif gate_name == "rx" and params:
        qc.rx(params[0], qubit)
    elif gate_name == "ry" and params:
        qc.ry(params[0], qubit)
    elif gate_name == "rz" and params:
        qc.rz(params[0], qubit)
    elif gate_name == "u3" and len(params) == 3:
        qc.u(params[0], params[1], params[2], qubit)


def _add_two_qubit_gate(qc: "QuantumCircuit", gate_name: str, qubits: Tuple[int, int]):
    """Add two qubit gate to Qiskit circuit."""
    q1, q2 = qubits

    if gate_name in ["cnot", "cx"]:
        qc.cx(q1, q2)
    elif gate_name == "cz":
        qc.cz(q1, q2)
    elif gate_name == "swap":
        qc.swap(q1, q2)


def to_qiskit(gates: List[Tuple], n_qubits: Optional[int] = None) -> "QuantumCircuit":
    """
    Convert quantum-debugger format to Qiskit circuit.

    Args:
        gates: List of gate tuples
        n_qubits: Number of qubits (auto-detected if None)

    Returns:
        Qiskit QuantumCircuit

    Examples:
        >>> gates = [('h', 0), ('cnot', (0, 1))]
        >>> qc = to_qiskit(gates)
        >>> print(qc)
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit not installed. Install with: pip install qiskit")

    # Auto-detect qubits if not provided
    if n_qubits is None:
        n_qubits = _detect_num_qubits(gates)

    qc = QuantumCircuit(n_qubits)

    for gate in gates:
        if not isinstance(gate, tuple):
            continue

        gate_name = gate[0]

        # Single qubit gates
        if len(gate) >= 2 and isinstance(gate[1], int):
            qubit = gate[1]
            params = gate[2:] if len(gate) > 2 else []
            _add_single_qubit_gate(qc, gate_name, qubit, params)

        # Two qubit gates
        elif len(gate) >= 2 and isinstance(gate[1], (tuple, list)):
            qubits = gate[1]
            if len(qubits) == 2:
                _add_two_qubit_gate(qc, gate_name, qubits)

    logger.info(f"Created Qiskit circuit: {qc.num_qubits} qubits, {len(qc.data)} gates")

    return qc


def is_qiskit_available() -> bool:
    """Check if Qiskit is available."""
    return QISKIT_AVAILABLE
