"""
Quantum Neural Network Base Classes

Provides foundational components for building quantum neural networks.
"""

import numpy as np
from typing import Optional, Callable, List
from abc import ABC, abstractmethod


class QNNLayer(ABC):
    """
    Base class for quantum neural network layers.

    All QNN layers inherit from this class and implement the build_circuit method.
    """

    def __init__(self, n_qubits: int, name: Optional[str] = None):
        """
        Initialize QNN layer.

        Args:
            n_qubits: Number of qubits in the layer
            name: Optional layer name
        """
        self.n_qubits = n_qubits
        self.name = name or self.__class__.__name__
        self._n_parameters = 0

    @abstractmethod
    def build_circuit(
        self, params: Optional[np.ndarray] = None, data: Optional[np.ndarray] = None
    ):
        """
        Build the quantum circuit for this layer.

        Args:
            params: Trainable parameters (for variational layers)
            data: Input data (for encoding layers)

        Returns:
            QuantumCircuit for this layer
        """
        pass

    @property
    def num_parameters(self) -> int:
        """Number of trainable parameters in this layer"""
        return self._n_parameters

    def __repr__(self) -> str:
        return f"{self.name}(n_qubits={self.n_qubits}, params={self.num_parameters})"


class ParameterizedLayer(QNNLayer):
    """
    Base class for layers with trainable parameters.
    """

    def __init__(self, n_qubits: int, n_parameters: int, name: Optional[str] = None):
        super().__init__(n_qubits, name)
        self._n_parameters = n_parameters
        self.parameters = None

    def initialize_parameters(
        self, method: str = "random", seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Initialize layer parameters.

        Args:
            method: Initialization method ('random', 'zeros', 'small')
            seed: Random seed for reproducibility

        Returns:
            Initialized parameters
        """
        if seed is not None:
            np.random.seed(seed)

        if method == "random":
            params = np.random.uniform(0, 2 * np.pi, self._n_parameters)
        elif method == "zeros":
            params = np.zeros(self._n_parameters)
        elif method == "small":
            params = np.random.normal(0, 0.1, self._n_parameters)
        else:
            raise ValueError(f"Unknown initialization method: {method}")

        self.parameters = params
        return params
