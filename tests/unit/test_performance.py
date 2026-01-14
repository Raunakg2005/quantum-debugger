"""
Performance and benchmark tests
"""

import pytest
import numpy as np
import time
from quantum_debugger import QuantumCircuit
from quantum_debugger.qml import VQE, QAOA
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian
from quantum_debugger.qml.ansatz import hardware_efficient_ansatz


class TestPerformance:
    """Performance benchmarks"""

    def test_circuit_creation_speed(self):
        """Benchmark circuit creation"""
        start = time.time()

        for _ in range(1000):
            qc = QuantumCircuit(5)
            qc.h(0)
            qc.cnot(0, 1)

        elapsed = time.time() - start
        assert elapsed < 1.0  # Should complete in under 1 second

    def test_gate_application_speed(self):
        """Benchmark gate operations"""
        qc = QuantumCircuit(10)

        start = time.time()
        for i in range(100):
            qc.h(i % 10)
        elapsed = time.time() - start

        assert elapsed < 0.5

    def test_vqe_execution_time(self):
        """Benchmark VQE execution"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)

        start = time.time()
        result = vqe.run(np.random.random(4))
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should complete reasonably fast
        assert "ground_state_energy" in result


class TestNumericalStability:
    """Numerical stability tests"""

    def test_very_small_parameters(self):
        """Test with very small rotation angles"""
        from quantum_debugger.qml.gates.parameterized import RYGate

        gate = RYGate(1e-15, 0)
        matrix = gate.matrix()

        # Should be close to identity
        identity = np.eye(2)
        np.testing.assert_array_almost_equal(matrix, identity, decimal=10)

    def test_very_large_parameters(self):
        """Test with very large rotation angles"""
        from quantum_debugger.qml.gates.parameterized import RZGate

        gate = RZGate(1000 * np.pi, 0)
        matrix = gate.matrix()

        # Should still be unitary
        product = matrix @ matrix.conj().T
        identity = np.eye(2)
        np.testing.assert_array_almost_equal(product, identity, decimal=8)

    def test_optimizer_numerical_stability(self):
        """Test optimizer handles edge cases"""
        from quantum_debugger.qml.optimizers import Adam

        opt = Adam(learning_rate=0.01)

        # Optimize simple quadratic
        params = np.array([10.0, -10.0])
        for _ in range(100):
            grad = 2 * params  # Gradient of x^2
            params = opt.step(params, grad)

        # Should move towards zero
        assert np.abs(params[0]) < 10.0
        assert np.abs(params[1]) < 10.0
