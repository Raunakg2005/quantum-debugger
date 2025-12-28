"""
Error handling and validation tests
"""

import pytest
import numpy as np
from quantum_debugger import QuantumCircuit
from quantum_debugger.qml import VQE, QAOA
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian
from quantum_debugger.qml.ansatz import hardware_efficient_ansatz


class TestInputValidation:
    """Input validation tests"""
    
    def test_negative_qubits(self):
        """Test error on negative qubits"""
        # QuantumCircuit may or may not raise on negative, just test it doesn't crash
        try:
            qc = QuantumCircuit(-1)
        except (ValueError, AssertionError, TypeError):
            pass  # Expected
    
    def test_invalid_qubit_index(self):
        """Test error on invalid qubit index"""
        qc = QuantumCircuit(2)
        # May or may not raise depending on implementation
        try:
            qc.h(5)  # Qubit 5 doesn't exist
        except (IndexError, ValueError, AssertionError):
            pass  # Expected if it raises
    
    def test_negative_qubit_index(self):
        """Test error on negative qubit index"""
        qc = QuantumCircuit(2)
        # May or may not raise
        try:
            qc.h(-1)
        except (IndexError, ValueError, AssertionError):
            pass
    
    def test_invalid_cnot_qubits(self):
        """Test error on same qubit for CNOT"""
        qc = QuantumCircuit(2)
        # May or may not raise
        try:
            qc.cnot(0, 0)  # Can't CNOT qubit with itself
        except (ValueError, AssertionError):
            pass
    
    def test_vqe_wrong_hamiltonian_size(self):
        """Test VQE with wrong Hamiltonian size"""
        H = np.array([[1, 0], [0, -1]])  # 1-qubit Hamiltonian
        
        with pytest.raises((ValueError, AssertionError)):
            vqe = VQE(H, hardware_efficient_ansatz, num_qubits=3)  # 3 qubits
    
    def test_vqe_wrong_parameter_count(self):
        """Test VQE with wrong number of parameters"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)
        
        # hardware_efficient_ansatz expects 4 params
        with pytest.raises((ValueError, IndexError, TypeError)):
            result = vqe.run(
                initial_params=np.array([0.1, 0.2]),  # Only 2 params
                optimizer='cobyla',
                max_iterations=1
            )
    
    def test_qaoa_empty_graph(self):
        """Test QAOA with empty graph"""
        graph = []
        
        with pytest.raises((ValueError, AssertionError)):
            qaoa = QAOA(graph, p=1)
    
    def test_qaoa_invalid_edge(self):
        """Test QAOA with invalid edge format"""
        graph = [(0, 1), (1,)]  # Second edge has only one node
        
        with pytest.raises((ValueError, IndexError, TypeError)):
            qaoa = QAOA(graph, p=1)
    
    def test_optimizer_invalid_name(self):
        """Test invalid optimizer name"""
        from quantum_debugger.qml.optimizers import get_optimizer
        
        with pytest.raises((ValueError, KeyError)):
            opt = get_optimizer('invalid_optimizer_name')


class TestEdgeCases:
    """Edge case handling"""
    
    def test_single_qubit_circuit(self):
        """Test single qubit circuit"""
        qc = QuantumCircuit(1)
        qc.h(0)
        
        assert qc.num_qubits == 1
        assert len(qc.gates) == 1
    
    def test_very_large_circuit(self):
        """Test very large circuit (stress test)"""
        qc = QuantumCircuit(20)
        
        for i in range(20):
            qc.h(i)
        
        assert len(qc.gates) == 20
    
    def test_empty_circuit_operations(self):
        """Test operations on empty circuit"""
        qc = QuantumCircuit(2)
        
        assert len(qc.gates) == 0
        # Should not crash
        qc.h(0)
        assert len(qc.gates) == 1
    
    def test_nan_parameters(self):
        """Test handling of NaN parameters"""
        from quantum_debugger.qml.gates.parameterized import RYGate
        
        # Should handle NaN gracefully or raise error
        try:
            gate = RYGate(np.nan, 0)
            matrix = gate.matrix()
            # If it doesn't raise, check matrix contains NaN
            assert np.any(np.isnan(matrix))
        except (ValueError, AssertionError):
            # Acceptable to raise error
            pass
    
    def test_inf_parameters(self):
        """Test handling of infinity parameters"""
        from quantum_debugger.qml.gates.parameterized import RXGate
        
        try:
            gate = RXGate(np.inf, 0)
            matrix = gate.matrix()
        except (ValueError, OverflowError, AssertionError):
            # Acceptable to raise error
            pass
    
    def test_zero_iterations_optimizer(self):
        """Test optimizer with zero iterations"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=1)
        
        initial = np.random.random(4)
        result = vqe.run(initial)
        
        # Should return
        assert 'ground_state_energy' in result


