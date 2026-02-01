"""
Basic Optimizers for Quantum Machine Learning
"""

import numpy as np


class GradientDescent:
    """
    Vanilla Gradient Descent optimizer.
    """

    def __init__(self, learning_rate: float = 0.01):
        """
        Initialize Gradient Descent optimizer.

        Args:
            learning_rate: Step size for parameter updates
        """
        self.learning_rate = learning_rate

    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """
        Perform one optimization step.

        Args:
            params: Current parameters
            gradients: Gradient vector

        Returns:
            Updated parameters
        """
        return params - self.learning_rate * gradients


class Adam:
    """
    Adam optimizer.

    Adaptive Moment Estimation (Adam) computes adaptive learning rates
    for each parameter.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
    ):
        """
        Initialize Adam optimizer.

        Args:
            learning_rate: Step size
            beta1: Exponential decay rate for first moment estimates
            beta2: Exponential decay rate for second moment estimates
            epsilon: Small constant for numerical stability
        """
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = None  # First moment estimate
        self.v = None  # Second moment estimate
        self.t = 0     # Time step

    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """
        Perform one Adam optimization step.

        Args:
            params: Current parameters
            gradients: Gradient vector

        Returns:
            Updated parameters
        """
        if self.m is None:
            self.m = np.zeros_like(params)
            self.v = np.zeros_like(params)

        self.t += 1

        # Update biased first moment estimate
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients

        # Update biased second raw moment estimate
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradients ** 2)

        # Compute bias-corrected first moment estimate
        m_hat = self.m / (1 - self.beta1 ** self.t)

        # Compute bias-corrected second raw moment estimate
        v_hat = self.v / (1 - self.beta2 ** self.t)

        # Update parameters
        return params - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
