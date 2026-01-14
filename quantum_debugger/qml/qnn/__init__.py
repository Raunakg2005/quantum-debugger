"""
Quantum Neural Network module
"""

from .base import QNNLayer, ParameterizedLayer
from .encoding import EncodingLayer
from .variational import VariationalLayer
from .network import QuantumNeuralNetwork
from .losses import (
    mean_squared_error,
    mean_absolute_error,
    binary_crossentropy,
    categorical_crossentropy,
    hinge_loss,
    get_loss_function,
)

__all__ = [
    # Base classes
    "QNNLayer",
    "ParameterizedLayer",
    # Layers
    "EncodingLayer",
    "VariationalLayer",
    # Network
    "QuantumNeuralNetwork",
    # Loss functions
    "mean_squared_error",
    "mean_absolute_error",
    "binary_crossentropy",
    "categorical_crossentropy",
    "hinge_loss",
    "get_loss_function",
]