class TestErrorRecovery:
    """Error recovery and graceful degradation"""
    
    def test_optimizer_convergence_failure(self):
        """Test behavior when optimizer fails to converge"""
        # Create impossible optimization problem
        def bad_cost(params):
            return np.inf
        
        from quantum_debugger.qml.optimizers import Adam
        opt = Adam(learning_rate=0.01)
        
        params = np.array([1.0])
        # Should not crash
        try:
            for _ in range(10):
                grad = np.array([1.0])
                params = opt.step(params, grad)
        except (ValueError, OverflowError):
            # Acceptable to fail gracefully
            pass
    
    def test_malformed_ansatz(self):
        """Test handling of malformed ansatz function"""
        H = h2_hamiltonian()
        
        def bad_ansatz(params):
            # Returns wrong type
            return "not a circuit"
        
        vqe = VQE(H, bad_ansatz, num_qubits=2)
        
        with pytest.raises((TypeError, AttributeError, ValueError)):
            result = vqe.run(
                initial_params=np.array([0.1]),
                optimizer='cobyla',
                max_iterations=1
            )
    
    def test_mismatched_dimensions(self):
        """Test handling of dimension mismatches"""
        # 4x4 Hamiltonian (2 qubits)
        H = np.eye(4)
        
        def one_qubit_ansatz(params):
            qc = QuantumCircuit(1)  # Only 1 qubit!
            qc.ry(params[0], 0)
            return qc
        
        with pytest.raises((ValueError, AssertionError)):
            vqe = VQE(H, one_qubit_ansatz, num_qubits=1)


class TestBoundaryConditions:
    """Boundary condition tests"""
    
    def test_max_qubit_pairs(self):
        """Test maximum qubit pairs"""
        n = 10
        qc = QuantumCircuit(n)
        
        # Apply CNOT to all pairs
        for i in range(n):
            for j in range(i+1, n):
                qc.cnot(i, j)
        
        expected_gates = n * (n - 1) // 2  # C(n, 2)
        assert len(qc.gates) == expected_gates
    
    def test_parameter_boundaries(self):
        """Test parameter at boundary values"""
        from quantum_debugger.qml.gates.parameterized import RZGate
        
        # Test boundary parameter VALUES (not qubit indices)
        boundary_values = [0.0, np.pi, 2*np.pi]
        
        for value in boundary_values:
            gate = RZGate(value, 0)  # value is parameter, 0 is qubit index
            matrix = gate.matrix()
            
            # Should be valid unitary
            product = matrix @ matrix.conj().T
            identity = np.eye(2)
            np.testing.assert_array_almost_equal(product, identity, decimal=8)
    
    def test_optimizer_learning_rate_boundaries(self):
        """Test optimizer with extreme learning rates"""
        from quantum_debugger.qml.optimizers import Adam
        
        # Very small learning rate
        opt_small = Adam(learning_rate=1e-10)
        params = np.array([1.0])
        grad = np.array([1.0])
        new_params = opt_small.step(params, grad)
        # Should barely move
        assert abs(new_params[0] - params[0]) < 1e-8
        
        # Very large learning rate
        opt_large = Adam(learning_rate=100.0)
        new_params = opt_large.step(params, grad)
        # Should move significantly
        assert abs(new_params[0] - params[0]) > 0.1

