"""
Comprehensive Tests for Parameterized Quantum Gates
====================================================

Tests for RX, RY, RZ gates with extensive coverage for debugging.
"""

import pytest
import numpy as np
from quantum_debugger.qml import RXGate, RYGate, RZGate, ParameterizedGate


class TestParameterizedGateBase:
    """Test base ParameterizedGate class"""
    
    def test_initialization(self):
        """Test basic gate initialization"""
        gate = ParameterizedGate(target=0, parameter=np.pi/4, trainable=True)
        assert gate.target == 0
        assert np.isclose(gate.parameter, np.pi/4)
        assert gate.trainable == True
        assert gate.gradient is None
    
    def test_negative_target_raises_error(self):
        """Test that negative target qubit raises ValueError"""
        with pytest.raises(ValueError, match="non-negative"):
            ParameterizedGate(target=-1, parameter=0.0)
    
    def test_matrix_not_implemented(self):
        """Test that base class matrix() raises NotImplementedError"""
        gate = ParameterizedGate(target=0)
        with pytest.raises(NotImplementedError):
            gate.matrix()
    
    def test_repr(self):
        """Test string representation"""
        gate = ParameterizedGate(target=2, parameter=1.5, trainable=False, name="Test")
        repr_str = repr(gate)
        assert "Test" in repr_str
        assert "target=2" in repr_str
        assert "1.5" in repr_str


class TestRXGate:
    """Test RX (rotation around X-axis) gate"""
    
    def test_initialization(self):
        """Test RX gate initialization"""
        rx = RXGate(target=1, parameter=np.pi/2)
        assert rx.target == 1
        assert np.isclose(rx.parameter, np.pi/2)
        assert rx.name == "RX"
    
    def test_matrix_shape(self):
        """Test matrix has correct shape"""
        rx = RXGate(target=0, parameter=0.5)
        matrix = rx.matrix()
        assert matrix.shape == (2, 2)
        assert matrix.dtype == complex
    
    def test_matrix_is_unitary(self):
        """Test that RX matrix is unitary: U†U = I"""
        rx = RXGate(target=0, parameter=np.pi/3)
        U = rx.matrix()
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-10)
    
    def test_zero_parameter(self):
        """Test RX(0) = Identity"""
        rx = RXGate(target=0, parameter=0.0)
        U = rx.matrix()
        np.testing.assert_allclose(U, np.eye(2), atol=1e-10)
    
    def test_pi_parameter(self):
        """Test RX(π) = -iX (Pauli-X with phase)"""
        rx = RXGate(target=0, parameter=np.pi)
        U = rx.matrix()
        X = np.array([[0, 1], [1, 0]])
        # RX(π) = -iX
        expected = -1j * X
        np.testing.assert_allclose(U, expected, atol=1e-10)
    
    def test_half_pi_parameter(self):
        """Test RX(π/2)"""
        rx = RXGate(target=0, parameter=np.pi/2)
        U = rx.matrix()
        expected = (1/np.sqrt(2)) * np.array([
            [1, -1j],
            [-1j, 1]
        ])
        np.testing.assert_allclose(U, expected, atol=1e-10)
    
    def test_parameter_update(self):
        """Test updating parameter changes matrix"""
        rx = RXGate(target=0, parameter=0.0)
        U1 = rx.matrix()
        
        rx.parameter = np.pi
        U2 = rx.matrix()
        
        # Matrices should be different
        assert not np.allclose(U1, U2)
    
    def test_determinant(self):
        """Test determinant is 1 (or -1 with phase)"""
        for theta in [0, np.pi/4, np.pi/2, np.pi, 2*np.pi]:
            rx = RXGate(target=0, parameter=theta)
            det = np.linalg.det(rx.matrix())
            assert np.isclose(np.abs(det), 1.0, atol=1e-10)
    
    def test_eigenvalues(self):
        """Test eigenvalues have magnitude 1"""
        rx = RXGate(target=0, parameter=np.pi/3)
        eigenvalues = np.linalg.eigvals(rx.matrix())
        for ev in eigenvalues:
            assert np.isclose(np.abs(ev), 1.0, atol=1e-10)


