"""
Pre-trained Quantum Neural Network

Wraps trained QNN models for easy loading, inference, and fine-tuning.
"""

import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PretrainedQNN:
    """
    Pre-trained quantum neural network model.

    Provides a consistent interface for loading pre-trained models,
    running inference, and fine-tuning on new data.

    Attributes:
        model_name: Unique identifier for the model
        dataset: Name of training dataset
        n_qubits: Number of qubits in the model
        n_layers: Number of circuit layers
        architecture: Model architecture configuration
        weights: Trained quantum circuit parameters
        metadata: Additional training information

    Examples:
        >>> from quantum_debugger.qml.transfer import load_pretrained
        >>> model = load_pretrained('mnist_qnn')
        >>> predictions = model.predict(X_test)
        >>> accuracy = model.score(X_test, y_test)
    """

    def __init__(
        self,
        model_name: str,
        config: Dict[str, Any],
        weights: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize pre-trained QNN.

        Args:
            model_name: Unique model identifier
            config: Model configuration dict with keys:
                - n_qubits: Number of qubits
                - n_layers: Number of circuit layers
                - ansatz_type: Type of ansatz
                - measurement: Measurement strategy
            weights: Trained parameter array
            metadata: Optional metadata dict with:
                - dataset: Training dataset name
                - accuracy: Model accuracy
                - epochs: Training epochs
                - date_trained: Training date
        """
        self.model_name = model_name
        self.config = config
        self.weights = weights
        self.metadata = metadata or {}

        # Extract common config values
        self.n_qubits = config.get("n_qubits", 4)
        self.n_layers = config.get("n_layers", 2)
        self.ansatz_type = config.get("ansatz_type", "real_amplitudes")

        # Build QNN from config
        self._build_model()

        logger.info(
            f"Loaded pre-trained model '{model_name}' "
            f"({self.n_qubits} qubits, {self.n_layers} layers)"
        )

    def _build_model(self):
        """Build QNN model from configuration."""
        from ..qnn import QuantumNeuralNetwork

        # Create QNN with just n_qubits (layers are added via .add() method)
        self.model = QuantumNeuralNetwork(n_qubits=self.n_qubits)

        # Compile the model (required before training/prediction)
        self.model.compile(optimizer="adam", loss="mse")

        # Set trained parameters (QNN uses _parameters internally)
        self.model._parameters = self.weights
        self.model.weights = self.weights  # Also set weights for compatibility

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Run inference on input data.

        Args:
            X: Input data (n_samples, n_features)

        Returns:
            Predictions (n_samples,) for classification
        """
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Input data

        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        else:
            # Binary classification fallback
            probs = self.model.forward(X)
            return np.column_stack([1 - probs, probs])

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Compute accuracy on test data.

        Args:
            X: Test features
            y: True labels

        Returns:
            Accuracy score (0 to 1)
        """
        predictions = self.predict(X)
        accuracy = np.mean(predictions == y)
        return accuracy

    def fine_tune(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        epochs: int = 10,
        learning_rate: float = 0.01,
        freeze_layers: Optional[list] = None,
        batch_size: int = 32,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Fine-tune model on new data.

        Args:
            X_train: Training features
            y_train: Training labels
            epochs: Number of training epochs
            learning_rate: Learning rate for optimization
            freeze_layers: Indices of layers to freeze (not update)
            batch_size: Batch size for training
            verbose: Print training progress

        Returns:
            Training history dict with 'loss' and 'accuracy'
        """
        logger.info(f"Fine-tuning '{self.model_name}' for {epochs} epochs...")

        # Train the model (QNN.fit doesn't take learning_rate directly)
        history = self.model.fit(
            X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
        )

        # Update weights
        self.weights = self.model.weights

        # Update metadata
        self.metadata["fine_tuned"] = True
        self.metadata["fine_tune_epochs"] = epochs

        logger.info(f"Fine-tuning complete. Final loss: {history['loss'][-1]:.4f}")

        return history

    def save(self, path: str, format: str = "pickle"):
        """
        Save model to disk.

        Args:
            path: File path to save to
            format: Serialization format ('pickle', 'json', 'hdf5')
        """
        from .serialization import save_model

        save_model(self, path, format=format)
        logger.info(f"Saved model to {path} (format: {format})")

    @classmethod
    def load(cls, path: str, format: str = "pickle") -> "PretrainedQNN":
        """
        Load model from disk.

        Args:
            path: File path to load from
            format: Serialization format

        Returns:
            Loaded PretrainedQNN instance
        """
        from .serialization import load_model

        model = load_model(path, format=format)
        logger.info(f"Loaded model from {path}")
        return model

    @classmethod
    def from_qnn(
        cls,
        qnn,
        model_name: str,
        dataset: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "PretrainedQNN":
        """
        Create PretrainedQNN from trained QNN instance.

        Args:
            qnn: Trained QuantumNeuralNetwork instance
            model_name: Name for the pre-trained model
            dataset: Dataset name
            metadata: Optional additional metadata

        Returns:
            PretrainedQNN instance
        """
        config = {
            "n_qubits": qnn.n_qubits,
            "n_layers": len(qnn.layers),  # Count layers instead
            "ansatz_type": getattr(qnn, "ansatz_type", "real_amplitudes"),
        }

        meta = metadata or {}
        meta["dataset"] = dataset

        # Get weights from QNN (use _parameters if weights doesn't exist)
        weights = getattr(qnn, "weights", getattr(qnn, "_parameters", np.array([])))

        return cls(model_name=model_name, config=config, weights=weights, metadata=meta)

    def get_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Dictionary with model details
        """
        return {
            "model_name": self.model_name,
            "n_qubits": self.n_qubits,
            "n_layers": self.n_layers,
            "ansatz_type": self.ansatz_type,
            "n_parameters": len(self.weights),
            "dataset": self.metadata.get("dataset", "Unknown"),
            "accuracy": self.metadata.get("accuracy", None),
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        dataset = self.metadata.get("dataset", "Unknown")
        acc = self.metadata.get("accuracy", "N/A")
        return (
            f"PretrainedQNN(name='{self.model_name}', "
            f"dataset='{dataset}', "
            f"qubits={self.n_qubits}, "
            f"accuracy={acc})"
        )
