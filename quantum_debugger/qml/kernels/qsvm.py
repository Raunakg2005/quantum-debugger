"""
Quantum Support Vector Machine (QSVM)

Implements SVM with quantum kernels for classification.
"""

import numpy as np
from typing import Dict, Any
from sklearn.svm import SVC

from .quantum_kernel import FidelityKernel


class QuantumSVM:
    """
    Support Vector Machine with quantum kernel

    Uses quantum kernel to compute similarity between data points,
    then trains classical SVM with precomputed kernel matrix.

    Example:
        ```python
        from quantum_debugger.qml.kernels import QuantumSVM

        qsvm = QuantumSVM(n_qubits=4, feature_map='zz')
        qsvm.fit(X_train, y_train)
        predictions = qsvm.predict(X_test)
        accuracy = qsvm.score(X_test, y_test)
        ```
    """

    def __init__(
        self,
        n_qubits: int = 4,
        feature_map: str = "zz",
        kernel_type: str = "fidelity",
        reps: int = 2,
        C: float = 1.0,
        **svm_kwargs,
    ):
        """
        Initialize Quantum SVM

        Args:
            n_qubits: Number of qubits
            feature_map: Feature map type (zz, pauli, angle)
            kernel_type: Kernel type (fidelity, projected)
            reps: Number of feature map repetitions
            C: SVM regularization parameter
            **svm_kwargs: Additional arguments for sklearn SVC
        """
        self.n_qubits = n_qubits
        self.feature_map = feature_map
        self.kernel_type = kernel_type
        self.reps = reps
        self.C = C

        # Create quantum kernel
        if kernel_type == "fidelity":
            self.quantum_kernel = FidelityKernel(
                feature_map=feature_map, n_qubits=n_qubits, reps=reps
            )
        else:
            from .quantum_kernel import ProjectedKernel

            self.quantum_kernel = ProjectedKernel(
                feature_map=feature_map, n_qubits=n_qubits, reps=reps
            )

        # Create classical SVM with precomputed kernel
        self.svm = SVC(kernel="precomputed", C=C, **svm_kwargs)

        # Training data (needed for prediction)
        self.X_train = None
        self.y_train = None
        self.K_train = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Train QSVM on data

        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,)

        Returns:
            self
        """
        self.X_train = X
        self.y_train = y

        # Compute quantum kernel matrix
        print(f"Computing quantum kernel matrix ({len(X)}x{len(X)})...")
        self.K_train = self.quantum_kernel.compute_kernel_matrix(X, X)

        # Train SVM with precomputed kernel
        self.svm.fit(self.K_train, y)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for test data

        Args:
            X: Test features (n_samples, n_features)

        Returns:
            Predicted labels (n_samples,)
        """
        if self.X_train is None:
            raise ValueError("Model not trained. Call fit() first.")

        # Compute kernel matrix between test and train
        K_test = self.quantum_kernel.compute_kernel_matrix(X, self.X_train)

        # Predict using SVM
        predictions = self.svm.predict(K_test)

        return predictions

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities

        Args:
            X: Test features

        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not hasattr(self.svm, "predict_proba"):
            raise ValueError(
                "Probability prediction requires probability=True in constructor"
            )

        K_test = self.quantum_kernel.compute_kernel_matrix(X, self.X_train)
        return self.svm.predict_proba(K_test)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Compute accuracy on test data

        Args:
            X: Test features
            y: True labels

        Returns:
            Accuracy score
        """
        predictions = self.predict(X)
        accuracy = np.mean(predictions == y)
        return accuracy

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Compute decision function values

        Args:
            X: Test features

        Returns:
            Decision function values
        """
        K_test = self.quantum_kernel.compute_kernel_matrix(X, self.X_train)
        return self.svm.decision_function(K_test)

    def get_support_vectors(self) -> np.ndarray:
        """Get support vectors"""
        return self.X_train[self.svm.support_]

    def get_kernel_matrix(self) -> np.ndarray:
        """Get training kernel matrix"""
        return self.K_train


def train_qsvm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray = None,
    y_test: np.ndarray = None,
    n_qubits: int = 4,
    feature_map: str = "zz",
    C: float = 1.0,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to train QSVM

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features (optional)
        y_test: Test labels (optional)
        n_qubits: Number of qubits
        feature_map: Feature map type
        C: Regularization parameter
        **kwargs: Additional QSVM parameters

    Returns:
        Dictionary with model and metrics
    """
    # Create and train QSVM
    qsvm = QuantumSVM(n_qubits=n_qubits, feature_map=feature_map, C=C, **kwargs)

    qsvm.fit(X_train, y_train)

    # Compute metrics
    train_accuracy = qsvm.score(X_train, y_train)

    result = {"model": qsvm, "train_accuracy": train_accuracy}

    if X_test is not None and y_test is not None:
        test_accuracy = qsvm.score(X_test, y_test)
        result["test_accuracy"] = test_accuracy
        result["predictions"] = qsvm.predict(X_test)

    return result
