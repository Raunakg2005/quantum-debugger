"""
Tests for Cirq integration
"""

import pytest
import numpy as np

# Try to import Cirq
try:
    import cirq
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False

from quantum_debugger import QuantumCircuit
from quantum_debugger.integrations import CirqAdapter


@pytest.mark.skipif(not CIRQ_AVAILABLE, reason="Cirq not installed")
class TestCirqAdapter:
    """Test Cirq adapter functionality"""
    
    def test_cirq_availability_check(self):
        """Test that Cirq availability is correctly detected"""
        CirqAdapter.check_cirq_available()  # Should not raise if Cirq is available
    
    def test_from_cirq_bell_state(self):
        """Test converting Cirq Bell state to QuantumDebugger"""
        # Create Cirq circuit
        q0, q1 = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([
            cirq.H(q0),
            cirq.CNOT(q0, q1)
        ])
        
        # Convert to QuantumDebugger
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        # Verify
        assert qd_circuit.num_qubits == 2
        assert len(qd_circuit.gates) == 2
        assert qd_circuit.gates[0].name == 'H'
        assert qd_circuit.gates[1].name == 'CNOT'
    
    def test_to_cirq_bell_state(self):
        """Test converting QuantumDebugger Bell state to Cirq"""
        # Create QuantumDebugger circuit
        qd_circuit = QuantumCircuit(2)
        qd_circuit.h(0)
        qd_circuit.cnot(0, 1)
        
        # Convert to Cirq
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        
        # Verify
        assert len(list(cirq_circuit.all_qubits())) == 2
        ops = list(cirq_circuit.all_operations())
        assert len(ops) == 2
    
    def test_from_cirq_single_qubit_gates(self):
        """Test all single-qubit gates from Cirq"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([
            cirq.H(q),
            cirq.X(q),
            cirq.Y(q),
            cirq.Z(q),
            cirq.S(q),
            cirq.T(q),
        ])
        
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        assert qd_circuit.num_qubits == 1
        assert len(qd_circuit.gates) == 6
        gate_names = [g.name for g in qd_circuit.gates]
        assert 'H' in gate_names
        assert 'X' in gate_names
        assert 'Y' in gate_names
        assert 'Z' in gate_names
        assert 'S' in gate_names
        assert 'T' in gate_names
    
    def test_from_cirq_two_qubit_gates(self):
        """Test two-qubit gates from Cirq"""
        q0, q1 = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([
            cirq.CNOT(q0, q1),
            cirq.CZ(q0, q1),
            cirq.SWAP(q0, q1),
        ])
        
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        assert qd_circuit.num_qubits == 2
        assert len(qd_circuit.gates) == 3
    
    def test_from_cirq_three_qubit_gates(self):
        """Test three-qubit gates from Cirq"""
        q0, q1, q2 = cirq.LineQubit.range(3)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append(cirq.CCX(q0, q1, q2))  # Toffoli
        
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        assert qd_circuit.num_qubits == 3
        assert len(qd_circuit.gates) == 1
        assert qd_circuit.gates[0].name == 'TOFFOLI'
    
    def test_from_cirq_rotation_gates(self):
        """Test rotation gates with parameters"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([
            cirq.Rx(rads=np.pi/4)(q),
            cirq.Ry(rads=np.pi/3)(q),
            cirq.Rz(rads=np.pi/2)(q),
        ])
        
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        assert qd_circuit.num_qubits == 1
        assert len(qd_circuit.gates) == 3
        
        # Check gate types
        gate_names = [g.name for g in qd_circuit.gates]
        assert 'RX' in gate_names
        assert 'RY' in gate_names
        assert 'RZ' in gate_names
    
    def test_to_cirq_single_qubit_gates(self):
        """Test all single-qubit gates to Cirq"""
        qd_circuit = QuantumCircuit(1)
        qd_circuit.h(0)
        qd_circuit.x(0)
        qd_circuit.y(0)
        qd_circuit.z(0)
        qd_circuit.s(0)
        qd_circuit.t(0)
        
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        
        ops = list(cirq_circuit.all_operations())
        assert len(ops) == 6
    
    def test_to_cirq_two_qubit_gates(self):
        """Test two-qubit gates to Cirq"""
        qd_circuit = QuantumCircuit(2)
        qd_circuit.cnot(0, 1)
        qd_circuit.cz(0, 1)
        qd_circuit.swap(0, 1)
        
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        
        ops = list(cirq_circuit.all_operations())
        assert len(ops) == 3
    
    def test_to_cirq_toffoli(self):
        """Test Toffoli gate to Cirq"""
        qd_circuit = QuantumCircuit(3)
        qd_circuit.toffoli(0, 1, 2)
        
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        
        ops = list(cirq_circuit.all_operations())
        assert len(ops) == 1
        assert isinstance(ops[0].gate, cirq.CCX.__class__)
    
    def test_to_cirq_rotation_gates(self):
        """Test rotation gates to Cirq"""
        qd_circuit = QuantumCircuit(1)
        qd_circuit.rx(np.pi/4, 0)
        qd_circuit.ry(np.pi/3, 0)
        qd_circuit.rz(np.pi/2, 0)
        
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        
        ops = list(cirq_circuit.all_operations())
        assert len(ops) == 3
    
    def test_roundtrip_conversion(self):
        """Test conversion from Cirq to QD and back"""
        # Create original Cirq circuit
        q0, q1 = cirq.LineQubit.range(2)
        original = cirq.Circuit()
        original.append([
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.X(q1),
        ])
        
        # Convert to QD and back
        qd_circuit = CirqAdapter.from_cirq(original)
        roundtrip = CirqAdapter.to_cirq(qd_circuit)
        
        # Both should have same structure
        assert len(list(original.all_qubits())) == len(list(roundtrip.all_qubits()))
        assert len(list(original.all_operations())) == len(list(roundtrip.all_operations()))
    
    def test_compare_circuits(self):
        """Test circuit comparison functionality"""
        # Create matching circuits
        q0, q1 = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([cirq.H(q0), cirq.CNOT(q0, q1)])
        
        qd_circuit = QuantumCircuit(2)
        qd_circuit.h(0)
        qd_circuit.cnot(0, 1)
        
        comparison = CirqAdapter.compare_circuits(cirq_circuit, qd_circuit)
        
        assert comparison['num_qubits_match'] is True
        assert comparison['num_gates_match'] is True
        assert comparison['cirq_qubits'] == 2
        assert comparison['qd_qubits'] == 2
    
    def test_simulate_cirq(self):
        """Test simulation using Cirq's simulator"""
        qd_circuit = QuantumCircuit(2)
        qd_circuit.h(0)
        qd_circuit.cnot(0, 1)
        
        result = CirqAdapter.simulate_cirq(qd_circuit)
        
        assert 'state_vector' in result
        assert result['state_vector'] is not None
        assert len(result['state_vector']) == 4  # 2^2 qubits
        
        # Bell state should be |00⟩ + |11⟩ (normalized)
        expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
        np.testing.assert_array_almost_equal(np.abs(result['state_vector']), np.abs(expected))
    
    def test_custom_qubits(self):
        """Test conversion with custom Cirq qubits"""
        qd_circuit = QuantumCircuit(2)
        qd_circuit.h(0)
        qd_circuit.cnot(0, 1)
        
        # Use custom qubits
        custom_qubits = [cirq.GridQubit(0, 0), cirq.GridQubit(0, 1)]
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit, qubits=custom_qubits)
        
        assert set(cirq_circuit.all_qubits()) == set(custom_qubits)
    
    def test_grover_algorithm(self):
        """Test more complex circuit - Grover's algorithm"""
        # 2-qubit Grover
        q0, q1 = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        
        # Superposition
        cirq_circuit.append([cirq.H(q0), cirq.H(q1)])
        
        # Oracle
        cirq_circuit.append(cirq.CZ(q0, q1))
        
        # Diffusion
        cirq_circuit.append([cirq.H(q0), cirq.H(q1)])
        cirq_circuit.append([cirq.Z(q0), cirq.Z(q1)])
        cirq_circuit.append(cirq.CZ(q0, q1))
        cirq_circuit.append([cirq.H(q0), cirq.H(q1)])
        
        # Convert
        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        
        assert qd_circuit.num_qubits == 2
        assert len(qd_circuit.gates) == 10
    
    def test_qft_circuit(self):
        """Test Quantum Fourier Transform circuit"""
        # 3-qubit QFT
        qd_circuit = QuantumCircuit(3)
        qd_circuit.h(0)
        qd_circuit.h(1)
        qd_circuit.h(2)
        qd_circuit.swap(0, 2)
        
        cirq_circuit = CirqAdapter.to_cirq(qd_circuit)
        ops = list(cirq_circuit.all_operations())
        
        assert len(ops) == 4
        assert len(list(cirq_circuit.all_qubits())) == 3

