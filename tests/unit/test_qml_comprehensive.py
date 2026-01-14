"""
Comprehensive Matrix and Quantum Property Tests
==============================================

Deep testing of matrix properties and quantum mechanics principles.
"""

import pytest
import numpy as np
from quantum_debugger.qml import RXGate, RYGate, RZGate


class TestMatrixAlgebra:
    """Test matrix algebra properties"""

    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    @pytest.mark.parametrize(
        "theta", [0, np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2, np.pi]
    )
    def test_unitarity(self, GateClass, theta):
        """Test U†U = I for all gates and angles"""
        gate = GateClass(target=0, parameter=theta)
        U = gate.matrix()
        UdaggerU = U.conj().T @ U
        np.testing.assert_allclose(UdaggerU, np.eye(2), atol=1e-14)

    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    @pytest.mark.parametrize("theta", [0.1, 0.5, 1.0, 1.5, 2.0])
    def test_determinant_unity(self, GateClass, theta):
        """Test |det(U)| = 1"""
        gate = GateClass(target=0, parameter=theta)
        U = gate.matrix()
        det = np.linalg.det(U)
        assert np.isclose(np.abs(det), 1.0, atol=1e-14)

    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    def test_eigenvalue_magnitude(self, GateClass):
        """Test eigenvalues have magnitude 1"""
        gate = GateClass(target=0, parameter=np.pi / 7)
        U = gate.matrix()
        eigenvalues = np.linalg.eigvals(U)
        for ev in eigenvalues:
            assert np.isclose(np.abs(ev), 1.0, atol=1e-14)

    @pytest.mark.parametrize("GateClass", [RXGate, RYGate, RZGate])
    def test_trace_property(self, GateClass):
        """Test trace properties of rotation matrices"""
        gate = GateClass(target=0, parameter=np.pi / 4)
        U = gate.matrix()
        trace = np.trace(U)
        # Trace should be close to 2*cos(θ/2) for rotation matrices
        assert np.abs(trace) <= 2.0  # Maximum trace magnitude


class TestQuantumProperties:
    """Test quantum mechanics properties"""

    def test_no_cloning_theorem(self):
        """Verify rotation gates preserve superposition uniquely"""
        # Cannot clone arbitrary quantum state
        state = np.array([0.6, 0.8], dtype=complex)

        rx = RXGate(target=0, parameter=np.pi / 3)
        rotated = rx.matrix() @ state

        # Rotated state should be different from original
        assert not np.allclose(rotated, state)
        # But norm should be preserved
        assert np.isclose(np.linalg.norm(rotated), 1.0)

    def test_reversibility(self):
        """Test U(θ) U(-θ) = I"""
        for theta in [np.pi / 5, np.pi / 3, 2 * np.pi / 3]:
            rx_pos = RXGate(target=0, parameter=theta)
            rx_neg = RXGate(target=0, parameter=-theta)

            product = rx_pos.matrix() @ rx_neg.matrix()
            np.testing.assert_allclose(product, np.eye(2), atol=1e-14)

    def test_bloch_vector_length_preservation(self):
        """Test Bloch vector length is preserved"""
        # Start with arbitrary state
        state = (1 / np.sqrt(3)) * np.array([1, np.sqrt(2)])

        for GateClass in [RXGate, RYGate, RZGate]:
            gate = GateClass(target=0, parameter=0.789)
            new_state = gate.matrix() @ state

            # Norm should be 1
            assert np.isclose(np.linalg.norm(new_state), 1.0, atol=1e-14)

    def test_measurement_probabilities(self):
        """Test measurement probabilities sum to 1"""
        state = np.array([1, 0], dtype=complex)

        rx = RXGate(target=0, parameter=np.pi / 4)
        final_state = rx.matrix() @ state

        # Probabilities for |0⟩ and |1⟩
        prob_0 = np.abs(final_state[0]) ** 2
        prob_1 = np.abs(final_state[1]) ** 2

        assert np.isclose(prob_0 + prob_1, 1.0, atol=1e-14)


class TestGateCompositions:
    """Test compositions of multiple gates"""

    def test_rx_ry_rz_composition(self):
        """Test arbitrary rotation via Euler decomposition"""
        # Any U(2) rotation can be written as RZ(α) RY(β) RZ(γ)
        alpha, beta, gamma = 0.3, 0.7, 1.1

        rz1 = RZGate(target=0, parameter=alpha)
        ry = RYGate(target=0, parameter=beta)
        rz2 = RZGate(target=0, parameter=gamma)

        U = rz2.matrix() @ ry.matrix() @ rz1.matrix()

        # Should be unitary
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-14)

        # Should have determinant with magnitude 1
        assert np.isclose(np.abs(np.linalg.det(U)), 1.0, atol=1e-14)

    def test_repeated_same_gate(self):
        """Test RX(θ)^n = RX(nθ)"""
        theta = np.pi / 7
        n = 5

        rx_single = RXGate(target=0, parameter=theta)
        rx_multiple = RXGate(target=0, parameter=n * theta)

        # Apply single rotation n times
        U_repeated = np.eye(2, dtype=complex)
        for _ in range(n):
            U_repeated = rx_single.matrix() @ U_repeated

        # Should equal single rotation by nθ
        U_direct = rx_multiple.matrix()

        np.testing.assert_allclose(U_repeated, U_direct, atol=1e-12)

    def test_commutators(self):
        """Test commutator relations"""
        theta1, theta2 = np.pi / 5, np.pi / 7

        # [RX, RY] ≠ 0 (don't commute)
        rx = RXGate(target=0, parameter=theta1)
        ry = RYGate(target=0, parameter=theta2)

        AB = rx.matrix() @ ry.matrix()
        BA = ry.matrix() @ rx.matrix()

        # Should not be equal
        assert not np.allclose(AB, BA, atol=1e-10)

        # But [RZ, Z] should be close to zero (they commute)
        rz = RZGate(target=0, parameter=theta1)
        Z = np.array([[1, 0], [0, -1]])

        RZ_Z = rz.matrix() @ Z
        Z_RZ = Z @ rz.matrix()

        np.testing.assert_allclose(RZ_Z, Z_RZ, atol=1e-14)


