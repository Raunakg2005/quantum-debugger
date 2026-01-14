"""
Quantum gate library

Standard quantum gates and their matrix representations.
"""

import numpy as np


class GateLibrary:
    """Library of standard quantum gates"""

    # Single-qubit gates
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

    X = np.array([[0, 1], [1, 0]], dtype=complex)

    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    S = np.array([[1, 0], [0, 1j]], dtype=complex)

    T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

    @staticmethod
    def RX(theta: float) -> np.ndarray:
        """Rotation around X-axis"""
        return np.array(
            [
                [np.cos(theta / 2), -1j * np.sin(theta / 2)],
                [-1j * np.sin(theta / 2), np.cos(theta / 2)],
            ],
            dtype=complex,
        )

    @staticmethod
    def RY(theta: float) -> np.ndarray:
        """Rotation around Y-axis"""
        return np.array(
            [
                [np.cos(theta / 2), -np.sin(theta / 2)],
                [np.sin(theta / 2), np.cos(theta / 2)],
            ],
            dtype=complex,
        )

    @staticmethod
    def RZ(theta: float) -> np.ndarray:
        """Rotation around Z-axis"""
        return np.array(
            [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
        )

    @staticmethod
    def PHASE(theta: float) -> np.ndarray:
        """Phase shift gate (P gate)"""
        return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)

    @staticmethod
    def CP(theta: float) -> np.ndarray:
        """Controlled-Phase gate (two-qubit)"""
        return np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, np.exp(1j * theta)]],
            dtype=complex,
        )

    # Two-qubit gates (little-endian: qubit 0 is LSB)
    # CNOT: control=qubit 0, target=qubit 1
    # Flips target when control is 1: |10⟩↔|11⟩ (indices 1↔3)
    CNOT = np.array(
        [
            [1, 0, 0, 0],  # |00⟩ → |00⟩
            [0, 0, 0, 1],  # |10⟩ → |11⟩
            [0, 0, 1, 0],  # |01⟩ → |01⟩
            [0, 1, 0, 0],  # |11⟩ → |10⟩
        ],
        dtype=complex,
    )

    CZ = np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=complex
    )

    SWAP = np.array(
        [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
    )

    # Three-qubit gates
    # Toffoli (CCNOT) for little-endian: controls on qubits 0,1; target is qubit 2
    # Flips target when both controls are 1 (indices 3↔7 in little-endian)
    TOFFOLI = np.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],  # |110⟩ ↔ |111⟩
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],  # |111⟩ ↔ |110⟩
        ],
        dtype=complex,
    )


class Gate:
    """Represents a gate operation"""

    def __init__(
        self, name: str, matrix: np.ndarray, qubits: list, params: dict = None
    ):
        self.name = name
        self.matrix = matrix
        self.qubits = qubits
        self.params = params or {}

    def __repr__(self):
        if self.params:
            param_str = ", ".join(f"{k}={v:.3f}" for k, v in self.params.items())
            return f"{self.name}({param_str}) on {self.qubits}"
        return f"{self.name} on {self.qubits}"

    def __str__(self):
        return self.__repr__()
