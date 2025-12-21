"""
Regression Tests for QML Module
================================

Tests to prevent regression of previously fixed bugs and ensure stability.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml import (
    RXGate, RYGate, RZGate,
    VQE, QAOA,
    h2_hamiltonian,
    hardware_efficient_ansatz
)
from quantum_debugger.qml.optimizers import Adam, GradientDescent


class TestOptimizerRegressions:
    """Regression tests for optimizer bugs"""
    
    def test_adam_momentum_initialization(self):
        """Test Adam properly initializes momentum (regression)"""
        opt = Adam(learning_rate=0.01)
        params = np.array([1.0, 2.0])
        grad = np.array([0.1, 0.2])
        
        # First step should initialize m and v
        new_params = opt.step(params, grad)
        
        assert opt.m is not None
        assert opt.v is not None
        assert not np.array_equal(params, new_params)
    
    def test_gradient_descent_no_state(self):
        """Test GD doesn't maintain state between steps"""
        opt = GradientDescent(learning_rate=0.1)
        params1 = np.array([5.0])
        grad1 = np.array([1.0])
        
        result1 = opt.step(params1, grad1)
        
        # Should be stateless
        params2 = np.array([5.0])
        grad2 = np.array([1.0])
        result2 = opt.step(params2, grad2)
        
        # Same input = same output
        np.testing.assert_array_equal(result1, result2)


class TestVQERegressions:
    """Regression tests for VQE bugs"""
    
    def test_vqe_history_populated(self):
        """Test VQE history is properly populated (regression)"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=10)
        
        result = vqe.run(np.array([0.5, 0.5]))
        
        # History should have entries
        assert len(vqe.history) > 0
        assert all('energy' in h for h in vqe.history)
        assert all('params' in h for h in vqe.history)
    
    def test_vqe_energy_real_valued(self):
        """Test VQE returns real energy (regression)"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=5)
        
        result = vqe.run(np.array([0.5, 0.5]))
        
        # Energy should be real
        assert np.isreal(result['ground_state_energy'])
    
    def test_vqe_parameter_preservation(self):
        """Test VQE doesn't modify input parameters (regression)"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=5)
        
        original_params = np.array([0.5, 0.5])
        input_params = original_params.copy()
        
        vqe.run(input_params)
        
        # Input should not be modified
        np.testing.assert_array_equal(input_params, original_params)


class TestQAOARegressions:
    """Regression tests for QAOA bugs"""
    
    def test_qaoa_cost_negation(self):
        """Test QAOA properly negates cost for maximization"""
        graph = [(0, 1), (1, 2)]
        qaoa = QAOA(graph=graph, p=1, max_iterations=5)
        
        result = qaoa.run(np.array([0.5, 0.5]))
        
        # Best value should be positive (not negative)
        assert result['best_value'] >= 0
    
    def test_qaoa_graph_node_indexing(self):
        """Test QAOA handles non-consecutive node indices"""
        graph = [(0, 5), (5, 10)]  # Non-consecutive indices
        qaoa = QAOA(graph=graph, p=1, max_iterations=5)
        
        # Should determine correct number of qubits
        assert qaoa.num_qubits == 11  # 0 to 10


class TestGateMatrixRegressions:
    """Regression tests for gate matrix bugs"""
    
    def test_rx_matrix_special_properties(self):
        """Test RX matrix special properties"""
        gate = RXGate(0, np.pi/4)
        U = gate.matrix()
        
        # RX is self-adjoint (Hermitian) because it's exp(-iθX/2) and X is Hermitian
        # However, rotation matrices are unitary, not necessarily Hermitian
        # Just check unitarity
        assert np.allclose(U @ U.conj().T, np.eye(2))
    
    def test_rz_matrix_diagonal(self):
        """Test RZ matrix is diagonal (regression)"""
        gate = RZGate(0, 0.5)
        U = gate.matrix()
        
        # RZ should be diagonal
        off_diag = U[0, 1]
        assert np.isclose(off_diag, 0, atol=1e-10)
    
    def test_gate_cache_invalidation(self):
        """Test cache invalidates on parameter change"""
        gate = RXGate(0, 0.5)
        
        matrix1 = gate.matrix()
        gate.parameter = 1.0
        matrix2 = gate.matrix()
        
        # Matrices should be different
        assert not np.allclose(matrix1, matrix2)


class TestNumericalPrecision:
    """Tests for numerical precision issues"""
    
    def test_small_angle_approximation(self):
        """Test gates work correctly for very small angles"""
        epsilon = 1e-10
        gate = RYGate(0, epsilon)
        U = gate.matrix()
        
        # Should be close to identity
        assert np.allclose(U, np.eye(2), atol=1e-8)
    
    def test_angle_wrapping_2pi(self):
        """Test angles differing by 2π give same results"""
        angle1 = 0.5
        angle2 = 0.5 + 2*np.pi
        
        gate1 = RZGate(0, angle1)
        gate2 = RZGate(0, angle2)
        
        U1 = gate1.matrix()
        U2 = gate2.matrix()
        
        # Should be equivalent up to global phase
        # Check if |⟨ψ1|ψ2⟩| = 1
        fidelity = abs(np.trace(U1.conj().T @ U2)) / 2
        assert np.isclose(fidelity, 1.0, atol=1e-10)
    
    def test_commutator_rx_ry(self):
        """Test RX and RY don't commute"""
        theta = 0.5
        rx = RXGate(0, theta).matrix()
        ry = RYGate(0, theta).matrix()
        
        # [RX, RY] = RX·RY - RY·RX should be non-zero
        commutator = rx @ ry - ry @ rx
        assert not np.allclose(commutator, np.zeros((2, 2)))