class TestRYGate:
    """Test RY (rotation around Y-axis) gate"""
    
    def test_initialization(self):
        """Test RY gate initialization"""
        ry = RYGate(target=2, parameter=1.5)
        assert ry.target == 2
        assert np.isclose(ry.parameter, 1.5)
        assert ry.name == "RY"
    
    def test_matrix_is_unitary(self):
        """Test that RY matrix is unitary"""
        ry = RYGate(target=0, parameter=np.pi/4)
        U = ry.matrix()
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-10)
    
    def test_zero_parameter(self):
        """Test RY(0) = Identity"""
        ry = RYGate(target=0, parameter=0.0)
        U = ry.matrix()
        np.testing.assert_allclose(U, np.eye(2), atol=1e-10)
    
    def test_pi_parameter(self):
        """Test RY(π) = -iY (Pauli-Y with phase factor)"""
        ry = RYGate(target=0, parameter=np.pi)
        U = ry.matrix()
        Y = np.array([[0, -1j], [1j, 0]])
        # RY(π) should flip the state
        expected = np.array([[0, -1], [1, 0]])
        np.testing.assert_allclose(U, expected, atol=1e-10)
    
    def test_matrix_is_real(self):
        """Test RY matrix has real entries (no imaginary part)"""
        ry = RYGate(target=0, parameter=np.pi/6)
        U = ry.matrix()
        # All imaginary parts should be essentially zero
        assert np.allclose(U.imag, 0, atol=1e-10)
    
    def test_half_pi(self):
        """Test RY(π/2)"""
        ry = RYGate(target=0, parameter=np.pi/2)
        U = ry.matrix()
        expected = (1/np.sqrt(2)) * np.array([
            [1, -1],
            [1, 1]
        ])
        np.testing.assert_allclose(U, expected, atol=1e-10)


class TestRZGate:
    """Test RZ (rotation around Z-axis) gate"""
    
    def test_initialization(self):
        """Test RZ gate initialization"""
        rz = RZGate(target=0, parameter=np.pi/4)
        assert rz.target == 0
        assert np.isclose(rz.parameter, np.pi/4)
        assert rz.name == "RZ"
    
    def test_matrix_is_unitary(self):
        """Test that RZ matrix is unitary"""
        rz = RZGate(target=0, parameter=np.pi/3)
        U = rz.matrix()
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-10)
    
    def test_matrix_is_diagonal(self):
        """Test RZ matrix is diagonal"""
        rz = RZGate(target=0, parameter=1.2)
        U = rz.matrix()
        # Off-diagonal elements should be zero
        assert np.isclose(U[0, 1], 0, atol=1e-10)
        assert np.isclose(U[1, 0], 0, atol=1e-10)
    
    def test_zero_parameter(self):
        """Test RZ(0) = Identity (up to global phase)"""
        rz = RZGate(target=0, parameter=0.0)
        U = rz.matrix()
        # RZ(0) = diag(1, 1) = I
        np.testing.assert_allclose(U, np.eye(2), atol=1e-10)
    
    def test_pi_parameter(self):
        """Test RZ(π) = -iZ (Pauli-Z with phase)"""
        rz = RZGate(target=0, parameter=np.pi)
        U = rz.matrix()
        # RZ(π) = diag(e^(-iπ/2), e^(iπ/2)) = diag(-i, i) = -iZ
        expected = np.array([[-1j, 0], [0, 1j]])
        np.testing.assert_allclose(U, expected, atol=1e-10)
    
    def test_s_gate(self):
        """Test RZ(π/2) = S gate"""
        rz = RZGate(target=0, parameter=np.pi/2)
        U = rz.matrix()
        S = np.array([[np.exp(-1j*np.pi/4), 0], 
                      [0, np.exp(1j*np.pi/4)]])
        np.testing.assert_allclose(U, S, atol=1e-10)
    
    def test_t_gate(self):
        """Test RZ(π/4) = T gate"""
        rz = RZGate(target=0, parameter=np.pi/4)
        U = rz.matrix()
        T = np.array([[np.exp(-1j*np.pi/8), 0], 
                      [0, np.exp(1j*np.pi/8)]])
        np.testing.assert_allclose(U, T, atol=1e-10)


