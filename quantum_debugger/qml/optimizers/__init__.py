"""
Optimizers for Quantum Machine Learning
=======================================

Classical optimizers for variational quantum algorithms.
"""

import numpy as np
from typing import Callable, Dict, Optional


class Optimizer:
    """Base class for optimizers"""
    
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.iteration = 0
    
    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """Perform one optimization step"""
        raise NotImplementedError


class GradientDescent(Optimizer):
    """
    Standard gradient descent optimizer.
    
    θ_new = θ_old - η * ∇f
    
    Examples:
        >>> opt = GradientDescent(learning_rate=0.1)
        >>> new_params = opt.step(params, gradients)
    """
    
    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """Gradient descent step"""
        self.iteration += 1
        return params - self.learning_rate * gradients


class Adam(Optimizer):
    """
    Adam optimizer (Adaptive Moment Estimation).
    
    Combines momentum and adaptive learning rates.
    
    Args:
        learning_rate: Step size (default 0.001)
        beta1: Exponential decay rate for first moment (default 0.9)
        beta2: Exponential decay rate for second moment (default 0.999)
        epsilon: Small constant for numerical stability (default 1e-8)
        
    Examples:
        >>> opt = Adam(learning_rate=0.01)
        >>> new_params = opt.step(params, gradients)
    """
    
    def __init__(
        self,
        learning_rate: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8
    ):
        super().__init__(learning_rate)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        
        # State variables
        self.m = None  # First moment
        self.v = None  # Second moment
    
    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """Adam optimization step"""
        # Initialize moments on first call
        if self.m is None:
            self.m = np.zeros_like(params)
            self.v = np.zeros_like(params)
        
        self.iteration += 1
        
        # Update biased first moment estimate
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients
        
        # Update biased second raw moment estimate
        self.v = self.beta2 * self.v + (1 - self.beta2) * gradients**2
        
        # Compute bias-corrected moments
        m_hat = self.m / (1 - self.beta1**self.iteration)
        v_hat = self.v / (1 - self.beta2**self.iteration)
        
        # Update parameters
        new_params = params - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
        
        return new_params


class SPSA(Optimizer):
    """
    SPSA (Simultaneous Perturbation Stochastic Approximation).
    
    Gradient-free optimizer good for noisy quantum hardware.
    Approximates gradient using random perturbations.
    
    Args:
        learning_rate: Step size
        perturbation: Size of random perturbation (default 0.1)
        
    Examples:
        >>> opt = SPSA(learning_rate=0.1)
        >>> new_params = opt.step_spsa(params, cost_function)
    """
    
    def __init__(self, learning_rate: float = 0.1, perturbation: float = 0.1):
        super().__init__(learning_rate)
        self.perturbation = perturbation
    
    def step_spsa(
        self,
        params: np.ndarray,
        cost_function: Callable
    ) -> np.ndarray:
        """
        SPSA step (requires cost function, not gradients).
        
        Args:
            params: Current parameters
            cost_function: Function to minimize
            
        Returns:
            Updated parameters
        """
        # Random perturbation direction
        delta = np.random.choice([-1, 1], size=len(params))
        
        # Evaluate at perturbed points
        params_plus = params + self.perturbation * delta
        params_minus = params - self.perturbation * delta
        
        cost_plus = cost_function(params_plus)
        cost_minus = cost_function(params_minus)
        
        # Approximate gradient
        gradient_approx = (cost_plus - cost_minus) / (2 * self.perturbation) * delta
        
        # Update
        self.iteration += 1
        return params - self.learning_rate * gradient_approx
    
    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """Standard step (for compatibility)"""
        self.iteration += 1
        return params - self.learning_rate * gradients


class RMSprop(Optimizer):
    """
    RMSprop optimizer.
    
    Adaptive learning rate method.
    
    Args:
        learning_rate: Step size
        decay_rate: Decay rate for moving average (default 0.9)
        epsilon: Small constant (default 1e-8)
    """
    
    def __init__(
        self,
        learning_rate: float = 0.001,
        decay_rate: float = 0.9,
        epsilon: float = 1e-8
    ):
        super().__init__(learning_rate)
        self.decay_rate = decay_rate
        self.epsilon = epsilon
        self.cache = None
    
    def step(self, params: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """RMSprop step"""
        if self.cache is None:
            self.cache = np.zeros_like(params)
        
        # Update cache
        self.cache = self.decay_rate * self.cache + (1 - self.decay_rate) * gradients**2
        
        # Update parameters
        self.iteration += 1
        return params - self.learning_rate * gradients / (np.sqrt(self.cache) + self.epsilon)


def get_optimizer(name: str, **kwargs) -> Optimizer:
    """
    Factory function to create optimizer by name.
    
    Args:
        name: Optimizer name ('adam', 'sgd', 'spsa', 'rmsprop')
        **kwargs: Optimizer-specific arguments
        
    Returns:
        Optimizer instance
        
    Examples:
        >>> opt = get_optimizer('adam', learning_rate=0.01)
    """
    optimizers = {
        'sgd': GradientDescent,
        'gd': GradientDescent,
        'adam': Adam,
        'spsa': SPSA,
        'rmsprop': RMSprop,
    }
    
    name_lower = name.lower()
    if name_lower not in optimizers:
        raise ValueError(f"Unknown optimizer: {name}. Choose from {list(optimizers.keys())}")
    
    return optimizers[name_lower](**kwargs)
