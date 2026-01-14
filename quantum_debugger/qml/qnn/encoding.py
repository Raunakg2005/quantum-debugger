"""
Encoding Layers for Quantum Neural Networks

Layers that encode classical data into quantum states.
"""

import numpy as np
from typing import Optional
from .base import QNNLayer
from ...core.circuit import QuantumCircuit
from ..data.feature_maps import zz_feature_map, pauli_feature_map, angle_encoding


class EncodingLayer(QNNLayer):
    """
    Encodes classical data into quantum states using feature maps.

    This layer has no trainable parameters - it only transforms
    classical input into quantum states.
    """

    def __init__(self, n_qubits: int, feature_map: str = "zz", reps: int = 1, **kwargs):
        """
        Initialize encoding layer.

        Args:
            n_qubits: Number of qubits
            feature_map: Type of feature map ('zz', 'pauli', 'angle')
            reps: Number of repetitions
            **kwargs: Additional arguments for feature map
        """
        super().__init__(n_qubits, name=f"EncodingLayer_{feature_map}")
        self.feature_map_type = feature_map
        self.reps = reps
        self.kwargs = kwargs
        self._n_parameters = 0  # No trainable parameters

        # Create feature map function
        if feature_map == "zz":
            self.feature_map = zz_feature_map(n_qubits, reps)
        elif feature_map == "pauli":
            self.feature_map = pauli_feature_map(n_qubits, reps=reps, **kwargs)
        elif feature_map == "angle":
            rotation = kwargs.get("rotation", "Y")
            self.feature_map = angle_encoding(n_qubits, rotation)
        else:
            raise ValueError(f"Unknown feature map: {feature_map}")

    def build_circuit(
        self, params: Optional[np.ndarray] = None, data: Optional[np.ndarray] = None
    ) -> QuantumCircuit:
        """
        Build encoding circuit for given data.

        Args:
            params: Not used (encoding layers have no parameters)
            data: Classical data to encode (shape: n_features)

        Returns:
            Quantum circuit encoding the data
        """
        if data is None:
            raise ValueError("EncodingLayer requires data input")

        if len(data) != self.n_qubits:
            raise ValueError(
                f"Data dimension {len(data)} doesn't match n_qubits {self.n_qubits}"
            )

        return self.feature_map(data)

    def __repr__(self) -> str:
        return f"EncodingLayer(map={self.feature_map_type}, qubits={self.n_qubits})"
