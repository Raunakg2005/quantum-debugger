"""
Quantum Neural Network Implementation

Main QNN class for building and training quantum neural networks.
"""

import numpy as np
from typing import List, Optional, Dict, Tuple
from .base import QNNLayer
from .losses import get_loss_function
from ...core.circuit import QuantumCircuit


class QuantumNeuralNetwork:
    """
    Quantum Neural Network with layer-based architecture.

    Supports encoding layers, variational layers, and training
    on multi-sample datasets.
    """

    def __init__(self, n_qubits: int):
        """
        Initialize Quantum Neural Network.

        Args:
            n_qubits: Number of qubits in the network
        """
        self.n_qubits = n_qubits
        self.layers: List[QNNLayer] = []
        self.optimizer = None
        self.loss_fn = None
        self.compiled = False
        self.history = {"loss": [], "val_loss": []}

    def add(self, layer: QNNLayer):
        """
        Add a layer to the network.

        Args:
            layer: QNN layer to add
        """
        if layer.n_qubits != self.n_qubits:
            raise ValueError(
                f"Layer has {layer.n_qubits} qubits, network expects {self.n_qubits}"
            )

        self.layers.append(layer)

    @property
    def num_parameters(self) -> int:
        """Total number of trainable parameters"""
        return sum(layer.num_parameters for layer in self.layers)

    def compile(
        self,
        optimizer: str = "adam",
        loss: str = "mse",
        learning_rate: float = 0.01,
        **kwargs,
    ):
        """
        Compile the network for training.

        Args:
            optimizer: Optimizer name ('adam', 'sgd', 'lbfgs', 'nelder-mead', etc.)
            loss: Loss function name
            learning_rate: Learning rate
            **kwargs: Additional optimizer arguments
        """
        # Simple optimizer handling - store config for use in fit()
        self.optimizer_name = optimizer
        self.learning_rate = learning_rate
        self.optimizer_kwargs = kwargs

        # Get loss function
        self.loss_fn = get_loss_function(loss)
        self.compiled = True

    def build_circuit(self, params: np.ndarray, data: np.ndarray) -> QuantumCircuit:
        """
        Build complete circuit for one data sample.

        Args:
            params: All trainable parameters
            data: Input data for encoding layer

        Returns:
            Complete quantum circuit
        """
        circuit = QuantumCircuit(self.n_qubits)
        param_idx = 0

        for layer in self.layers:
            if layer.num_parameters > 0:
                # Variational layer with parameters
                layer_params = params[param_idx:param_idx + layer.num_parameters]
                layer_circuit = layer.build_circuit(params=layer_params)
                param_idx += layer.num_parameters
            else:
                # Encoding layer with data
                layer_circuit = layer.build_circuit(data=data)

            # Append gates to main circuit
            for gate in layer_circuit.gates:
                circuit.gates.append(gate)

        return circuit

    def forward(self, params: np.ndarray, X: np.ndarray) -> np.ndarray:
        """
        Forward pass through the network.

        Args:
            params: Network parameters
            X: Input data (N samples × D features)

        Returns:
            Predictions (N samples)
        """
        predictions = []

        for sample in X:
            # Build circuit for this sample
            circuit = self.build_circuit(params, sample)

            # Get final state vector
            state = circuit.get_statevector()

            # Measure expectation value (use Z measurement on all qubits)
            expectation = self._compute_expectation(state.state_vector)
            predictions.append(expectation)

        return np.array(predictions)

    def _compute_expectation(self, state: np.ndarray) -> float:
        """
        Compute expectation value from quantum state.

        Args:
            state: Quantum state vector

        Returns:
            Expectation value
        """
        # Simple measurement: probability of |0...0⟩ - probability of |1...1⟩
        prob_zero = np.abs(state[0]) ** 2
        prob_one = np.abs(state[-1]) ** 2
        return prob_zero - prob_one

    def compute_loss(self, params: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
        """
        Compute loss for given parameters.

        Args:
            params: Network parameters
            X: Input data
            y: Target labels

        Returns:
            Loss value
        """
        predictions = self.forward(params, X)
        return self.loss_fn(predictions, y)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 10,
        batch_size: Optional[int] = None,
        validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        verbose: int = 1,
    ) -> Dict[str, List[float]]:
        """
        Train the network.

        Args:
            X: Training data (N samples × D features)
            y: Training labels (N samples)
            epochs: Number of training epochs
            batch_size: Batch size (None = full batch)
            validation_data: Optional (X_val, y_val) tuple
            verbose: Verbosity level (0 = silent, 1 = progress)

        Returns:
            Training history
        """
        if not self.compiled:
            raise RuntimeError("Network must be compiled before training")

        # Initialize parameters
        params = self._initialize_all_parameters()

        n_samples = len(X)
        if batch_size is None:
            batch_size = n_samples

        # Training loop
        for epoch in range(epochs):
            epoch_losses = []

            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            # Mini-batch training
            for i in range(0, n_samples, batch_size):
                batch_X = X_shuffled[i:i + batch_size]
                batch_y = y_shuffled[i:i + batch_size]

                # Compute loss
                loss = self.compute_loss(params, batch_X, batch_y)
                epoch_losses.append(loss)

                # Compute gradient (finite differences for now)
                gradient = self._compute_gradient(params, batch_X, batch_y)

                # Update parameters the optimizer (placeholder - needs proper integration)
                params = params - 0.01 * gradient

            # Average loss for epoch
            train_loss = np.mean(epoch_losses)
            self.history["loss"].append(train_loss)

            # Validation loss
            if validation_data is not None:
                X_val, y_val = validation_data
                val_loss = self.compute_loss(params, X_val, y_val)
                self.history["val_loss"].append(val_loss)

            # Print progress
            if verbose and epoch % max(1, epochs // 10) == 0:
                msg = f"Epoch {epoch + 1}/{epochs} - loss: {train_loss:.4f}"
                if validation_data is not None:
                    msg += f" - val_loss: {val_loss:.4f}"
                print(msg)

        # Store final parameters
        self._parameters = params

        return self.history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions on new data.

        Args:
            X: Input data (N samples × D features)

        Returns:
            Predictions (N samples)
        """
        if not hasattr(self, "_parameters"):
            raise RuntimeError("Network must be trained before prediction")

        return self.forward(self._parameters, X)

    def _initialize_all_parameters(self, method: str = "random") -> np.ndarray:
        """
        Initialize all network parameters.

        Args:
            method: Initialization method

        Returns:
            Initialized parameters
        """
        all_params = []

        for layer in self.layers:
            if layer.num_parameters > 0:
                params = layer.initialize_parameters(method)
                all_params.extend(params)

        return np.array(all_params)

    def _compute_gradient(
        self, params: np.ndarray, X: np.ndarray, y: np.ndarray, epsilon: float = 1e-4
    ) -> np.ndarray:
        """
        Compute gradient using finite differences.

        Args:
            params: Current parameters
            X: Input data
            y: Target labels
            epsilon: Finite difference step

        Returns:
            Gradient vector
        """
        gradient = np.zeros_like(params)

        for i in range(len(params)):
            # Forward difference
            params_plus = params.copy()
            params_plus[i] += epsilon

            loss_plus = self.compute_loss(params_plus, X, y)
            loss_current = self.compute_loss(params, X, y)

            gradient[i] = (loss_plus - loss_current) / epsilon

        return gradient

    def summary(self):
        """Print network architecture summary"""
        print("=" * 60)
        print(f"Quantum Neural Network ({self.n_qubits} qubits)")
        print("=" * 60)
        print(f"{'Layer':<30} {'Parameters':<15}")
        print("-" * 60)

        total_params = 0
        for i, layer in enumerate(self.layers):
            n_params = layer.num_parameters
            total_params += n_params
            print(f"{layer.name:<30} {n_params:<15}")

        print("=" * 60)
        print(f"Total parameters: {total_params}")
        print("=" * 60)

    def __repr__(self) -> str:
        return f"QuantumNeuralNetwork(qubits={self.n_qubits}, layers={len(self.layers)}, params={self.num_parameters})"
