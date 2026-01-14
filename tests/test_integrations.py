"""
Tests for framework integrations (Qiskit, PennyLane, Cirq bridges)
"""

import pytest
import numpy as np

from quantum_debugger.integrations import (
    QISKIT_AVAILABLE,
    PENNYLANE_AVAILABLE,
    CIRQ_AVAILABLE,
    get_available_frameworks
)


class TestFrameworkAvailability:
    """Test framework detection"""
    
    def test_get_available_frameworks(self):
        """Test getting list of available frameworks"""
        frameworks = get_available_frameworks()
        
        # Should return a list
        assert isinstance(frameworks, list)
        
        # Each should be a string
        assert all(isinstance(f, str) for f in frameworks)
    
    def test_framework_flags(self):
        """Test framework availability flags are booleans"""
        assert isinstance(QISKIT_AVAILABLE, bool)
        assert isinstance(PENNYLANE_AVAILABLE, bool)
        assert isinstance(CIRQ_AVAILABLE, bool)


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
class TestQiskitBridge:
    """Test Qiskit integration"""
    
    def test_from_qiskit_basic(self):
        """Test basic Qiskit circuit import"""
        from qiskit import QuantumCircuit
        from quantum_debugger.integrations import from_qiskit
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        gates = from_qiskit(qc)
        
        assert len(gates) == 2
        assert gates[0][0] == 'h'
        assert gates[1][0] in ['cnot', 'cx']
    
    def test_to_qiskit_basic(self):
        """Test basic circuit export to Qiskit"""
        from quantum_debugger.integrations import to_qiskit
        
        gates = [('h', 0), ('cnot', (0, 1))]
        qc = to_qiskit(gates)
        
        assert qc.num_qubits == 2
        assert len(qc.data) == 2
    
    def test_qiskit_roundtrip(self):
        """Test Qiskit import/export roundtrip"""
        from qiskit import QuantumCircuit
        from quantum_debugger.integrations import from_qiskit, to_qiskit
        
        # Original circuit
        qc1 = QuantumCircuit(2)
        qc1.h(0)
        qc1.x(1)
        
        # Convert to our format and back
        gates = from_qiskit(qc1)
        qc2 = to_qiskit(gates)
        
        assert qc1.num_qubits == qc2.num_qubits
        assert len(qc1.data) == len(qc2.data)


@pytest.mark.skipif(not PENNYLANE_AVAILABLE, reason="PennyLane not installed")
class TestPennyLaneBridge:
    """Test PennyLane integration"""
    
    def test_to_pennylane_basic(self):
        """Test basic circuit export to PennyLane"""
        from quantum_debugger.integrations import to_pennylane
        
        gates = [('h', 0), ('cnot', (0, 1))]
        qnode = to_pennylane(gates)
        
        # Should be callable
        assert callable(qnode)
        
        # Should execute
        result = qnode()
        assert isinstance(result, (float, np.floating))


@pytest.mark.skipif(not CIRQ_AVAILABLE, reason="Cirq not installed")
class TestCirqBridge:
    """Test Cirq integration"""
    
    def test_from_cirq_basic(self):
        """Test basic Cirq circuit import"""
        import cirq
        from quantum_debugger.integrations import from_cirq
        
        qubits = cirq.LineQubit.range(2)
        circuit = cirq.Circuit()
        circuit.append(cirq.H(qubits[0]))
        circuit.append(cirq.CNOT(qubits[0], qubits[1]))
        
        gates = from_cirq(circuit)
        
        assert len(gates) >= 2
        assert any(g[0] == 'h' for g in gates)
    
    def test_to_cirq_basic(self):
        """Test basic circuit export to Cirq"""
        from quantum_debugger.integrations import to_cirq
        
        gates = [('h', 0), ('cnot', (0, 1))]
        circuit = to_cirq(gates)
        
        assert len(circuit.all_qubits()) == 2
        assert len(circuit) >= 1  # At least one moment


class TestIntegrationWorkflows:
    """Test complete integration workflows"""
    
    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_qiskit_with_optimization(self):
        """Test using Qiskit circuit with quantum-debugger optimization"""
        from qiskit import QuantumCircuit
        from quantum_debugger.integrations import from_qiskit, to_qiskit
        from quantum_debugger.optimization import optimize_circuit
        
        # Create circuit with redundancy
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.h(0)  # Will cancel
        qc.x(1)
        
        # Optimize
        gates = from_qiskit(qc)
        optimized_gates = optimize_circuit(gates)
        
        # Should have fewer gates
        assert len(optimized_gates) < len(gates)
        
        # Convert back
        qc_opt = to_qiskit(optimized_gates)
        assert qc_opt.num_qubits == qc.num_qubits
    
    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_qiskit_with_compilation(self):
        """Test using Qiskit with circuit compiler"""
        from qiskit import QuantumCircuit
        from quantum_debugger.integrations import from_qiskit
        from quantum_debugger.optimization import compile_circuit
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        gates = from_qiskit(qc)
        compiled = compile_circuit(gates, optimization_level=2)
        
        # Should still have gates
        assert len(compiled) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