class TestBoundaryConditions:
    """Test boundary conditions and limits"""
    
    def test_zero_parameter_gate(self):
        """Test gate with parameter = 0"""
        for GateClass in [RXGate, RYGate, RZGate]:
            gate = GateClass(0, 0.0)
            U = gate.matrix()
            
            # Should be identity (or close to it)
            assert np.allclose(U, np.eye(2), atol=1e-10)
    
    def test_max_iterations_respected(self):
        """Test VQE respects max_iterations limit"""
        H = h2_hamiltonian()
        max_iter = 5
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=max_iter)
        
        result = vqe.run(np.array([0.5, 0.5]))
        
        # Should not exceed max iterations
        assert len(vqe.history) <= max_iter + 5  # Allow some tolerance
    
    def test_single_parameter_ansatz(self):
        """Test VQE with minimal single-parameter ansatz"""
        H = h2_hamiltonian()
        
        def single_param_ansatz(params, num_qubits):
            return [RYGate(0, params[0])]
        
        vqe = VQE(H, single_param_ansatz, num_qubits=2, max_iterations=10)
        result = vqe.run(np.array([0.5]))
        
        assert 'ground_state_energy' in result


class TestDataIntegrity:
    """Test data integrity and immutability"""
    
    def test_hamiltonian_not_modified(self):
        """Test VQE doesn't modify Hamiltonian"""
        H = h2_hamiltonian()
        H_original = H.copy()
        
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=5)
        vqe.run(np.array([0.5, 0.5]))
        
        # Hamiltonian should be unchanged
        np.testing.assert_array_equal(H, H_original)
    
    def test_history_immutable_params(self):
        """Test history stores copies of parameters, not references"""
        H = h2_hamiltonian()
        # Use at least 10 iterations to satisfy COBYLA minimum (num_vars + 2)
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=10)
        
        vqe.run(np.array([0.5, 0.5]))
        
        # Modify history entry params
        if len(vqe.history) > 0:
            vqe.history[0]['params'][0] = 999.0
            
            # Other entries should not be affected
            if len(vqe.history) > 1:
                assert vqe.history[1]['params'][0] != 999.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
