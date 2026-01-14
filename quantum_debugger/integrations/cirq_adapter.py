"""
Cirq Adapter - Convert between Cirq and QuantumDebugger circuits

This module provides bidirectional conversion:
- Import Cirq Circuit → QuantumDebugger circuit
- Export QuantumDebugger circuit → Cirq Circuit
"""

import numpy as np
from typing import Optional, List, Tuple

try:
    import cirq

    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False
    cirq = None

from ..core.circuit import QuantumCircuit as QDCircuit


class CirqAdapter:
    """Adapter for converting between Cirq and QuantumDebugger circuits"""

    # Gate name mapping: Cirq → QuantumDebugger
    GATE_MAP = {
        "H": "h",
        "X": "x",
        "Y": "y",
        "Z": "z",
        "S": "s",
        "T": "t",
        "CNOT": "cnot",
        "CX": "cnot",
        "CZ": "cz",
        "SWAP": "swap",
        "TOFFOLI": "toffoli",
        "CCX": "toffoli",
        "Rx": "rx",
        "Ry": "ry",
        "Rz": "rz",
    }

    @staticmethod
    def check_cirq_available():
        """Check if Cirq is installed"""
        if not CIRQ_AVAILABLE:
            raise ImportError("Cirq is not installed. Install with: pip install cirq")

    @classmethod
    def from_cirq(cls, cirq_circuit: "cirq.Circuit") -> QDCircuit:
        """
        Convert a Cirq Circuit to QuantumDebugger circuit

        Args:
            cirq_circuit: Cirq Circuit to convert

        Returns:
            QuantumDebugger QuantumCircuit

        Example:
            >>> import cirq
            >>> q0, q1 = cirq.LineQubit.range(2)
            >>> cirq_circuit = cirq.Circuit()
            >>> cirq_circuit.append([cirq.H(q0), cirq.CNOT(q0, q1)])
            >>> qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        """
        cls.check_cirq_available()

        # Get all qubits and create mapping
        qubits = sorted(cirq_circuit.all_qubits())
        qubit_map = {q: i for i, q in enumerate(qubits)}
        num_qubits = len(qubits)

        # Create QuantumDebugger circuit
        qd_circuit = QDCircuit(num_qubits)

        # Convert each operation
        for moment in cirq_circuit:
            for operation in moment:
                gate = operation.gate
                gate_qubits = operation.qubits

                # Get qubit indices
                qubit_indices = [qubit_map[q] for q in gate_qubits]

                # Determine gate type using string comparison (more reliable)
                gate_str = str(gate).upper()
                gate_name = None
                params = []

                # Check gates by string representation
                if "H" == gate_str:
                    gate_name = "h"
                elif "X" == gate_str:
                    gate_name = "x"
                elif "Y" == gate_str:
                    gate_name = "y"
                elif "Z" == gate_str:
                    gate_name = "z"
                elif "S" == gate_str:
                    gate_name = "s"
                elif "T" == gate_str:
                    gate_name = "t"
                elif "CNOT" in gate_str or "CX" in gate_str:
                    gate_name = "cnot"
                elif "CZ" == gate_str:
                    gate_name = "cz"
                elif "SWAP" in gate_str:
                    gate_name = "swap"
                elif "CCX" in gate_str or "TOFFOLI" in gate_str:
                    gate_name = "toffoli"
                elif gate_str.startswith("RX"):
                    gate_name = "rx"
                    # Extract angle from gate
                    if hasattr(gate, "exponent"):
                        params = [gate.exponent * np.pi]
                    elif hasattr(gate, "_rads"):
                        params = [gate._rads]
                elif gate_str.startswith("RY"):
                    gate_name = "ry"
                    if hasattr(gate, "exponent"):
                        params = [gate.exponent * np.pi]
                    elif hasattr(gate, "_rads"):
                        params = [gate._rads]
                elif gate_str.startswith("RZ"):
                    gate_name = "rz"
                    if hasattr(gate, "exponent"):
                        params = [gate.exponent * np.pi]
                    elif hasattr(gate, "_rads"):
                        params = [gate._rads]

                # Apply gate to QuantumDebugger circuit
                if gate_name:
                    gate_method = getattr(qd_circuit, gate_name)
                    if params:
                        # Parameterized gate
                        gate_method(*params, *qubit_indices)
                    else:
                        # Standard gate
                        gate_method(*qubit_indices)
                else:
                    print(
                        f"Warning: Gate '{gate_str}' not supported in QuantumDebugger, skipping"
                    )

        return qd_circuit

    @classmethod
    def to_cirq(
        cls, qd_circuit: QDCircuit, qubits: Optional[List["cirq.Qubit"]] = None
    ) -> "cirq.Circuit":
        """
        Convert a QuantumDebugger circuit to Cirq Circuit

        Args:
            qd_circuit: QuantumDebugger circuit to convert
            qubits: Optional list of Cirq qubits to use. If None, LineQubits are created.

        Returns:
            Cirq Circuit

        Example:
            >>> from quantum_debugger import QuantumCircuit
            >>> qd_circuit = QuantumCircuit(2)
            >>> qd_circuit.h(0)
            >>> qd_circuit.cnot(0, 1)
            >>> cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        """
        cls.check_cirq_available()

        # Create qubits if not provided
        if qubits is None:
            qubits = [cirq.LineQubit(i) for i in range(qd_circuit.num_qubits)]
        elif len(qubits) != qd_circuit.num_qubits:
            raise ValueError(
                f"Number of qubits ({len(qubits)}) doesn't match circuit ({qd_circuit.num_qubits})"
            )

        # Create Cirq circuit
        cirq_circuit = cirq.Circuit()

        # Convert each gate
        for gate in qd_circuit.gates:
            gate_name = gate.name.lower()
            gate_qubits = [qubits[i] for i in gate.qubits]
            params = gate.params if gate.params else {}

            # Map to Cirq gates
            if gate_name == "h":
                cirq_circuit.append(cirq.H(gate_qubits[0]))
            elif gate_name == "x":
                cirq_circuit.append(cirq.X(gate_qubits[0]))
            elif gate_name == "y":
                cirq_circuit.append(cirq.Y(gate_qubits[0]))
            elif gate_name == "z":
                cirq_circuit.append(cirq.Z(gate_qubits[0]))
            elif gate_name == "s":
                cirq_circuit.append(cirq.S(gate_qubits[0]))
            elif gate_name == "t":
                cirq_circuit.append(cirq.T(gate_qubits[0]))
            elif gate_name == "cnot":
                cirq_circuit.append(cirq.CNOT(gate_qubits[0], gate_qubits[1]))
            elif gate_name == "cz":
                cirq_circuit.append(cirq.CZ(gate_qubits[0], gate_qubits[1]))
            elif gate_name == "swap":
                cirq_circuit.append(cirq.SWAP(gate_qubits[0], gate_qubits[1]))
            elif gate_name == "toffoli":
                cirq_circuit.append(
                    cirq.CCX(gate_qubits[0], gate_qubits[1], gate_qubits[2])
                )
            elif gate_name == "rx" and "theta" in params:
                # Convert radians to Cirq exponent
                exponent = params["theta"] / np.pi
                cirq_circuit.append(cirq.Rx(rads=params["theta"])(gate_qubits[0]))
            elif gate_name == "ry" and "theta" in params:
                cirq_circuit.append(cirq.Ry(rads=params["theta"])(gate_qubits[0]))
            elif gate_name == "rz" and "theta" in params:
                cirq_circuit.append(cirq.Rz(rads=params["theta"])(gate_qubits[0]))
            elif gate_name == "cp" and "theta" in params:
                # Controlled phase
                cirq_circuit.append(
                    cirq.CZPowGate(exponent=params["theta"] / np.pi)(
                        gate_qubits[0], gate_qubits[1]
                    )
                )
            elif gate_name == "phase" and "theta" in params:
                # Phase gate
                cirq_circuit.append(
                    cirq.ZPowGate(exponent=params["theta"] / np.pi)(gate_qubits[0])
                )
            else:
                print(
                    f"Warning: Gate '{gate_name}' not recognized for Cirq conversion, skipping"
                )

        return cirq_circuit

    @classmethod
    def compare_circuits(
        cls, cirq_circuit: "cirq.Circuit", qd_circuit: QDCircuit
    ) -> dict:
        """
        Compare a Cirq circuit with a QuantumDebugger circuit

        Returns:
            Dictionary with comparison results
        """
        cls.check_cirq_available()

        cirq_num_qubits = len(cirq_circuit.all_qubits())
        cirq_num_ops = sum(len(moment) for moment in cirq_circuit)

        return {
            "num_qubits_match": cirq_num_qubits == qd_circuit.num_qubits,
            "num_gates_match": cirq_num_ops == len(qd_circuit.gates),
            "cirq_qubits": cirq_num_qubits,
            "qd_qubits": qd_circuit.num_qubits,
            "cirq_gates": cirq_num_ops,
            "qd_gates": len(qd_circuit.gates),
        }

    @classmethod
    def simulate_cirq(cls, qd_circuit: QDCircuit) -> dict:
        """
        Simulate a QuantumDebugger circuit using Cirq's simulator

        Args:
            qd_circuit: QuantumDebugger circuit to simulate

        Returns:
            Dictionary with simulation results
        """
        cls.check_cirq_available()

        # Convert to Cirq
        cirq_circuit = cls.to_cirq(qd_circuit)

        # Simulate
        simulator = cirq.Simulator()
        result = simulator.simulate(cirq_circuit)

        return {
            "state_vector": result.final_state_vector,
            "measurements": (
                result.measurements if hasattr(result, "measurements") else None
            ),
        }
