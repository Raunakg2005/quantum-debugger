"""
Extreme edge cases and stress tests for Cirq integration
"""

import pytest
import numpy as np
import cirq
from quantum_debugger import QuantumCircuit
from quantum_debugger.integrations import CirqAdapter


@pytest.mark.skipif(not cirq, reason="Cirq not installed")
class TestCirqEdgeCases:
    """Edge cases and boundary conditions"""

    def test_single_qubit_circuit(self):
        """Test minimal 1-qubit circuit"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append(cirq.H(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 1
        assert len(qd_circuit.gates) == 1

    def test_empty_circuit(self):
        """Test empty circuit"""
        qubits = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        # Add qubits to circuit
        for q in qubits:
            cirq_circuit.append(cirq.I(q))  # Identity gates

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 2

    def test_max_qubits(self):
        """Test large number of qubits"""
        n = 20  # 20 qubits
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        for q in qubits:
            cirq_circuit.append(cirq.H(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 20
        assert len(qd_circuit.gates) == 20

    def test_very_deep_circuit(self):
        """Test very deep circuit (many layers)"""
        n_layers = 100
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()

        for _ in range(n_layers):
            cirq_circuit.append(cirq.H(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert len(qd_circuit.gates) == 100

    def test_zero_angle_rotation(self):
        """Test rotation with zero angle"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append(cirq.Rx(rads=0)(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 1
        assert len(qd_circuit.gates) == 1

    def test_two_pi_rotation(self):
        """Test 2π rotation (identity)"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append(cirq.Rx(rads=2 * np.pi)(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        result = CirqAdapter.simulate_cirq(qd_circuit)

        # Should be close to |0⟩
        expected = np.array([1.0, 0.0])
        np.testing.assert_array_almost_equal(
            np.abs(result["state_vector"]), expected, decimal=5
        )

    def test_negative_angles(self):
        """Test negative rotation angles"""
        q = cirq.LineQubit(0)
        angles = [-np.pi / 2, -np.pi / 4, -np.pi]

        for angle in angles:
            cirq_circuit = cirq.Circuit()
            cirq_circuit.append(cirq.Ry(rads=angle)(q))

            qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
            assert len(qd_circuit.gates) == 1

    def test_consecutive_same_gates(self):
        """Test many consecutive same gates"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()

        # 10 consecutive X gates = identity (2^10 = 1024 mod 2 = 0)
        for _ in range(10):
            cirq_circuit.append(cirq.X(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        result = CirqAdapter.simulate_cirq(qd_circuit)

        # Should be |0⟩
        expected = np.array([1.0, 0.0])
        np.testing.assert_array_almost_equal(
            np.abs(result["state_vector"]), expected, decimal=10
        )

    def test_all_gates_on_same_qubit(self):
        """Test applying all gate types to single qubit"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()

        cirq_circuit.append(
            [
                cirq.H(q),
                cirq.X(q),
                cirq.Y(q),
                cirq.Z(q),
                cirq.S(q),
                cirq.T(q),
                cirq.Rx(rads=0.1)(q),
                cirq.Ry(rads=0.2)(q),
                cirq.Rz(rads=0.3)(q),
            ]
        )

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert len(qd_circuit.gates) == 9

    def test_long_entanglement_chain(self):
        """Test long chain of entangling gates"""
        n = 15
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        # Create chain
        cirq_circuit.append(cirq.H(qubits[0]))
        for i in range(n - 1):
            cirq_circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 15
        assert len(qd_circuit.gates) == 15  # 1 H + 14 CNOTs


@pytest.mark.skipif(not cirq, reason="Cirq not installed")
class TestCirqStressTests:
    """Stress tests and performance"""

    @pytest.mark.skip(reason="12-qubit test is slow, skip for regular testing")
    def test_wide_and_deep_circuit(self):
        """Test circuit that is both wide and deep"""
        n_qubits = 12
        n_layers = 20
        qubits = cirq.LineQubit.range(n_qubits)
        cirq_circuit = cirq.Circuit()

        for layer in range(n_layers):
            # Single-qubit layer
            for q in qubits:
                cirq_circuit.append(cirq.Ry(rads=np.pi / 4 * layer)(q))

            # Two-qubit layer
            for i in range(0, n_qubits - 1, 2):
                cirq_circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 12
        # 20 layers * (12 RY + 6 CNOT) = 360 gates
        assert len(qd_circuit.gates) == 360

    def test_random_circuit_large(self):
        """Test large random circuit"""
        np.random.seed(123)
        n_qubits = 15
        n_gates = 200

        qubits = cirq.LineQubit.range(n_qubits)
        cirq_circuit = cirq.Circuit()

        gates = [cirq.H, cirq.X, cirq.Y, cirq.Z, cirq.S, cirq.T]

        for _ in range(n_gates):
            if np.random.random() < 0.7:
                gate = np.random.choice(gates)
                qubit = np.random.choice(qubits)
                cirq_circuit.append(gate(qubit))
            else:
                q1, q2 = np.random.choice(qubits, size=2, replace=False)
                cirq_circuit.append(cirq.CNOT(q1, q2))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 15
        assert len(qd_circuit.gates) == 200

    def test_alternating_gates_pattern(self):
        """Test repeating pattern of gates"""
        n_repeats = 50
        qubits = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()

        for _ in range(n_repeats):
            cirq_circuit.append(
                [
                    cirq.H(qubits[0]),
                    cirq.CNOT(qubits[0], qubits[1]),
                    cirq.T(qubits[0]),
                    cirq.T(qubits[1]),
                ]
            )

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert len(qd_circuit.gates) == 200  # 50 * 4

    def test_all_to_all_connectivity(self):
        """Test circuit with all-to-all connectivity"""
        n = 6
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        # Apply CNOT between all pairs
        for i in range(n):
            for j in range(i + 1, n):
                cirq_circuit.append(cirq.CNOT(qubits[i], qubits[j]))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        # C(6,2) = 15 pairs
        assert len(qd_circuit.gates) == 15


@pytest.mark.skipif(not cirq, reason="Cirq not installed")
class TestCirqRobustness:
    """Robustness and error handling"""

    def test_multiple_roundtrips(self):
        """Test multiple roundtrip conversions"""
        q0, q1 = cirq.LineQubit.range(2)
        original = cirq.Circuit()
        original.append([cirq.H(q0), cirq.CNOT(q0, q1)])

        # Multiple roundtrips
        circuit = original
        for _ in range(5):
            qd = CirqAdapter.from_cirq(circuit)
            circuit = CirqAdapter.to_cirq(qd)

        # Should maintain structure
        assert len(list(circuit.all_operations())) == 2

    def test_grid_qubits(self):
        """Test with GridQubits instead of LineQubits"""
        qubits = [cirq.GridQubit(i, j) for i in range(2) for j in range(2)]
        cirq_circuit = cirq.Circuit()

        for q in qubits:
            cirq_circuit.append(cirq.H(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 4
        assert len(qd_circuit.gates) == 4

    def test_mixed_qubit_types_conversion(self):
        """Test conversion back with different qubit types"""
        q0, q1 = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit()
        cirq_circuit.append([cirq.H(q0), cirq.CNOT(q0, q1)])

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)

        # Convert back with GridQubits
        grid_qubits = [cirq.GridQubit(0, 0), cirq.GridQubit(0, 1)]
        cirq_back = CirqAdapter.to_cirq(qd_circuit, qubits=grid_qubits)

        assert set(cirq_back.all_qubits()) == set(grid_qubits)

    def test_very_small_angles(self):
        """Test with very small rotation angles"""
        q = cirq.LineQubit(0)
        small_angles = [1e-10, 1e-8, 1e-6, 1e-4]

        for angle in small_angles:
            cirq_circuit = cirq.Circuit()
            cirq_circuit.append(cirq.Rx(rads=angle)(q))

            qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
            result = CirqAdapter.simulate_cirq(qd_circuit)

            # Should still be normalized
            total_prob = np.sum(np.abs(result["state_vector"]) ** 2)
            np.testing.assert_almost_equal(total_prob, 1.0, decimal=10)

    def test_very_large_angles(self):
        """Test with very large rotation angles"""
        q = cirq.LineQubit(0)
        large_angles = [10 * np.pi, 100 * np.pi, 1000 * np.pi]

        for angle in large_angles:
            cirq_circuit = cirq.Circuit()
            cirq_circuit.append(cirq.Rz(rads=angle)(q))

            qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
            result = CirqAdapter.simulate_cirq(qd_circuit)

            # Should still be normalized
            total_prob = np.sum(np.abs(result["state_vector"]) ** 2)
            np.testing.assert_almost_equal(total_prob, 1.0, decimal=10)

    def test_compare_with_original_simulation(self):
        """Compare simulation results between Cirq and converted circuit"""
        test_cases = [
            # (n_qubits, circuit_builder)
            (2, lambda qs: [cirq.H(qs[0]), cirq.CNOT(qs[0], qs[1])]),
            (3, lambda qs: [cirq.H(qs[i]) for i in range(3)]),
            (2, lambda qs: [cirq.X(qs[0]), cirq.Y(qs[1]), cirq.CZ(qs[0], qs[1])]),
        ]

        for n_qubits, builder in test_cases:
            qubits = cirq.LineQubit.range(n_qubits)
            cirq_circuit = cirq.Circuit()
            cirq_circuit.append(builder(qubits))

            # Original simulation
            sim = cirq.Simulator()
            original = sim.simulate(cirq_circuit)

            # Converted simulation
            qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
            converted = CirqAdapter.simulate_cirq(qd_circuit)

            # Compare
            np.testing.assert_array_almost_equal(
                np.abs(original.final_state_vector),
                np.abs(converted["state_vector"]),
                decimal=10,
            )

    def test_numerical_stability_deep_circuit(self):
        """Test numerical stability with deep circuit"""
        q = cirq.LineQubit(0)
        cirq_circuit = cirq.Circuit()

        # Apply many small rotations
        for i in range(1000):
            cirq_circuit.append(cirq.Ry(rads=0.001)(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        result = CirqAdapter.simulate_cirq(qd_circuit)

        # Should still be normalized
        total_prob = np.sum(np.abs(result["state_vector"]) ** 2)
        np.testing.assert_almost_equal(total_prob, 1.0, decimal=6)


@pytest.mark.skipif(not cirq, reason="Cirq not installed")
class TestCirqSpecialCases:
    """Special circuit patterns and cases"""

    def test_cat_state(self):
        """Test cat state creation"""
        n = 8
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        # Create cat state
        cirq_circuit.append(cirq.H(qubits[0]))
        for i in range(n - 1):
            cirq_circuit.append(cirq.CNOT(qubits[0], qubits[i + 1]))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert len(qd_circuit.gates) == n

    def test_w_state(self):
        """Test W state preparation (simplified)"""
        n = 4
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        # Simplified W state circuit
        for q in qubits:
            cirq_circuit.append(cirq.Ry(rads=np.pi / n)(q))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 4

    def test_phase_estimation_subcircuit(self):
        """Test phase estimation subcircuit"""
        qubits = cirq.LineQubit.range(4)
        cirq_circuit = cirq.Circuit()

        # Prepare eigenstate
        cirq_circuit.append(cirq.X(qubits[3]))

        # QFT on first 3 qubits (simplified)
        for i in range(3):
            cirq_circuit.append(cirq.H(qubits[i]))

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert qd_circuit.num_qubits == 4

    def test_ladder_circuit(self):
        """Test ladder-like circuit structure"""
        n = 6
        qubits = cirq.LineQubit.range(n)
        cirq_circuit = cirq.Circuit()

        # Ladder pattern
        for i in range(n - 1):
            cirq_circuit.append(
                [
                    cirq.H(qubits[i]),
                    cirq.CNOT(qubits[i], qubits[i + 1]),
                ]
            )

        qd_circuit = CirqAdapter.from_cirq(cirq_circuit)
        assert len(qd_circuit.gates) == 10  # 5 H + 5 CNOT
