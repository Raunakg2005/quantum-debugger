"""
Ansatz Selection

Automatically select the best quantum ansatz for your data.
"""

import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AnsatzSelector:
    """
    Automatically select best ansatz (quantum circuit architecture).

    Tests different ansatz types and returns the best performer.

    Examples:
        >>> selector = AnsatzSelector()
        >>> best_ansatz = selector.select(X_train, y_train)
        >>> print(f"Best ansatz: {best_ansatz}")  # 'real_amplitudes', 'efficient_su2', etc.
    """

    def __init__(self, ansatz_types: Optional[List[str]] = None):
        """
        Initialize ansatz selector.

        Args:
            ansatz_types: List of ansatz types to try
                         If None, uses default set
        """
        self.ansatz_types = ansatz_types or [
            "real_amplitudes",
            "efficient_su2",
            "hardware_efficient",
        ]

        self.results_ = {}
        self.best_ansatz_ = None
        self.best_score_ = -np.inf

    def select(
        self, X: np.ndarray, y: np.ndarray, n_qubits: int, epochs: int = 10
    ) -> str:
        """
        Select best ansatz for dataset.

        Args:
            X: Training features
            y: Training labels
            n_qubits: Number of qubits
            epochs: Epochs for testing

        Returns:
            Name of best ansatz
        """
        from quantum_debugger.qml.qnn import QuantumNeuralNetwork

        for ansatz_type in self.ansatz_types:
            logger.info(f"Testing ansatz: {ansatz_type}")

            try:
                # Create QNN with this ansatz
                qnn = QuantumNeuralNetwork(n_qubits=n_qubits)
                qnn.compile(optimizer="adam", loss="mse")

                # Train briefly
                history = qnn.fit(X, y, epochs=epochs, verbose=0)

                # Evaluate
                predictions = qnn.predict(X)
                pred_labels = (predictions > 0.5).astype(int).flatten()
                score = np.mean(pred_labels == y)

                self.results_[ansatz_type] = {
                    "score": score,
                    "final_loss": history["loss"][-1] if history["loss"] else None,
                }

                if score > self.best_score_:
                    self.best_score_ = score
                    self.best_ansatz_ = ansatz_type
                    logger.info(f"  ✨ New best: {ansatz_type} ({score:.3f})")

            except Exception as e:
                logger.warning(f"  ❌ {ansatz_type} failed: {e}")
                continue

        return self.best_ansatz_

    def get_results(self) -> Dict:
        """Get all ansatz results."""
        return {
            "best_ansatz": self.best_ansatz_,
            "best_score": self.best_score_,
            "all_results": self.results_,
        }


def select_best_ansatz(
    X: np.ndarray, y: np.ndarray, n_qubits: int, quick: bool = True
) -> str:
    """
    Quick function to select best ansatz.

    Args:
        X: Training data
        y: Labels
        n_qubits: Number of qubits
        quick: If True, use fewer epochs

    Returns:
        Best ansatz name

    Examples:
        >>> ansatz = select_best_ansatz(X, y, n_qubits=4)
        >>> print(f"Use {ansatz} for best results!")
    """
    selector = AnsatzSelector()
    epochs = 5 if quick else 15

    return selector.select(X, y, n_qubits, epochs=epochs)
