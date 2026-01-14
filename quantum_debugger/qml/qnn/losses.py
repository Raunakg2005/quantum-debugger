"""
Loss Functions for Quantum Neural Networks
"""

import numpy as np
from typing import Callable


def mean_squared_error(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Mean Squared Error loss function.

    Args:
        predictions: Predicted values
        targets: True target values

    Returns:
        MSE loss
    """
    return np.mean((predictions - targets) ** 2)


def mean_absolute_error(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Mean Absolute Error loss function.

    Args:
        predictions: Predicted values
        targets: True target values

    Returns:
        MAE loss
    """
    return np.mean(np.abs(predictions - targets))


def binary_crossentropy(
    predictions: np.ndarray, targets: np.ndarray, epsilon: float = 1e-7
) -> float:
    """
    Binary cross-entropy loss.

    Args:
        predictions: Predicted probabilities
        targets: True labels (0 or 1)
        epsilon: Small constant to avoid log(0)

    Returns:
        Binary cross-entropy loss
    """
    # Clip predictions to avoid log(0)
    predictions = np.clip(predictions, epsilon, 1 - epsilon)

    return -np.mean(
        targets * np.log(predictions) + (1 - targets) * np.log(1 - predictions)
    )


def categorical_crossentropy(
    predictions: np.ndarray, targets: np.ndarray, epsilon: float = 1e-7
) -> float:
    """
    Categorical cross-entropy loss.

    Args:
        predictions: Predicted class probabilities (N × C)
        targets: True labels as one-hot vectors (N × C)
        epsilon: Small constant to avoid log(0)

    Returns:
        Categorical cross-entropy loss
    """
    predictions = np.clip(predictions, epsilon, 1 - epsilon)
    return -np.mean(np.sum(targets * np.log(predictions), axis=1))


def hinge_loss(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Hinge loss for SVM-style classification.

    Args:
        predictions: Predicted values
        targets: True labels (-1 or +1)

    Returns:
        Hinge loss
    """
    return np.mean(np.maximum(0, 1 - targets * predictions))


def get_loss_function(name: str) -> Callable:
    """
    Get loss function by name.

    Args:
        name: Loss function name

    Returns:
        Loss function
    """
    losses = {
        "mse": mean_squared_error,
        "mean_squared_error": mean_squared_error,
        "mae": mean_absolute_error,
        "mean_absolute_error": mean_absolute_error,
        "binary_crossentropy": binary_crossentropy,
        "categorical_crossentropy": categorical_crossentropy,
        "hinge": hinge_loss,
    }

    name = name.lower()
    if name not in losses:
        raise ValueError(f"Unknown loss function: {name}")

    return losses[name]
