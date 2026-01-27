"""
Qiskit Adapter - Convert between Qiskit and QuantumDebugger circuits

This module provides bidirectional conversion:
- Import Qiskit QuantumCircuit → QuantumDebugger circuit
- Export QuantumDebugger circuit → Qiskit QuantumCircuit
"""

try:
    from qiskit import QuantumCircuit as QiskitCircuit

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None

from ..core.circuit import QuantumCircuit as QDCircuit


class QiskitAdapter:
    """Adapter for converting between Qiskit and QuantumDebugger circuits"""

    # Gate name mapping: Qiskit → QuantumDebugger
    GATE_MAP = {
        "h": "h",
        "x": "x",
        "y": "y",
        "z": "z",
        "s": "s",
        "t": "t",
        "cx": "cnot",
        "cz": "cz",
        "cp": "cp",
        "swap": "swap",
        "ccx": "toffoli",
        "rx": "rx",
        "ry": "ry",
        "rz": "rz",
        "p": "phase",
    }

    @staticmethod
    def check_qiskit_available():
        """Check if Qiskit is installed"""
        if not QISKIT_AVAILABLE:
            raise ImportError(
                "Qiskit is not installed. Install with: pip install qiskit"
            )

    @classmethod
    def from_qiskit(cls, qiskit_circuit: "QiskitCircuit") -> QDCircuit:
        """
        Convert a Qiskit QuantumCircuit to QuantumDebugger circuit

        Args:
            qiskit_circuit: Qiskit QuantumCircuit to convert

        Returns:
            QuantumDebugger QuantumCircuit

        Example:
            >>> from qiskit import QuantumCircuit
            >>> qc_qiskit = QuantumCircuit(2)
            >>> qc_qiskit.h(0)
            >>> qc_qiskit.cx(0, 1)
            >>> qc_qd = QiskitAdapter.from_qiskit(qc_qiskit)
        """
        cls.check_qiskit_available()

        # Create QuantumDebugger circuit with same number of qubits
        num_qubits = qiskit_circuit.num_qubits
        qd_circuit = QDCircuit(num_qubits)

        # Convert each gate
        for instruction, qubits, clbits in qiskit_circuit.data:
            gate_name = instruction.name.lower()
            qubit_indices = [qiskit_circuit.find_bit(q).index for q in qubits]

            # Get parameters if any
            params = instruction.params if hasattr(instruction, "params") else []

            # Map gate name
            if gate_name in cls.GATE_MAP:
                qd_gate_name = cls.GATE_MAP[gate_name]

                # Apply gate to QuantumDebugger circuit
                if len(params) > 0:
                    # Parameterized gate
                    gate_method = getattr(qd_circuit, qd_gate_name)
                    gate_method(params[0], *qubit_indices)
                elif len(qubit_indices) == 1:
                    # Single-qubit gate
                    gate_method = getattr(qd_circuit, qd_gate_name)
                    gate_method(qubit_indices[0])
                elif len(qubit_indices) == 2:
                    # Two-qubit gate
                    gate_method = getattr(qd_circuit, qd_gate_name)
                    gate_method(qubit_indices[0], qubit_indices[1])
                elif len(qubit_indices) == 3:
                    # Three-qubit gate (Toffoli)
                    gate_method = getattr(qd_circuit, qd_gate_name)
                    gate_method(qubit_indices[0], qubit_indices[1], qubit_indices[2])
            else:
                print(
                    f"Warning: Gate '{gate_name}' not supported in QuantumDebugger, skipping"
                )

        return qd_circuit

    @classmethod
    def to_qiskit(cls, qd_circuit: QDCircuit) -> "QiskitCircuit":
        """
        Convert a QuantumDebugger circuit to Qiskit QuantumCircuit

        Args:
            qd_circuit: QuantumDebugger circuit to convert

        Returns:
            Qiskit QuantumCircuit

        Example:
            >>> from quantum_debugger import QuantumCircuit
            >>> qc_qd = QuantumCircuit(2)
            >>> qc_qd.h(0)
            >>> qc_qd.cnot(0, 1)
            >>> qc_qiskit = QiskitAdapter.to_qiskit(qc_qd)
        """
        cls.check_qiskit_available()

        # Create Qiskit circuit
        qiskit_circuit = QiskitCircuit(qd_circuit.num_qubits)

        # Reverse gate mapping
        reverse_map = {v: k for k, v in cls.GATE_MAP.items()}

        # Convert each gate
        for gate in qd_circuit.gates:
            gate_name = gate.name.lower()
            qubits = gate.qubits
            params = gate.params if gate.params else {}

            # Map gate name back to Qiskit
            if gate_name in reverse_map:
                qiskit_gate_name = reverse_map[gate_name]

                # Apply gate to Qiskit circuit
                if "theta" in params:
                    # Parameterized gate
                    gate_method = getattr(qiskit_circuit, qiskit_gate_name)
                    gate_method(params["theta"], *qubits)
                else:
                    # Standard gate
                    gate_method = getattr(qiskit_circuit, qiskit_gate_name)
                    gate_method(*qubits)
            else:
                print(
                    f"Warning: Gate '{gate_name}' not recognized for Qiskit conversion, skipping"
                )

        return qiskit_circuit

    @classmethod
    def compare_circuits(
        cls, qiskit_circuit: "QiskitCircuit", qd_circuit: QDCircuit
    ) -> dict:
        """
        Compare a Qiskit circuit with a QuantumDebugger circuit

        Returns:
            Dictionary with comparison results
        """
        cls.check_qiskit_available()

        return {
            "num_qubits_match": qiskit_circuit.num_qubits == qd_circuit.num_qubits,
            "num_gates_match": len(qiskit_circuit.data) == len(qd_circuit.gates),
            "qiskit_gates": len(qiskit_circuit.data),
            "qd_gates": len(qd_circuit.gates),
        }
