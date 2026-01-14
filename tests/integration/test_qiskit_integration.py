"""
Comprehensive tests for Qiskit integration
"""

import pytest
import numpy as np

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit import transpile
    from qiskit.quantum_info import Statevector

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

from quantum_debugger import QuantumCircuit
from quantum_debugger.integrations import QiskitAdapter


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
class TestQiskitIntegration:
    """Qiskit adapter integration tests"""

    def test_bell_state_conversion(self):
        """Test Bell state from Qiskit"""
        qc = QiskitCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 2
        assert len(qd.gates) == 2

    def test_ghz_state(self):
        """Test GHZ state"""
        n = 5
        qc = QiskitCircuit(n)
        qc.h(0)
        for i in range(n - 1):
            qc.cx(i, i + 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 5
        assert len(qd.gates) == 5

    def test_rotation_gates(self):
        """Test parameterized rotation gates"""
        qc = QiskitCircuit(1)
        qc.rx(np.pi / 4, 0)
        qc.ry(np.pi / 3, 0)
        qc.rz(np.pi / 2, 0)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 3

    def test_roundtrip_conversion(self):
        """Test Qiskit -> QD -> Qiskit"""
        qc_orig = QiskitCircuit(2)
        qc_orig.h(0)
        qc_orig.cx(0, 1)
        qc_orig.z(1)

        qd = QiskitAdapter.from_qiskit(qc_orig)
        qc_back = QiskitAdapter.to_qiskit(qd)

        assert qc_orig.num_qubits == qc_back.num_qubits
        assert len(qc_orig.data) == len(qc_back.data)

    def test_toffoli_gate(self):
        """Test Toffoli (CCX) gate"""
        qc = QiskitCircuit(3)
        qc.ccx(0, 1, 2)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 1
        assert qd.gates[0].name == "TOFFOLI"

    def test_swap_gate(self):
        """Test SWAP gate"""
        qc = QiskitCircuit(2)
        qc.swap(0, 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 1

    def test_all_single_qubit_gates(self):
        """Test all single-qubit gates"""
        qc = QiskitCircuit(1)
        qc.h(0)
        qc.x(0)
        qc.y(0)
        qc.z(0)
        qc.s(0)
        qc.t(0)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 6

    def test_controlled_gates(self):
        """Test controlled gates"""
        qc = QiskitCircuit(2)
        qc.cz(0, 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 1

    def test_empty_circuit(self):
        """Test empty circuit"""
        qc = QiskitCircuit(3)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 3
        assert len(qd.gates) == 0

    def test_large_circuit(self):
        """Test large random circuit"""
        n = 10
        qc = QiskitCircuit(n)

        for i in range(n):
            qc.h(i)
        for i in range(n - 1):
            qc.cx(i, i + 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 10
        assert len(qd.gates) == 19


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
class TestQiskitAdvanced:
    """Advanced Qiskit integration tests"""

    def test_vqe_ansatz(self):
        """Test VQE ansatz circuit"""
        qc = QiskitCircuit(4)

        # Prepare ansatz
        for i in range(4):
            qc.ry(np.pi / 4, i)

        for i in range(3):
            qc.cx(i, i + 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 7

    def test_qaoa_circuit(self):
        """Test QAOA-like circuit"""
        qc = QiskitCircuit(4)

        # Initialization
        for i in range(4):
            qc.h(i)

        # Problem layer (ZZ)
        for i in range(3):
            qc.cx(i, i + 1)
            qc.rz(0.5, i + 1)
            qc.cx(i, i + 1)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 4

    def test_quantum_phase_estimation(self):
        """Test QPE subcircuit"""
        qc = QiskitCircuit(4)

        # QFT
        for i in range(3):
            qc.h(i)

        # Eigenstate preparation
        qc.x(3)

        qd = QiskitAdapter.from_qiskit(qc)
        assert len(qd.gates) == 4

    def test_grover_oracle(self):
        """Test Grover oracle"""
        qc = QiskitCircuit(3)

        # Hadamard on all
        for i in range(3):
            qc.h(i)

        # Oracle (CCZ)
        qc.ccx(0, 1, 2)
        qc.z(2)
        qc.ccx(0, 1, 2)

        qd = QiskitAdapter.from_qiskit(qc)
        assert qd.num_qubits == 3

    def test_compare_circuits(self):
        """Test circuit comparison"""
        qc = QiskitCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        qd = QiskitAdapter.from_qiskit(qc)

        comparison = QiskitAdapter.compare_circuits(qc, qd)
        assert comparison["num_qubits_match"]
        assert comparison["num_gates_match"]

    def test_multiple_roundtrips(self):
        """Test stability over multiple conversions"""
        qc = QiskitCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        for _ in range(5):
            qd = QiskitAdapter.from_qiskit(qc)
            qc = QiskitAdapter.to_qiskit(qd)

        assert qc.num_qubits == 2
        assert len(qc.data) == 2
