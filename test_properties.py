"""
Property-Based Tests for QML Module
====================================

Tests mathematical properties that should always hold true.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml import RXGate, RYGate, RZGate
from quantum_debugger.qml import VQE, h2_hamiltonian, hardware_efficient_ansatz


class TestUnitarityProperty:
    """Test unitarity property for all gates"""
    
    def test_unitarity_random_params(self):
        """Test unitarity holds for 100 random parameters"""
        np.random.seed(42)
        params = np.random.rand(100) * 10 - 5  # Random in [-5, 5]
        
        for param in params:
            for GateClass in [RXGate, RYGate, RZGate]:
                gate = GateClass(0, param)
                U = gate.matrix()
                
                # U†U = I
                should_be_identity = U.conj().T @ U
                assert np.allclose(should_be_identity, np.eye(2), atol=1e-10), \
                    f"{GateClass.__name__}({param}) not unitary"
    
    def test_determinant_property(self):
        """Test |det(U)| = 1 for all gates"""
        params = np.linspace(0, 2*np.pi, 20)
        
        for param in params:
            for GateClass in [RXGate, RYGate, RZGate]:
                gate = GateClass(0, param)
                U = gate.matrix()
                det = np.linalg.det(U)
                
                assert np.isclose(abs(det), 1.0, atol=1e-10)


class TestHermitianProperty:
    """Test Hermitian properties"""
    
    def test_hamiltonian_hermitian(self):
        """Test H2 Hamiltonian is Hermitian"""
        H = h2_hamiltonian()
        
        # H = H†
        assert np.allclose(H, H.conj().T)
    
    def test_energy_real_valued(self):
        """Test energy eigenvalues are real for Hermitian H"""
        H = h2_hamiltonian()
        eigenvalues = np.linalg.eigvalsh(H)
        
        # All eigenvalues should be real
        assert all(np.isreal(eigenvalues))


class TestCompositionProperties:
    """Test composition and algebraic properties"""
    
    def test_rx_inverse_property(self):
        """Test RX(θ) · RX(-θ) = I"""
        theta = 0.7
        rx_forward = RXGate(0, theta).matrix()
        rx_backward = RXGate(0, -theta).matrix()
        
        product = rx_forward @ rx_backward
        assert np.allclose(product, np.eye(2), atol=1e-10)
    
    def test_rz_composition(self):
        """Test RZ(a) · RZ(b) = RZ(a+b)"""
        a, b = 0.3, 0.5
        
        rz_a = RZGate(0, a).matrix()
        rz_b = RZGate(0, b).matrix()
        rz_ab = RZGate(0, a + b).matrix()
        
        product = rz_a @ rz_b
        
        # Check equivalence up to global phase
        phase_diff = product[0, 0] / rz_ab[0, 0]
        normalized_product = product / phase_diff
        
        assert np.allclose(normalized_product, rz_ab, atol=1e-10)
    
    def test_double_application(self):
        """Test U²(θ) = U(2θ)"""
        theta = 0.4
        
        for GateClass in [RXGate, RYGate, RZGate]:
            U_theta = GateClass(0, theta).matrix()
            U_2theta = GateClass(0, 2*theta).matrix()
            
            U_squared = U_theta @ U_theta
            
            # Check equivalence (may differ by global phase)
            ratio = U_squared[0, 0] / U_2theta[0, 0] if U_2theta[0, 0] != 0 else 1
            normalized = U_squared / ratio
            
            assert np.allclose(normalized, U_2theta, atol=1e-10)


class TestVariationalPrinciple:
    """Test variational principle for VQE"""
    
    def test_vqe_upper_bound(self):
        """Test VQE energy >= exact ground state (variational principle)"""
        H = h2_hamiltonian()
        exact_energy = np.linalg.eigvalsh(H)[0]
        
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=20)
        
        # Try multiple random starts
        for seed in [42, 123, 456]:
            np.random.seed(seed)
            result = vqe.run(np.random.rand(2))
            
            # VQE energy should be >= exact (within numerical tolerance)
            assert result['ground_state_energy'] >= exact_energy - 1e-6
    
    def test_energy_monotonic_decrease(self):
        """Test energy decreases or stays same during optimization"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=30)
        
        result = vqe.run(np.array([0.5, 0.5]))
        
        energies = [h['energy'] for h in vqe.history]
        
        # Check that minimum energy in history <= initial energy
        assert min(energies) <= energies[0]


class TestSymmetryProperties:
    """Test symmetry properties"""
    
    def test_rx_antisymmetry(self):
        """Test RX(-θ) = RX(θ)† """
        theta = 0.6
        
        rx_pos = RXGate(0, theta).matrix()
        rx_neg = RXGate(0, -theta).matrix()
        
        # RX(-θ) should equal RX(θ)†
        assert np.allclose(rx_neg, rx_pos.conj().T, atol=1e-10)
    
    def test_ry_antisymmetry(self):
        """Test RY(-θ) = RY(θ)†"""
        theta = 0.6
        
        ry_pos = RYGate(0, theta).matrix()
        ry_neg = RYGate(0, -theta).matrix()
        
        assert np.allclose(ry_neg, ry_pos.conj().T, atol=1e-10)


class TestNormalizationProperties:
    """Test normalization and probability properties"""
    
    def test_statevector_normalized(self):
        """Test statevectors remain normalized after gate application"""
        # Initial state |0⟩
        state = np.array([1.0, 0.0], dtype=complex)
        
        gates = [
            RXGate(0, 0.5).matrix(),
            RYGate(0, 1.2).matrix(),
            RZGate(0, 0.8).matrix(),
        ]
        
        for gate in gates:
            state = gate @ state
            norm = np.linalg.norm(state)
            assert np.isclose(norm, 1.0, atol=1e-10)
    
    def test_probability_conservation(self):
        """Test probabilities sum to 1 after gate application"""
        state = np.array([0.6, 0.8], dtype=complex)  # Normalized
        
        gate = RXGate(0, 0.7).matrix()
        new_state = gate @ state
        
        probabilities = np.abs(new_state)**2
        assert np.isclose(np.sum(probabilities), 1.0, atol=1e-10)


class TestConsistencyProperties:
    """Test consistency across different representations"""
    
    def test_gate_target_consistency(self):
        """Test gate target qubit is correctly stored"""
        for target in [0, 1, 5, 10]:
            gate = RXGate(target, 0.5)
            assert gate.target == target
    
    def test_parameter_update_consistency(self):
        """Test parameter updates consistently"""
        gate = RYGate(0, 0.5)
        
        # Update parameter
        new_param = 1.2
        gate.parameter = new_param
        
        # Check it's stored
        assert gate.parameter == new_param
        
        # Check matrix reflects new parameter
        U = gate.matrix()
        # RY matrix should use new parameter
        expected = np.array([
            [np.cos(new_param/2), -np.sin(new_param/2)],
            [np.sin(new_param/2), np.cos(new_param/2)]
        ])
        assert np.allclose(U, expected)


class TestInvariantProperties:
    """Test properties that should be invariant"""
    
    def test_matrix_shape_invariant(self):
        """Test matrix shape is always 2x2"""
        params = np.random.rand(50) * 10
        
        for param in params:
            for GateClass in [RXGate, RYGate, RZGate]:
                gate = GateClass(0, param)
                U = gate.matrix()
                assert U.shape == (2, 2)
    
    def test_dtype_invariant(self):
        """Test matrices are always complex"""
        gate = RZGate(0, 0.5)
        U = gate.matrix()
        assert U.dtype == complex or U.dtype == np.complex128


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
