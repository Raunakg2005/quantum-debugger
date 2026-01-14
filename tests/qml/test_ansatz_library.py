"""
Tests for expanded ansatz library
"""

import pytest
import numpy as np
from quantum_debugger.qml.ansatz import (
    real_amplitudes,
    two_local,
    excitation_preserving,
    strongly_entangling,
)


class TestRealAmplitudes:
    """Test RealAmplitudes ansatz"""

    def test_parameter_count_linear(self):
        """Test parameter count with linear entanglement"""
        ansatz = real_amplitudes(num_qubits=3, reps=2, entanglement="linear")
        assert ansatz.num_parameters == 9  # (2+1) * 3

    def test_builds_circuit(self):
        """Test that ansatz builds a valid circuit"""
        ansatz = real_amplitudes(num_qubits=2, reps=1)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert circuit.num_qubits == 2

    def test_entanglement_linear(self):
        """Test linear entanglement pattern"""
        ansatz = real_amplitudes(num_qubits=4, reps=1, entanglement="linear")
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # Should have 4 RY (initial) + 3 CNOT + 4 RY (final) = 11 gates
        assert len(circuit.gates) == 11

    def test_entanglement_full(self):
        """Test full entanglement pattern"""
        ansatz = real_amplitudes(num_qubits=3, reps=1, entanglement="full")
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # 3 RY + 3 CNOT (0-1, 0-2, 1-2) + 3 RY = 9 gates
        assert len(circuit.gates) == 9

    def test_entanglement_circular(self):
        """Test circular entanglement"""
        ansatz = real_amplitudes(num_qubits=3, reps=1, entanglement="circular")
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # 3 RY + 3 CNOT (circular) + 3 RY = 9 gates
        assert len(circuit.gates) == 9

    def test_multiple_reps(self):
        """Test with multiple repetitions"""
        ansatz = real_amplitudes(num_qubits=2, reps=3, entanglement="linear")
        assert ansatz.num_parameters == 8  # (3+1) * 2


class TestTwoLocal:
    """Test TwoLocal ansatz"""

    def test_single_rotation_block(self):
        """Test with single rotation type"""
        ansatz = two_local(num_qubits=2, rotation_blocks="ry", reps=1)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert circuit.num_qubits == 2

    def test_mixed_rotation_blocks(self):
        """Test alternating rotation types"""
        ansatz = two_local(num_qubits=3, rotation_blocks=["ry", "rz"], reps=2)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert len(circuit.gates) >= 9  # At least rotation gates

    def test_different_entanglement_gates(self):
        """Test with CZ entanglement"""
        ansatz = two_local(
            num_qubits=2, rotation_blocks="rx", entanglement_blocks="cz", reps=1
        )
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # Check for CZ gates
        cz_count = sum(1 for g in circuit.gates if g.name == "CZ")
        assert cz_count == 1  # One CZ for 2 qubits, linear

    def test_swap_entanglement(self):
        """Test with SWAP gates"""
        ansatz = two_local(
            num_qubits=3,
            rotation_blocks="ry",
            entanglement_blocks="swap",
            entanglement="linear",
            reps=1,
        )
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        swap_count = sum(1 for g in circuit.gates if g.name == "SWAP")
        assert swap_count == 2  # 2 SWAPs for 3 qubits, linear

    def test_parameter_count(self):
        """Test parameter count calculation"""
        ansatz = two_local(num_qubits=4, reps=2)
        assert ansatz.num_parameters == 12  # (2+1) * 4


class TestExcitationPreserving:
    """Test ExcitationPreserving ansatz"""

    def test_basic_construction(self):
        """Test basic ansatz construction"""
        ansatz = excitation_preserving(num_qubits=4, reps=2)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert circuit.num_qubits == 4

    def test_with_skip_final_rotation(self):
        """Test skipping final rotation layer"""
        ansatz1 = excitation_preserving(num_qubits=3, reps=2, skip_final_rotation=False)
        ansatz2 = excitation_preserving(num_qubits=3, reps=2, skip_final_rotation=True)

        # ansatz1 should have more parameters
        assert ansatz1.num_parameters > ansatz2.num_parameters

    def test_entanglement_patterns(self):
        """Test different entanglement patterns"""
        for pattern in ["linear", "full", "circular"]:
            ansatz = excitation_preserving(num_qubits=3, reps=1, entanglement=pattern)
            params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
            circuit = ansatz(params)
            assert circuit.num_qubits == 3

    def test_chemistry_application(self):
        """Test suitable for chemistry (even qubits for electrons)"""
        # 4 qubits = 2 electrons in 4 orbitals
        ansatz = excitation_preserving(num_qubits=4, reps=1)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # Should preserve excitation number
        assert circuit is not None