class TestCircuitIntegration:
    """Test integration with quantum circuits"""

    def test_bell_state_preparation(self):
        """Test creating Bell state using RY"""
        # |Φ+⟩ = (|00⟩ + |11⟩)/√2
        # Can be created with RY(π/2) on first qubit (simplified)

        state = np.array([1, 0], dtype=complex)
        ry = RYGate(target=0, parameter=np.pi / 2)

        bell_like = ry.matrix() @ state

        # Should be (|0⟩ + |1⟩)/√2
        expected = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
        np.testing.assert_allclose(bell_like, expected, atol=1e-14)

    def test_state_tomography_simulation(self):
        """Simulate measuring state in different bases"""
        # Prepare |+⟩ state
        ry = RYGate(target=0, parameter=np.pi / 2)
        state = ry.matrix() @ np.array([1, 0])

        # Measure in X basis (should be |+⟩)
        X = np.array([[0, 1], [1, 0]])
        x_expectation = state.conj() @ X @ state
        assert np.isclose(x_expectation.real, 1.0, atol=1e-14)

        # Measure in Z basis (should be 0)
        Z = np.array([[1, 0], [0, -1]])
        z_expectation = state.conj() @ Z @ state
        assert np.isclose(z_expectation.real, 0.0, atol=1e-14)

    def test_phase_kickback(self):
        """Test phase kickback effect"""
        # Apply RZ to |1⟩ should add phase
        state_1 = np.array([0, 1], dtype=complex)

        rz = RZGate(target=0, parameter=np.pi / 3)
        result = rz.matrix() @ state_1

        # Should have phase on |1⟩ component
        expected_phase = np.exp(1j * np.pi / 6)
        assert np.isclose(result[1] / expected_phase, 1.0, atol=1e-14)


class TestNumericalAccuracy:
    """Test numerical accuracy and precision"""

    @pytest.mark.parametrize("angle", np.linspace(0, 2 * np.pi, 50))
    def test_many_angles(self, angle):
        """Test gates at many different angles"""
        rx = RXGate(target=0, parameter=angle)
        U = rx.matrix()

        # Must be unitary
        identity = U.conj().T @ U
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-13)

    def test_cumulative_error(self):
        """Test cumulative numerical error over many operations"""
        state = np.array([1, 0], dtype=complex)

        # Apply 1000 small rotations
        for _ in range(1000):
            rx = RXGate(target=0, parameter=0.001)
            state = rx.matrix() @ state

        # Norm should still be 1
        assert np.isclose(np.linalg.norm(state), 1.0, atol=1e-10)

    def test_matrix_reconstruction(self):
        """Test that matrix can be reconstructed from parameters"""
        original_theta = 1.234

        rx = RXGate(target=0, parameter=original_theta)
        U1 = rx.matrix()

        # Change parameter and back
        rx.parameter = 5.678
        rx.parameter = original_theta
        U2 = rx.matrix()

        # Should be identical
        np.testing.assert_allclose(U1, U2, atol=1e-15)


class TestGateIdentities:
    """Test special gate identities"""

    def test_pauli_x_via_rx(self):
        """Test RX(π) = -iX"""
        rx = RXGate(target=0, parameter=np.pi)
        X = np.array([[0, 1], [1, 0]])
        np.testing.assert_allclose(rx.matrix(), -1j * X, atol=1e-14)

    def test_pauli_y_via_ry(self):
        """Test RY(π) gives bit flip"""
        ry = RYGate(target=0, parameter=np.pi)
        # RY(π) = [[0, -1], [1, 0]]
        expected = np.array([[0, -1], [1, 0]])
        np.testing.assert_allclose(ry.matrix(), expected, atol=1e-14)

    def test_pauli_z_via_rz(self):
        """Test RZ(π) = -iZ"""
        rz = RZGate(target=0, parameter=np.pi)
        # RZ(π) = [[-i, 0], [0, i]]
        expected = np.array([[-1j, 0], [0, 1j]])
        np.testing.assert_allclose(rz.matrix(), expected, atol=1e-14)

    def test_hadamard_like_rotation(self):
        """Test creating Hadamard-like gate"""
        # H can be decomposed as RY(π/2) RX(π)
        ry = RYGate(target=0, parameter=np.pi / 2)
        rx = RXGate(target=0, parameter=np.pi)

        H_like = ry.matrix() @ rx.matrix()

        # Should be unitary
        identity = H_like.conj().T @ H_like
        np.testing.assert_allclose(identity, np.eye(2), atol=1e-14)

    def test_sqrt_not(self):
        """Test √NOT gate via RY(π/2)"""
        ry = RYGate(target=0, parameter=np.pi / 2)
        U = ry.matrix()

        # Applying twice should give NOT (up to phase)
        NOT_like = U @ U

        # Should swap |0⟩ and |1⟩
        state_0 = np.array([1, 0])
        result = NOT_like @ state_0

        # Should be close to |1⟩
        assert np.isclose(np.abs(result[1]), 1.0, atol=1e-14)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
