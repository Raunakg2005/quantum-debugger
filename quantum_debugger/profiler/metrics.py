"""
Circuit metrics and analysis
"""

from typing import Dict, List
from quantum_debugger.core.circuit import QuantumCircuit


class CircuitMetrics:
    """Container for circuit analysis metrics"""

    def __init__(self, circuit: QuantumCircuit):
        self.circuit = circuit
        self._compute_metrics()

    def _compute_metrics(self):
        """Compute all metrics"""
        self.num_qubits = self.circuit.num_qubits
        self.total_gates = len(self.circuit.gates)
        self.depth = self.circuit.depth()

        # Gate type counts
        self.gate_counts = {}
        for gate in self.circuit.gates:
            name = gate.name
            self.gate_counts[name] = self.gate_counts.get(name, 0) + 1

        # Special counts
        self.single_qubit_gates = sum(
            1 for g in self.circuit.gates if len(g.qubits) == 1
        )
        self.two_qubit_gates = sum(1 for g in self.circuit.gates if len(g.qubits) == 2)
        self.three_qubit_gates = sum(
            1 for g in self.circuit.gates if len(g.qubits) == 3
        )

        self.cnot_count = self.gate_counts.get("CNOT", 0) + self.gate_counts.get(
            "CX", 0
        )
        self.t_count = self.gate_counts.get("T", 0)

        # Critical path analysis
        self.critical_path = self._find_critical_path()

        # Parallelism factor
        self.parallelism = self.total_gates / self.depth if self.depth > 0 else 0

    def _find_critical_path(self) -> List[int]:
        """Find the critical path (longest dependency chain)"""
        if not self.circuit.gates:
            return []

        # Track dependencies
        qubit_last_gate = {}
        gate_start_time = []

        for i, gate in enumerate(self.circuit.gates):
            # Find latest dependency
            start_time = 0
            for q in gate.qubits:
                if q in qubit_last_gate:
                    start_time = max(
                        start_time, gate_start_time[qubit_last_gate[q]] + 1
                    )

            gate_start_time.append(start_time)

            # Update last gate for each qubit
            for q in gate.qubits:
                qubit_last_gate[q] = i

        # Find path with maximum start time
        max_time = max(gate_start_time)
        critical_gates = [i for i, t in enumerate(gate_start_time) if t == max_time]

        return critical_gates

    def get_summary(self) -> Dict:
        """Get summary dictionary of all metrics"""
        return {
            "num_qubits": self.num_qubits,
            "total_gates": self.total_gates,
            "depth": self.depth,
            "single_qubit_gates": self.single_qubit_gates,
            "two_qubit_gates": self.two_qubit_gates,
            "three_qubit_gates": self.three_qubit_gates,
            "cnot_count": self.cnot_count,
            "t_count": self.t_count,
            "parallelism_factor": self.parallelism,
            "gate_counts": self.gate_counts,
            "critical_path_length": len(self.critical_path),
        }

    def estimate_execution_time(
        self, gate_time: float = 1.0, cnot_time: float = 10.0
    ) -> float:
        """
        Estimate execution time on quantum hardware

        Args:
            gate_time: Time for single-qubit gate (μs)
            cnot_time: Time for CNOT gate (μs)

        Returns:
            Estimated time in microseconds
        """
        single_time = self.single_qubit_gates * gate_time
        two_time = self.two_qubit_gates * cnot_time

        return single_time + two_time

    def estimate_error_rate(
        self, single_error: float = 0.001, cnot_error: float = 0.01
    ) -> float:
        """
        Estimate cumulative error rate

        Args:
            single_error: Error rate for single-qubit gates
            cnot_error: Error rate for CNOT gates

        Returns:
            Estimated cumulative error rate
        """
        # Simplified error model (multiplicative)
        single_fidelity = (1 - single_error) ** self.single_qubit_gates
        two_fidelity = (1 - cnot_error) ** self.two_qubit_gates

        total_fidelity = single_fidelity * two_fidelity
        return 1 - total_fidelity

    def __repr__(self):
        return f"CircuitMetrics({self.num_qubits} qubits, {self.total_gates} gates, depth {self.depth})"
