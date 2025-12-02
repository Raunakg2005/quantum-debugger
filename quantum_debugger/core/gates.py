"""
Quantum gate definitions and operations
"""

import numpy as np
from typing import Dict, Callable


class GateLibrary:
    """Library of standard quantum gates"""

    # Single-qubit gates
    I = np.array([[1, 0], [0, 1]], dtype=complex)  # Identity
    X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X (NOT)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y
    Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Hadamard
    S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
    T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)  # T gate
    
    # Rotation gates (parameterized)
    @staticmethod
    def RX(theta: float) -> np.ndarray:
        """Rotation around X-axis"""
        return np.array([
            [np.cos(theta / 2), -1j * np.sin(theta / 2)],
            [-1j * np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def RY(theta: float) -> np.ndarray:
        """Rotation around Y-axis"""
        return np.array([
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def RZ(theta: float) -> np.ndarray:
        """Rotation around Z-axis"""
        return np.array([
            [np.exp(-1j * theta / 2), 0],
            [0, np.exp(1j * theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def PHASE(theta: float) -> np.ndarray:
        """Phase shift gate"""
        return np.array([
            [1, 0],
            [0, np.exp(1j * theta)]
        ], dtype=complex)
    
    # Two-qubit gates
    CNOT = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)
    
    CZ = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1]
    ], dtype=complex)
    
    SWAP = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=complex)
    
    # Three-qubit gates
    TOFFOLI = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0]
    ], dtype=complex)
    
    @staticmethod
    def controlled_gate(gate: np.ndarray) -> np.ndarray:
        """Create a controlled version of a single-qubit gate"""
        n = gate.shape[0]
        controlled = np.eye(2 * n, dtype=complex)
        controlled[n:, n:] = gate
        return controlled
    
    @staticmethod
    def tensor_product(*gates) -> np.ndarray:
        """Compute tensor product of multiple gates"""
        result = gates[0]
        for gate in gates[1:]:
            result = np.kron(result, gate)
        return result


class Gate:
    """Represents a quantum gate operation"""
    
    def __init__(self, name: str, matrix: np.ndarray, qubits: list, params: dict = None):
        """
        Initialize a gate
        
        Args:
            name: Gate name (e.g., 'H', 'CNOT', 'RX')
            matrix: Unitary matrix representing the gate
            qubits: List of qubit indices the gate acts on
            params: Optional parameters (e.g., rotation angles)
        """
        self.name = name
        self.matrix = matrix
        self.qubits = qubits if isinstance(qubits, list) else [qubits]
        self.params = params or {}
    
    def __repr__(self):
        qubit_str = ','.join(map(str, self.qubits))
        if self.params:
            param_str = ','.join(f"{k}={v}" for k, v in self.params.items())
            return f"{self.name}({param_str})[q{qubit_str}]"
        return f"{self.name}[q{qubit_str}]"
    
    def __str__(self):
        return self.__repr__()
    
    @property
    def num_qubits(self):
        """Number of qubits this gate acts on"""
        return len(self.qubits)
    
    def is_controlled(self):
        """Check if this is a controlled gate"""
        return self.num_qubits > 1 and self.name.startswith('C')
    
    def dagger(self):
        """Return the conjugate transpose of this gate"""
        return Gate(
            name=f"{self.name}†",
            matrix=self.matrix.conj().T,
            qubits=self.qubits,
            params=self.params
        )
