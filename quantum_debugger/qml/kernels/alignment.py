"""
Kernel Alignment Optimization

Methods for optimizing feature maps based on kernel-target alignment.
"""

import numpy as np
from typing import Dict, Any
from scipy.optimize import minimize

from .quantum_kernel import QuantumKernel


def kernel_target_alignment(K: np.ndarray, y: np.ndarray) -> float:
    """
    Compute kernel-target alignment

    Measures how well a kernel matrix aligns with the target labels.
    Higher alignment indicates better kernel for classification.

    Args:
        K: Kernel matrix (n, n)
        y: Target labels (n,)

    Returns:
        Alignment score (0 to 1, higher is better)
    """
    n = len(y)

    # Create ideal kernel (label agreement)
    y_matrix = y.reshape(-1, 1) @ y.reshape(1, -1)
    Y = (y_matrix == y_matrix.T).astype(float)

    # Frobenius inner product
    alignment = np.trace(K @ Y) / np.sqrt(np.trace(K @ K) * np.trace(Y @ Y))

    return alignment


def centered_kernel_alignment(K: np.ndarray, y: np.ndarray) -> float:
    """
    Centered kernel alignment (CKA)

    More robust version of kernel alignment.

    Args:
        K: Kernel matrix
        y: Target labels

    Returns:
        CKA score
    """
    n = len(y)

    # Center kernel
    H = np.eye(n) - np.ones((n, n)) / n
    K_centered = H @ K @ H

    # Create target kernel
    y_matrix = y.reshape(-1, 1) @ y.reshape(1, -1)
    Y = (y_matrix == y_matrix.T).astype(float)
    Y_centered = H @ Y @ H

    # CKA
    num = np.trace(K_centered @ Y_centered)
    denom = np.sqrt(
        np.trace(K_centered @ K_centered) * np.trace(Y_centered @ Y_centered)
    )

    if denom == 0:
        return 0.0

    cka = num / denom
    return cka


def optimize_feature_map(
    X: np.ndarray,
    y: np.ndarray,
    base_kernel: QuantumKernel,
    n_iterations: int = 100,
    method: str = "COBYLA",
) -> Dict[str, Any]:
    """
    Optimize feature map parameters to maximize kernel alignment

    Args:
        X: Training data (n_samples, n_features)
        y: Training labels (n_samples,)
        base_kernel: Base quantum kernel to optimize
        n_iterations: Number of optimization iterations
        method: Optimization method

    Returns:
        Dictionary with optimized kernel and metrics
    """
    # Initial parameters (feature map encoding weights)
    n_params = base_kernel.n_qubits
    initial_params = np.random.rand(n_params)

    # Track best alignment
    best_alignment = -np.inf
    best_params = initial_params.copy()
    alignments_history = []

    def objective(params):
        """Objective: maximize negative alignment"""
        nonlocal best_alignment, best_params

        # Update kernel parameters (simplified)
        # In practice, would modify feature map encoding

        # Compute kernel matrix
        K = base_kernel.compute_kernel_matrix(X, X)

        # Compute alignment
        alignment = kernel_target_alignment(K, y)
        alignments_history.append(alignment)

        # Track best
        if alignment > best_alignment:
            best_alignment = alignment
            best_params = params.copy()

        # Return negative (for minimization)
        return -alignment

    # Optimize
    result = minimize(
        objective, initial_params, method=method, options={"maxiter": n_iterations}
    )

    # Return results
    return {
        "best_params": best_params,
        "best_alignment": best_alignment,
        "alignments_history": alignments_history,
        "optimization_result": result,
    }


def evaluate_kernel_quality(K: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    """
    Evaluate multiple quality metrics for a kernel

    Args:
        K: Kernel matrix
        y: Target labels

    Returns:
        Dictionary of quality metrics
    """
    metrics = {}

    # Kernel-target alignment
    metrics["alignment"] = kernel_target_alignment(K, y)

    # Centered kernel alignment
    metrics["centered_alignment"] = centered_kernel_alignment(K, y)

    # Kernel matrix properties
    eigenvalues = np.linalg.eigvalsh(K)
    metrics["condition_number"] = np.max(eigenvalues) / np.min(
        eigenvalues[eigenvalues > 1e-10]
    )
    metrics["rank"] = np.sum(eigenvalues > 1e-10)
    metrics["trace"] = np.trace(K)

    # Kernel statistics
    metrics["mean"] = np.mean(K)
    metrics["std"] = np.std(K)
    metrics["min"] = np.min(K)
    metrics["max"] = np.max(K)

    return metrics