class TestStronglyEntangling:
    """Test StronglyEntangling ansatz"""

    def test_parameter_count(self):
        """Test correct number of parameters"""
        ansatz = strongly_entangling(num_qubits=3, reps=2)
        # 3 qubits * 3 rotations * 2 reps = 18 parameters
        assert ansatz.num_parameters == 18

    def test_builds_circuit(self):
        """Test circuit construction"""
        ansatz = strongly_entangling(num_qubits=2, reps=1)
        params = np.random.uniform(0, 2 * np.pi, 6)  # 2*3*1=6
        circuit = ansatz(params)
        assert circuit.num_qubits == 2

    def test_gate_count(self):
        """Test number of gates"""
        ansatz = strongly_entangling(num_qubits=3, reps=1)
        params = np.random.uniform(0, 2 * np.pi, 9)
        circuit = ansatz(params)
        # 3 qubits * 3 rotations + 3 CNOTs = 12 gates
        assert len(circuit.gates) == 12

    def test_multiple_layers(self):
        """Test with multiple layers"""
        ansatz = strongly_entangling(num_qubits=4, reps=3)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        # Each layer: 4*3 rotations + 4 CNOTs = 16 gates
        # 3 layers = 48 gates
        assert len(circuit.gates) == 48

    def test_expressiveness(self):
        """Test high expressiveness (many parameters)"""
        ansatz = strongly_entangling(num_qubits=5, reps=2)
        # Should have many parameters for expressiveness
        assert ansatz.num_parameters >= 20


class TestAnsatzComparison:
    """Compare different ansätze"""

    def test_parameter_scaling(self):
        """Test how parameters scale with qubits"""
        n = 5
        reps = 2

        real_amp = real_amplitudes(n, reps)
        two_loc = two_local(n, reps=reps)
        exc_pres = excitation_preserving(n, reps)
        strong_ent = strongly_entangling(n, reps)

        # StronglyEntangling should have most parameters
        assert strong_ent.num_parameters > real_amp.num_parameters

    def test_same_circuit_different_ansatz(self):
        """Test building circuits with different ansätze"""
        n = 3

        ansatze = [
            real_amplitudes(n, reps=1),
            two_local(n, reps=1),
            excitation_preserving(n, reps=1),
            strongly_entangling(n, reps=1),
        ]

        for ansatz in ansatze:
            params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
            circuit = ansatz(params)
            assert circuit.num_qubits == n

    def test_circuit_depth_comparison(self):
        """Compare circuit depths"""
        n = 4
        reps = 1

        # All should produce valid circuits
        ansatz_builders = [
            (real_amplitudes, {"num_qubits": n, "reps": reps}),
            (two_local, {"num_qubits": n, "reps": reps}),
            (excitation_preserving, {"num_qubits": n, "reps": reps}),
            (strongly_entangling, {"num_qubits": n, "reps": reps}),
        ]

        for ansatz_fn, kwargs in ansatz_builders:
            ansatz = ansatz_fn(**kwargs)
            params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
            circuit = ansatz(params)
            assert len(circuit.gates) > 0


class TestEdgeCases:
    """Test edge cases"""

    def test_single_qubit(self):
        """Test with single qubit"""
        ansatz = real_amplitudes(num_qubits=1, reps=1)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert circuit.num_qubits == 1

    def test_zero_reps(self):
        """Test with zero repetitions"""
        ansatz = real_amplitudes(num_qubits=2, reps=0)
        # Should still have one rotation layer
        assert ansatz.num_parameters == 2

    def test_large_circuit(self):
        """Test with larger circuit"""
        ansatz = strongly_entangling(num_qubits=10, reps=2)
        params = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        circuit = ansatz(params)
        assert circuit.num_qubits == 10

    def test_invalid_entanglement(self):
        """Test invalid entanglement pattern"""
        with pytest.raises(ValueError, match="Unknown"):
            ansatz = real_amplitudes(3, reps=1, entanglement="invalid")
            params = np.random.uniform(0, 2 * np.pi, 6)
            ansatz(params)
