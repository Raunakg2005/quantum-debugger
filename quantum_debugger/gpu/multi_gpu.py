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
    """
    Base class for distributed QNN.

    The default behaviour genuinely trains the wrapped QNN (single-device). True
    multi-device distribution requires a GPU backend (CuPy + multiple GPUs); when
    that is unavailable, training falls back to one device and produces the same
    trained model rather than raising or silently doing nothing.
    """

    def __init__(self, qnn: Any, gpu_ids: List[int]):
        """Initialize distributed QNN."""
        self.qnn = qnn
        self.gpu_ids = gpu_ids
        self.n_gpus = max(1, len(gpu_ids))

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Train the wrapped QNN (single-device fallback)."""
        self.qnn.fit(X, y, **kwargs)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with the wrapped QNN."""
        return self.qnn.predict(X)


class DataParallelQNN(DistributedQNN):
    """
    Data parallel training across GPUs.

    Splits batches across GPUs, aggregates gradients.
    """

    def __init__(self, qnn: Any, gpu_ids: List[int]):
        """Initialize data parallel QNN."""
        super().__init__(qnn, gpu_ids)

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

        Each mini-batch is split into ``n_gpus`` shards; a gradient is computed
        per shard and the shard gradients are averaged before the optimizer step
        -- exactly the data-parallel algorithm. On a single device the shards run
        sequentially (no wall-clock speedup), but the result is a genuinely
        trained model; with a real multi-GPU backend the shards would run
        concurrently. This uses the wrapped QNN's real gradient and optimizer,
        unlike the previous version which called methods that do not exist on the
        QNN and therefore trained nothing.

        Args:
            X: Training data
            y: Training labels
            epochs: Number of epochs
            batch_size: Total batch size (split across shards)
        """
        qnn = self.qnn
        if not getattr(qnn, "compiled", False):
            qnn.compile()

        params = qnn._initialize_all_parameters()
        optimizer = qnn._make_optimizer()
        n_samples = len(X)

        for epoch in range(epochs):
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            epoch_loss = 0.0
            n_batches = 0

            for i in range(0, n_samples, batch_size):
                bx = X_shuffled[i : i + batch_size]
                by = y_shuffled[i : i + batch_size]
                if len(bx) == 0:
                    continue

                # Data-parallel: shard the batch, average per-shard gradients.
                shard_x = np.array_split(bx, self.n_gpus)
                shard_y = np.array_split(by, self.n_gpus)
                shard_grads = []
                for sx, sy in zip(shard_x, shard_y):
                    if len(sx) == 0:
                        continue
                    shard_grads.append(qnn._compute_gradient(params, sx, sy))

                if shard_grads:
                    avg_grad = np.mean(shard_grads, axis=0)
                    params = optimizer.step(params, avg_grad)
                    epoch_loss += qnn.compute_loss(params, bx, by)
                    n_batches += 1

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch + 1}/{epochs}: Loss={epoch_loss / max(n_batches, 1):.4f}"
                )

        qnn._parameters = params
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with the trained QNN."""
        return self.qnn.predict(X)


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
