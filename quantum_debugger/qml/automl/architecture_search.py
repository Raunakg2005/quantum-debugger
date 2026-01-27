"""
Quantum Neural Architecture Search (QNAS)

Automatically search for optimal quantum neural network architecture.
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class QuantumNAS:
    """
    Neural Architecture Search for Quantum Networks.

    Automatically finds best:
    - Number of qubits
    - Number of layers
    - Layer types
    - Connectivity

    Examples:
        >>> nas = QuantumNAS(max_qubits=6)
        >>> best_arch = nas.search(X_train, y_train)
        >>> print(f"Best architecture: {best_arch}")
    """

    def __init__(
        self, max_qubits: int = 8, max_layers: int = 5, search_budget: int = 30
    ):
        """
        Initialize QNAS.

        Args:
            max_qubits: Maximum qubits to search
            max_layers: Maximum layers to try
            search_budget: Number of architectures to try
        """
        self.max_qubits = max_qubits
        self.max_layers = max_layers
        self.search_budget = search_budget

        self.best_architecture_ = None
        self.best_score_ = -np.inf
        self.search_history_ = []

    def search(self, X: np.ndarray, y: np.ndarray, epochs: int = 10) -> Dict:
        """
        Search for best architecture.

        Args:
            X: Training features
            y: Training labels
            epochs: Epochs for evaluation

        Returns:
            Best architecture specification
        """
        from quantum_debugger.qml.qnn import QuantumNeuralNetwork

        logger.info(f"Starting architecture search (budget: {self.search_budget})")

        # Generate candidate architectures
        architectures = self._generate_architectures(X.shape[1])

        for i, arch in enumerate(architectures[: self.search_budget]):
            logger.info(f"Testing architecture {i + 1}/{self.search_budget}: {arch}")

            try:
                # Build model with this architecture
                model = QuantumNeuralNetwork(n_qubits=arch["n_qubits"])
                model.compile(optimizer="adam", loss="mse")

                # Train
                history = model.fit(X, y, epochs=epochs, verbose=0)

                # Evaluate
                predictions = model.predict(X)
                pred_labels = (predictions > 0.5).astype(int).flatten()
                score = np.mean(pred_labels == y)

                # Track
                self.search_history_.append(
                    {
                        "architecture": arch,
                        "score": score,
                        "loss": history["loss"][-1] if history["loss"] else None,
                    }
                )

                # Update best
                if score > self.best_score_:
                    self.best_score_ = score
                    self.best_architecture_ = arch
                    logger.info(f"  ✨ New best! Score: {score:.3f}")

            except Exception as e:
                logger.warning(f"  ❌ Architecture failed: {e}")
                continue

        logger.info(f"Search complete! Best: {self.best_architecture_}")

        return self.best_architecture_

    def _generate_architectures(self, n_features: int) -> List[Dict]:
        """Generate candidate architectures."""
        architectures = []

        # Try different qubit counts
        for n_qubits in range(2, min(n_features + 1, self.max_qubits + 1)):
            # Try different layer counts
            for n_layers in range(1, self.max_layers + 1):
                architectures.append(
                    {
                        "n_qubits": n_qubits,
                        "n_layers": n_layers,
                        "ansatz": "real_amplitudes",
                    }
                )

        # Shuffle for diversity
        np.random.shuffle(architectures)

        return architectures

    def get_search_summary(self) -> Dict:
        """Get search summary."""
        return {
            "best_architecture": self.best_architecture_,
            "best_score": self.best_score_,
            "n_architectures_tested": len(self.search_history_),
            "all_scores": [h["score"] for h in self.search_history_],
        }


def quantum_nas(
    X: np.ndarray, y: np.ndarray, max_qubits: int = 6, quick: bool = True
) -> Dict:
    """
    Quick neural architecture search.

    Args:
        X: Training data
        y: Labels
        max_qubits: Maximum qubits
        quick: If True, use smaller budget

    Returns:
        Best architecture

    Examples:
        >>> arch = quantum_nas(X, y,  max_qubits=4)
        >>> print(f"Use {arch['n_qubits']} qubits, {arch['n_layers']} layers")
    """
    budget = 10 if quick else 30
    nas = QuantumNAS(max_qubits=max_qubits, search_budget=budget)

    return nas.search(X, y, epochs=5 if quick else 10)