class TestGateCompositions:
    """Test compositions and relationships between gates"""
    
    def test_rx_ry_commutation(self):
        """Test that RX and RY don't commute (in general)"""
        theta = np.pi/4
        rx = RXGate(target=0, parameter=theta)
        ry = RYGate(target=0, parameter=theta)
        
        # RX·RY
        composition1 = rx.matrix() @ ry.matrix()
        # RY·RX
        composition2 = ry.matrix() @ rx.matrix()
        
        # Should not be equal (except for special angles)
        assert not np.allclose(composition1, composition2, atol=1e-10)
    
    def test_rz_commutes_with_z(self):
        """Test RZ commutes with Pauli-Z"""
        rz = RZGate(target=0, parameter=np.pi/3)
        Z = np.array([[1, 0], [0, -1]])
        
        # RZ·Z
        comp1 = rz.matrix() @ Z
        # Z·RZ
        comp2 = Z @ rz.matrix()
        
        # Should commute
        np.testing.assert_allclose(comp1, comp2, atol=1e-10)
    
    def test_two_pi_rotation(self):
        """Test that RX(2π) = -I (full rotation with phase)"""
        rx = RXGate(target=0, parameter=2*np.pi)
        U = rx.matrix()
        np.testing.assert_allclose(U, -np.eye(2), atol=1e-10)
    
    def test_inverse_rotation(self):
        """Test RX(θ)·RX(-θ) = I"""
        theta = np.pi/3
        rx_pos = RXGate(target=0, parameter=theta)
        rx_neg = RXGate(target=0, parameter=-theta)
        
        product = rx_pos.matrix() @ rx_neg.matrix()
        np.testing.assert_allclose(product, np.eye(2), atol=1e-10)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.parametrize("theta", [0, 1e-10, -1e-10, 1e10, -1e10])
    def test_extreme_parameters(self, theta):
        """Test gates with extreme parameter values"""
        rx = RXGate(target=0, parameter=theta)
        U = rx.matrix()
        
        # Should still be unitary
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-8)
    
    def test_large_qubit_index(self):
        """Test with large qubit indices"""
        gate = RXGate(target=1000, parameter=np.pi/4)
        assert gate.target == 1000
    
    def test_trainable_flag(self):
        """Test trainable flag persistence"""
        gate = RXGate(target=0, parameter=0.5, trainable=False)
        assert gate.trainable == False
        
        gate.trainable = True
        assert gate.trainable == True
    
    def test_gradient_storage(self):
        """Test gradient can be stored"""
        gate = RXGate(target=0, parameter=0.5)
        assert gate.gradient is None
        
        gate.gradient = 0.123
        assert np.isclose(gate.gradient, 0.123)


class TestMatrixProperties:
    """Test mathematical properties of gate matrices"""
    
    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    @pytest.mark.parametrize("theta", [0, np.pi/6, np.pi/4, np.pi/2, np.pi])
    def test_norm_preservation(self, GateClass, theta):
        """Test that gates preserve state vector norm"""
        gate = GateClass(target=0, parameter=theta)
        U = gate.matrix()
        
        # Test on |0⟩ and |1⟩ basis states
        for state in [np.array([1, 0]), np.array([0, 1])]:
            new_state = U @ state
            original_norm = np.linalg.norm(state)
            new_norm = np.linalg.norm(new_state)
            assert np.isclose(original_norm, new_norm, atol=1e-10)
    
    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    def test_hermiticity_of_generator(self, GateClass):
        """Test that generator of rotation is Hermitian"""
        # Use very small angle for accurate first-order approximation
        theta = 1e-6
        gate = GateClass(target=0, parameter=theta)
        U = gate.matrix()
        
        # For small θ: U ≈ I - iθG where G is Hermitian generator
        # So G ≈ i(I-U)/θ
        G = 1j * (np.eye(2) - U) / theta
        
        # G should be approximately Hermitian (use looser tolerance for numerical errors)
        assert np.allclose(G, G.conj().T, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
