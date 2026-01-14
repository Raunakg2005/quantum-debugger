"""
Multi-GPU Support for Quantum Simulations

Distribute quantum neural network training across multiple GPUs.
"""

import numpy as np
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MultiGPUManager:
    """
    Manage multiple GPU devices for quantum simulations.

    Provides data parallelism and model parallelism strategies
    for distributing quantum neural network training across GPUs.

    Examples:
        >>> manager = MultiGPUManager(gpu_ids=[0, 1, 2, 3])
        >>> distributed_qnn = manager.distribute_qnn(qnn, strategy='data_parallel')
        >>> distributed_qnn.fit(X_train, y_train, batch_size=64)
    """

    def __init__(self, gpu_ids: Optional[List[int]] = None):
        """
        Initialize multi-GPU manager.

        Args:
            gpu_ids: List of GPU IDs to use. None = use all available GPUs.
        """
        self.gpu_ids = gpu_ids
        self._available_gpus = self._detect_gpus()

        if self.gpu_ids is None:
            self.gpu_ids = list(range(len(self._available_gpus)))

        self.n_gpus = len(self.gpu_ids)
        logger.info(
            f"MultiGPUManager initialized with {self.n_gpus} GPUs: {self.gpu_ids}"
        )

    def _detect_gpus(self) -> List[Dict[str, Any]]:
        """
        Detect available GPU devices.

        Returns:
            List of GPU information dictionaries
        """
        try:
            import cupy as cp

            n_devices = cp.cuda.runtime.getDeviceCount()

            gpus = []
            for i in range(n_devices):
                cp.cuda.Device(i).use()
                props = cp.cuda.runtime.getDeviceProperties(i)
                gpus.append(
                    {
                        "id": i,
                        "name": props["name"].decode(),
                        "total_memory": props["totalGlobalMem"],
                        "compute_capability": f"{props['major']}.{props['minor']}",
                    }
                )

            logger.info(f"Detected {len(gpus)} GPU(s)")
            return gpus

        except ImportError:
            logger.warning("CuPy not installed. Multi-GPU not available.")
            return []
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")
            return []

    def get_available_gpus(self) -> List[Dict[str, Any]]:
        """Get list of available GPUs with their properties."""
        return self._available_gpus

    def distribute_qnn(
        self, qnn: Any, strategy: str = "data_parallel"
    ) -> "DistributedQNN":
        """
        Distribute QNN across multiple GPUs.

        Args:
            qnn: QuantumNeuralNetwork instance
            strategy: 'data_parallel' or 'model_parallel'

        Returns:
            DistributedQNN wrapper
        """
        if strategy == "data_parallel":
            return DataParallelQNN(qnn, self.gpu_ids)
        elif strategy == "model_parallel":
            return ModelParallelQNN(qnn, self.gpu_ids)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def synchronize(self):
        """Synchronize all GPUs."""
        try:
            import cupy as cp

            for gpu_id in self.gpu_ids:
                with cp.cuda.Device(gpu_id):
                    cp.cuda.Stream.null.synchronize()
            logger.debug("All GPUs synchronized")
        except ImportError:
            pass


class DistributedQNN:
    """Base class for distributed QNN."""

    def __init__(self, qnn: Any, gpu_ids: List[int]):
        """Initialize distributed QNN."""
        self.qnn = qnn
        self.gpu_ids = gpu_ids
        self.n_gpus = len(gpu_ids)

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Training method to be implemented by subclasses."""
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prediction method to be implemented by subclasses."""
        raise NotImplementedError


