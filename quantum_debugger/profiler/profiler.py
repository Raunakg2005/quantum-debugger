"""
Circuit profiler for performance analysis
"""

from typing import Dict, List
from quantum_debugger.core.circuit import QuantumCircuit
from quantum_debugger.profiler.metrics import CircuitMetrics


class CircuitProfiler:
    """Profiler for analyzing quantum circuit performance"""
    
    def __init__(self, circuit: QuantumCircuit):
        """
        Initialize profiler
        
        Args:
            circuit: Quantum circuit to profile
        """
        self.circuit = circuit
        self.metrics = CircuitMetrics(circuit)
    
    def analyze(self) -> CircuitMetrics:
        """
        Analyze the circuit and return metrics
        
        Returns:
            CircuitMetrics object with analysis results
        """
        return self.metrics
    
    def get_optimization_suggestions(self) -> List[str]:
        """
        Get suggestions for circuit optimization
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # High CNOT count
        if self.metrics.cnot_count > self.metrics.num_qubits * 3:
            suggestions.append(
                f"⚠️  High CNOT count ({self.metrics.cnot_count}). "
                "Consider CNOT reduction techniques."
            )
        
        # High T count
        if self.metrics.t_count > self.metrics.num_qubits * 2:
            suggestions.append(
                f"⚠️  High T-gate count ({self.metrics.t_count}). "
                "T-gates are expensive on fault-tolerant hardware."
            )
        
        # High depth
        if self.metrics.depth > self.metrics.num_qubits * 5:
            suggestions.append(
                f"⚠️  Circuit depth ({self.metrics.depth}) is high. "
                "Consider parallelizing gates."
            )
        
        # Low parallelism
        if self.metrics.parallelism < 1.5 and self.metrics.num_qubits > 2:
            suggestions.append(
                f"💡 Low parallelism factor ({self.metrics.parallelism:.2f}). "
                "Look for opportunities to execute gates in parallel."
            )
        
        # Consecutive gates on same qubit
        consecutive = self._find_consecutive_single_qubit_gates()
        if consecutive:
            suggestions.append(
                f"💡 Found {len(consecutive)} sequences of consecutive single-qubit gates. "
                "These could be combined into single rotations."
            )
        
        if not suggestions:
            suggestions.append("✅ Circuit appears well optimized!")
        
        return suggestions
    
    def _find_consecutive_single_qubit_gates(self) -> List[tuple]:
        """Find consecutive single-qubit gates on the same qubit"""
        consecutive = []
        
        for q in range(self.circuit.num_qubits):
            sequence = []
            for i, gate in enumerate(self.circuit.gates):
                if gate.qubits == [q] and len(gate.qubits) == 1:
                    sequence.append(i)
                else:
                    if len(sequence) >= 2:
                        consecutive.append((q, sequence))
                    sequence = []
            
            if len(sequence) >= 2:
                consecutive.append((q, sequence))
        
        return consecutive
    
    def compare_with_ideal(self) -> Dict:
        """
        Compare circuit with theoretical ideal
        
        Returns:
            Comparison metrics
        """
        # Theoretical minimum for common algorithms
        ideal_depth = self.metrics.num_qubits  # Very rough estimate
        
        return {
            'actual_depth': self.metrics.depth,
            'ideal_depth': ideal_depth,
            'depth_overhead': self.metrics.depth / ideal_depth if ideal_depth > 0 else 0,
            'gate_efficiency': self.metrics.parallelism
        }
    
    def print_report(self):
        """Print comprehensive profiling report"""
        print("\n" + "=" * 70)
        print(" " * 20 + "CIRCUIT PROFILING REPORT")
        print("=" * 70)
        
        # Basic metrics
        print(f"\n📊 BASIC METRICS")
        print(f"   Number of Qubits: {self.metrics.num_qubits}")
        print(f"   Total Gates: {self.metrics.total_gates}")
        print(f"   Circuit Depth: {self.metrics.depth}")
        print(f"   Parallelism Factor: {self.metrics.parallelism:.2f}")
        
        # Gate breakdown
        print(f"\n🔧 GATE BREAKDOWN")
        print(f"   Single-Qubit Gates: {self.metrics.single_qubit_gates}")
        print(f"   Two-Qubit Gates: {self.metrics.two_qubit_gates}")
        if self.metrics.three_qubit_gates > 0:
            print(f"   Three-Qubit Gates: {self.metrics.three_qubit_gates}")
        
        print(f"\n   Gate Type Counts:")
        for gate_name, count in sorted(self.metrics.gate_counts.items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"      {gate_name}: {count}")
        
        # Special metrics
        print(f"\n⚡ SPECIAL METRICS")
        print(f"   CNOT Count: {self.metrics.cnot_count}")
        print(f"   T-Gate Count: {self.metrics.t_count}")
        print(f"   Critical Path Length: {len(self.metrics.critical_path)} gates")
        
        # Performance estimates
        exec_time = self.metrics.estimate_execution_time()
        error_rate = self.metrics.estimate_error_rate()
        
        print(f"\n⏱️  PERFORMANCE ESTIMATES")
        print(f"   Estimated Execution Time: {exec_time:.2f} μs")
        print(f"   Estimated Error Rate: {error_rate*100:.4f}%")
        print(f"   Estimated Fidelity: {(1-error_rate)*100:.4f}%")
        
        # Optimization suggestions
        suggestions = self.get_optimization_suggestions()
        print(f"\n💡 OPTIMIZATION SUGGESTIONS")
        for suggestion in suggestions:
            print(f"   {suggestion}")
        
        # Comparison with ideal
        comparison = self.compare_with_ideal()
        print(f"\n📈 COMPARISON WITH IDEAL")
        print(f"   Actual Depth: {comparison['actual_depth']}")
        print(f"   Theoretical Minimum: {comparison['ideal_depth']}")
        print(f"   Depth Overhead: {comparison['depth_overhead']:.2f}x")
        
        print("=" * 70 + "\n")
    
    def __repr__(self):
        return f"CircuitProfiler({self.metrics})"
