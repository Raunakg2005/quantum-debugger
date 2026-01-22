"""
Base classes for hybrid classical-quantum layers
"""

import numpy as np
from typing import List
from abc import ABC, abstractmethod


class HybridLayer(ABC):
    """Base class for hybrid quantum-classical layers"""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.trainable_params = []

    @abstractmethod
    def forward(self, inputs):
        """Forward pass through the layer"""
        pass

    @abstractmethod
    def backward(self, grad_output):
        """Backward pass for gradient computation"""
        pass

    def get_parameters(self):
        """Get trainable parameters"""
        return self.trainable_params

    def set_parameters(self, params):
        """Set trainable parameters"""
        self.trainable_params = params


class ClassicalPreprocessor(HybridLayer):
    """
    Classical neural network preprocessing before quantum layer

    Features:
    - Dense layers with activation
    - Batch normalization
    - Dropout for regularization
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_layers: List[int] = None,
        activation: str = "relu",
        use_batch_norm: bool = False,
        dropout_rate: float = 0.0,
        name: str = None,
    ):
        super().__init__(name)
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layers = hidden_layers or []
        self.activation = activation
        self.use_batch_norm = use_batch_norm
        self.dropout_rate = dropout_rate

        # Initialize weights and biases
        self.weights = []
        self.biases = []
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize layer weights using Xavier initialization"""
        layers = [self.input_dim] + self.hidden_layers + [self.output_dim]

        for i in range(len(layers) - 1):
            # Xavier/Glorot initialization
            limit = np.sqrt(6.0 / (layers[i] + layers[i + 1]))
            W = np.random.uniform(-limit, limit, (layers[i], layers[i + 1]))
            b = np.zeros(layers[i + 1])

            self.weights.append(W)
            self.biases.append(b)
            self.trainable_params.extend([W, b])

    def _activate(self, x):
        """Apply activation function"""
        if self.activation == "relu":
            return np.maximum(0, x)
        elif self.activation == "tanh":
            return np.tanh(x)
        elif self.activation == "sigmoid":
            return 1 / (1 + np.exp(-x))
        elif self.activation == "linear":
            return x
        else:
            raise ValueError(f"Unknown activation: {self.activation}")

    def forward(self, inputs):
        """
        Forward pass through classical layers

        Args:
            inputs: Input data (batch_size, input_dim)

        Returns:
            Processed features (batch_size, output_dim)
        """
        x = inputs

        for i, (W, b) in enumerate(zip(self.weights, self.biases)):
            # Linear transformation
            x = np.dot(x, W) + b

            # Activation (not on last layer)
            if i < len(self.weights) - 1:
                x = self._activate(x)

                # Dropout (training only)
                if self.dropout_rate > 0:
                    mask = np.random.binomial(1, 1 - self.dropout_rate, x.shape)
                    x = x * mask / (1 - self.dropout_rate)

        return x

    def backward(self, grad_output):
        """
        Backward pass for gradient computation

        Args:
            grad_output: Gradient from next layer

        Returns:
            Gradient for previous layer
        """
        # Simplified backward pass
        # Full implementation would store activations and compute exact gradients
        return grad_output


class QuantumMiddleLayer(HybridLayer):
    """
    Quantum processing layer in hybrid model

    Encodes classical data into quantum states,
    applies variational circuit, and measures.
    """

    def __init__(
        self,
        n_qubits: int,
        encoding_type: str = "angle",
        ansatz_type: str = "real_amplitudes",
        ansatz_reps: int = 2,
        measurement_basis: str = "computational",
        name: str = None,
    ):
        super().__init__(name)
        self.n_qubits = n_qubits
        self.encoding_type = encoding_type
        self.ansatz_type = ansatz_type
        self.ansatz_reps = ansatz_reps
        self.measurement_basis = measurement_basis

        # Will be populated with quantum circuit parameters
        self._initialize_quantum_params()

    def _initialize_quantum_params(self):
        """Initialize quantum circuit parameters"""
        # Number of parameters depends on ansatz
        if self.ansatz_type == "real_amplitudes":
            n_params = self.n_qubits * (self.ansatz_reps + 1)
        elif self.ansatz_type == "strongly_entangling":
            n_params = 3 * self.n_qubits * self.ansatz_reps
        else:
            n_params = self.n_qubits * self.ansatz_reps

        # Random initialization between 0 and 2π
        self.quantum_params = np.random.uniform(0, 2 * np.pi, n_params)
        self.trainable_params = [self.quantum_params]

    def encode_data(self, classical_data):
        """
        Encode classical data into quantum state

        Args:
            classical_data: Classical features (must match n_qubits)

        Returns:
            Encoded quantum state
        """
        if self.encoding_type == "angle":
            # Angle encoding: RY(x_i) on each qubit
            return classical_data % (2 * np.pi)
        elif self.encoding_type == "amplitude":
            # Amplitude encoding: normalize to quantum state
            norm = np.linalg.norm(classical_data)
            return classical_data / norm if norm > 0 else classical_data
        else:
            return classical_data

    def forward(self, inputs):
        """
        Forward pass through quantum layer

        Args:
            inputs: Classical features (batch_size, n_qubits)

        Returns:
            Quantum measurement outcomes (batch_size, n_qubits)
        """
        batch_size = inputs.shape[0]
        outputs = np.zeros((batch_size, self.n_qubits))

        for i, sample in enumerate(inputs):
            # Encode data
            encoded = self.encode_data(sample[: self.n_qubits])

            # Simulate quantum circuit (simplified)
            # In practice, this would use the actual quantum simulator
            # For now, apply simple transformation
            processed = np.cos(encoded + self.quantum_params[: self.n_qubits])

            outputs[i] = processed

        return outputs

    def backward(self, grad_output):
        """
        Backward pass using parameter shift rule

        Args:
            grad_output: Gradient from next layer

        Returns:
            Gradient for previous layer
        """
        # Parameter shift rule for quantum gradients
        # Simplified implementation
        return grad_output


class ClassicalPostprocessor(HybridLayer):
    """
    Classical neural network after quantum layer

    Features:
    - Dense layers
    - Softmax for classification
    - Linear output for regression
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_layers: List[int] = None,
        output_activation: str = "softmax",
        name: str = None,
    ):
        super().__init__(name)
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layers = hidden_layers or []
        self.output_activation = output_activation

        # Initialize weights
        self.weights = []
        self.biases = []
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize weights"""
        layers = [self.input_dim] + self.hidden_layers + [self.output_dim]

        for i in range(len(layers) - 1):
            limit = np.sqrt(6.0 / (layers[i] + layers[i + 1]))
            W = np.random.uniform(-limit, limit, (layers[i], layers[i + 1]))
            b = np.zeros(layers[i + 1])

            self.weights.append(W)
            self.biases.append(b)
            self.trainable_params.extend([W, b])

    def forward(self, inputs):
        """
        Forward pass through postprocessing layers

        Args:
            inputs: Quantum measurement outcomes

        Returns:
            Final predictions
        """
        x = inputs

        for i, (W, b) in enumerate(zip(self.weights, self.biases)):
            x = np.dot(x, W) + b

            # Activation on last layer only
            if i == len(self.weights) - 1:
                if self.output_activation == "softmax":
                    # Softmax for classification
                    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
                    x = exp_x / np.sum(exp_x, axis=-1, keepdims=True)
                elif self.output_activation == "sigmoid":
                    x = 1 / (1 + np.exp(-x))
                # Linear output for regression (no activation)
            else:
                # ReLU for hidden layers
                x = np.maximum(0, x)

        return x

    def backward(self, grad_output):
        """Backward pass"""
        return grad_output