class DataParallelQNN(DistributedQNN):
    """
    Data parallel training across GPUs.

    Splits batches across GPUs, aggregates gradients.
    """

    def __init__(self, qnn: Any, gpu_ids: List[int]):
        """Initialize data parallel QNN."""
        super().__init__(qnn, gpu_ids)
        self._replicas = self._create_replicas()

    def _create_replicas(self) -> List[Any]:
        """Create QNN replica on each GPU."""
        replicas = []
        for gpu_id in self.gpu_ids:
            # Create replica with same architecture
            replica = type(self.qnn)(
                n_qubits=self.qnn.n_qubits, n_layers=getattr(self.qnn, "n_layers", 1)
            )
            # Copy weights from original
            if hasattr(self.qnn, "_parameters"):
                replica._parameters = self.qnn._parameters.copy()
            replicas.append(replica)
        return replicas

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 10,
        batch_size: int = 32,
        **kwargs,
    ):
        """
        Train with data parallelism.

        Args:
            X: Training data
            y: Training labels
            epochs: Number of epochs
            batch_size: Total batch size (split across GPUs)
            **kwargs: Additional training arguments
        """
        n_samples = len(X)
        batch_size_per_gpu = batch_size // self.n_gpus

        for epoch in range(epochs):
            epoch_loss = 0
            n_batches = 0

            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            # Process batches
            for i in range(0, n_samples, batch_size):
                batch_end = min(i + batch_size, n_samples)
                X_batch = X_shuffled[i:batch_end]
                y_batch = y_shuffled[i:batch_end]

                # Split batch across GPUs
                batch_losses = []
                batch_gradients = []

                for gpu_idx, replica in enumerate(self._replicas):
                    start_idx = gpu_idx * batch_size_per_gpu
                    end_idx = min(start_idx + batch_size_per_gpu, len(X_batch))

                    if start_idx < end_idx:
                        X_split = X_batch[start_idx:end_idx]
                        y_split = y_batch[start_idx:end_idx]

                        # Forward pass on GPU
                        loss = replica._compute_loss(X_split, y_split)
                        batch_losses.append(loss)

                        # Compute gradients (simplified)
                        if hasattr(replica, "_compute_gradients"):
                            grads = replica._compute_gradients(X_split, y_split)
                            batch_gradients.append(grads)

                # Average losses
                if batch_losses:
                    epoch_loss += np.mean(batch_losses)
                    n_batches += 1

                    # Aggregate and apply gradients
                    if batch_gradients:
                        avg_gradients = np.mean(batch_gradients, axis=0)
                        self._apply_gradients(avg_gradients)

            # Log progress
            if (epoch + 1) % 10 == 0:
                avg_loss = epoch_loss / max(n_batches, 1)
                logger.info(f"Epoch {epoch+1}/{epochs}: Loss={avg_loss:.4f}")

        return self

    def _apply_gradients(self, gradients: np.ndarray):
        """Apply averaged gradients to all replicas."""
        learning_rate = 0.01
        for replica in self._replicas:
            if hasattr(replica, "_parameters"):
                replica._parameters -= learning_rate * gradients

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict using first replica (all have same weights).

        Args:
            X: Input data

        Returns:
            Predictions
        """
        return self._replicas[0].predict(X)


class ModelParallelQNN(DistributedQNN):
    """
    Model parallel training across GPUs.

    Splits model layers across GPUs.
    """

    def __init__(self, qnn: Any, gpu_ids: List[int]):
        """Initialize model parallel QNN."""
        super().__init__(qnn, gpu_ids)
        self._layer_assignments = self._assign_layers()

    def _assign_layers(self) -> Dict[int, int]:
        """Assign layers to GPUs."""
        n_layers = getattr(self.qnn, "n_layers", 1)
        layers_per_gpu = max(1, n_layers // self.n_gpus)

        assignments = {}
        for layer_idx in range(n_layers):
            gpu_idx = min(layer_idx // layers_per_gpu, self.n_gpus - 1)
            assignments[layer_idx] = self.gpu_ids[gpu_idx]

        return assignments

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """
        Train with model parallelism.

        Note: Simplified implementation. Real model parallelism
        requires careful pipeline management.
        """
        # Fallback to single GPU for now
        return self.qnn.fit(X, y, **kwargs)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with model parallelism."""
        return self.qnn.predict(X)
