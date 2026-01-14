"""
Variational Layers for Quantum Neural Networks

Trainable layers using quantum circuit ansätze.
"""

import numpy as np
from typing import Optional
from .base import ParameterizedLayer
from ...core.circuit import QuantumCircuit
from ..ansatz import (
    real_amplitudes,
    two_local,
    excitation_preserving,
    strongly_entangling,
)


class VariationalLayer(ParameterizedLayer):
    """
    Trainable quantum layer using ansatz templates.

    This layer contains trainable parameters that are optimized
    during training.
    """

    def __init__(
        self, n_qubits: int, ansatz: str = "real_amplitudes", reps: int = 1, **kwargs
    ):
        """
        Initialize variational layer.

        Args:
            n_qubits: Number of qubits
            ansatz: Ansatz type ('real_amplitudes', 'two_local',
                    'excitation_preserving', 'strongly_entangling')
            reps: Number of repetitions
            **kwargs: Additional ansatz arguments
        """
        # Create ansatz to get parameter count
        self.ansatz_type = ansatz
        self.reps = reps
        self.kwargs = kwargs

        if ansatz == "real_amplitudes":
            self.ansatz_fn = real_amplitudes(n_qubits, reps, **kwargs)
        elif ansatz == "two_local":
            self.ansatz_fn = two_local(n_qubits, reps=reps, **kwargs)
        elif ansatz == "excitation_preserving":
            self.ansatz_fn = excitation_preserving(n_qubits, reps, **kwargs)
        elif ansatz == "strongly_entangling":
            self.ansatz_fn = strongly_entangling(n_qubits, reps)
        else:
            raise ValueError(f"Unknown ansatz: {ansatz}")

        n_parameters = self.ansatz_fn.num_parameters

        super().__init__(n_qubits, n_parameters, name=f"VariationalLayer_{ansatz}")

    def build_circuit(
        self, params: Optional[np.ndarray] = None, data: Optional[np.ndarray] = None
    ) -> QuantumCircuit:
        """
        Build variational circuit with given parameters.

        Args:
            params: Trainable parameters for the layer
            data: Not used (variational layers don't use input data)

        Returns:
            Parameterized quantum circuit
        """
        if params is None:
            if self.parameters is None:
                # Initialize if not done
                params = self.initialize_parameters("random")
            else:
                params = self.parameters

        if len(params) != self.num_parameters:
            raise ValueError(
                f"Expected {self.num_parameters} parameters, got {len(params)}"
            )

        # Build circuit using ansatz
        circuit = self.ansatz_fn(params)

        return circuit

    def __repr__(self) -> str:
        return (
            f"VariationalLayer(ansatz={self.ansatz_type}, params={self.num_parameters})"
        )
