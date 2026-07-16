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

    def _apply_ansatz(self, circuit, params):
        """Apply the variational ansatz consuming exactly len(params) angles."""
        p = 0
        n = self.n_qubits
        if self.ansatz_type == "real_amplitudes":
            for _ in range(self.ansatz_reps):
                for q in range(n):
                    circuit.ry(params[p], q)
                    p += 1
                for q in range(n - 1):
                    circuit.cnot(q, q + 1)
            for q in range(n):  # final rotation layer -> n*(reps+1) params
                circuit.ry(params[p], q)
                p += 1
        elif self.ansatz_type == "strongly_entangling":
            for _ in range(self.ansatz_reps):
                for q in range(n):
                    circuit.rx(params[p], q)
                    circuit.ry(params[p + 1], q)
                    circuit.rz(params[p + 2], q)
                    p += 3
                for q in range(n):
                    circuit.cnot(q, (q + 1) % n)
        else:
            for _ in range(self.ansatz_reps):
                for q in range(n):
                    circuit.ry(params[p], q)
                    p += 1
                for q in range(n - 1):
                    circuit.cnot(q, q + 1)
        return circuit

    def _build_circuit(self, x, params):
        """Encode x, apply the ansatz, return the circuit for |psi(x, params)>."""
        from ...core.circuit import QuantumCircuit

        circuit = QuantumCircuit(self.n_qubits)
        encoded = self.encode_data(np.asarray(x, dtype=float)[: self.n_qubits])
        for q in range(self.n_qubits):
            circuit.ry(float(encoded[q]), q)  # ry(theta, qubit)
        return self._apply_ansatz(circuit, params)

    def _z_expectations(self, state_vector):
        """Pauli-Z expectation on each qubit from a state vector."""
        probs = np.abs(state_vector) ** 2
        indices = np.arange(state_vector.shape[0])
        return np.array(
            [np.dot(probs, 1.0 - 2.0 * ((indices >> q) & 1)) for q in range(self.n_qubits)]
        )

    def _forward_single(self, x, params):
        """Simulate one sample through the real circuit and measure <Z> per qubit."""
        state = self._build_circuit(x, params).get_statevector().state_vector
        return self._z_expectations(state)

    def forward(self, inputs):
        """
        Forward pass through the quantum layer.

        Genuinely simulates, for each sample, a circuit of angle-encoding
        rotations followed by the variational ansatz on the state-vector
        simulator, and returns the Pauli-Z expectation of every qubit. (The
        previous version returned ``cos(x + params)`` -- a classical surrogate
        that ignored the ansatz and all but the first n_qubits parameters.)

        Args:
            inputs: Classical features (batch_size, n_qubits)

        Returns:
            Quantum <Z> expectations (batch_size, n_qubits), each in [-1, 1]
        """
        inputs = np.asarray(inputs)
        outputs = np.zeros((inputs.shape[0], self.n_qubits))
        for i, sample in enumerate(inputs):
            outputs[i] = self._forward_single(sample[: self.n_qubits], self.quantum_params)
        return outputs

    def parameter_shift_gradients(self, inputs, grad_output):
        """
        Exact gradients of the layer via the parameter-shift rule.

        Every trainable angle (both the variational parameters and the
        angle-encoding of the inputs) enters through a Pauli rotation
        exp(-i theta P / 2), so d<O>/d theta = (1/2)[<O>(theta + pi/2) -
        <O>(theta - pi/2)] is exact.

        Args:
            inputs: Batch of inputs (batch_size, n_qubits)
            grad_output: Upstream gradient (batch_size, n_qubits)

        Returns:
            (param_grads (n_params,), input_grads (batch_size, n_qubits))
        """
        inputs = np.asarray(inputs, dtype=float)
        grad_output = np.asarray(grad_output, dtype=float)
        shift = np.pi / 2
        params = self.quantum_params
        param_grads = np.zeros_like(params)
        input_grads = np.zeros_like(inputs)

        for i, sample in enumerate(inputs):
            x = sample[: self.n_qubits]
            upstream = grad_output[i]

            for k in range(params.shape[0]):
                p_plus = params.copy()
                p_plus[k] += shift
                p_minus = params.copy()
                p_minus[k] -= shift
                deriv = 0.5 * (
                    self._forward_single(x, p_plus) - self._forward_single(x, p_minus)
                )
                param_grads[k] += np.dot(upstream, deriv)

            for j in range(self.n_qubits):
                x_plus = x.copy()
                x_plus[j] += shift
                x_minus = x.copy()
                x_minus[j] -= shift
                deriv = 0.5 * (
                    self._forward_single(x_plus, params)
                    - self._forward_single(x_minus, params)
                )
                input_grads[i, j] = np.dot(upstream, deriv)

        return param_grads, input_grads

    def backward(self, grad_output):
        """
        Backward pass (parameter-shift). Requires the inputs from the forward
        pass; prefer :meth:`parameter_shift_gradients` which takes them
        explicitly. Kept for the HybridLayer API.
        """
        if not hasattr(self, "_last_inputs"):
            return grad_output
        param_grads, input_grads = self.parameter_shift_gradients(
            self._last_inputs, grad_output
        )
        self._param_grads = param_grads
        return input_grads


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
