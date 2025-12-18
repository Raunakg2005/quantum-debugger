"""
Gradient Computation Utilities
==============================

Methods for computing gradients of quantum circuits.
"""

import numpy as np
from typing import Callable, List


def parameter_shift_gradient(
    circuit_builder: Callable,
    cost_function: Callable,
    params: np.ndarray,
    param_index: int,
    shift: float = np.pi / 2
) -> float:
    """
    Compute gradient using parameter shift rule.
    
    For a gate U(θ) = exp(-iθG/2), the gradient is:
    ∂f/∂θ = [f(θ + π/2) - f(θ - π/2)] / 2
    
    where f is the cost function.
    
    Args:
        circuit_builder: Function that builds circuit from parameters
        cost_function: Function that evaluates cost from circuit
        params: Current parameter values
        param_index: Index of parameter to differentiate
        shift: Shift amount (default π/2 for standard gates)
        
    Returns:
        Gradient value ∂f/∂θᵢ
        
    Examples:
        >>> def circuit(p): return build_circuit(p)
        >>> def cost(c): return evaluate_energy(c)
        >>> grad = parameter_shift_gradient(circuit, cost, params, 0)
    """
    # Shift parameter forward
    params_plus = params.copy()
    params_plus[param_index] += shift
    
    # Shift parameter backward
    params_minus = params.copy()
    params_minus[param_index] -= shift
    
    # Evaluate cost at both points
    cost_plus = cost_function(circuit_builder(params_plus))
    cost_minus = cost_function(circuit_builder(params_minus))
    
    # Compute gradient
    gradient = (cost_plus - cost_minus) / 2
    
    return gradient


def finite_difference_gradient(
    cost_function: Callable,
    params: np.ndarray,
    param_index: int,
    epsilon: float = 1e-7
) -> float:
    """
    Compute gradient using finite differences.
    
    ∂f/∂θ ≈ [f(θ + ε) - f(θ)] / ε
    
    Less accurate than parameter shift but works for any function.
    
    Args:
        cost_function: Function to differentiate
        params: Current parameters
        param_index: Parameter to differentiate
        epsilon: Small perturbation
        
    Returns:
        Approximate gradient
    """
    params_shifted = params.copy()
    params_shifted[param_index] += epsilon
    
    cost_original = cost_function(params)
    cost_shifted = cost_function(params_shifted)
    
    gradient = (cost_shifted - cost_original) / epsilon
    
    return gradient


def compute_gradients(
    circuit_builder: Callable,
    cost_function: Callable,
    params: np.ndarray,
    method: str = 'parameter_shift'
) -> np.ndarray:
    """
    Compute all gradients for a parameter vector.
    
    Args:
        circuit_builder: Circuit builder function
        cost_function: Cost function
        params: Parameters
        method: 'parameter_shift' or 'finite_difference'
        
    Returns:
        Gradient vector ∇f
    """
    gradients = np.zeros_like(params)
    
    for i in range(len(params)):
        if method == 'parameter_shift':
            gradients[i] = parameter_shift_gradient(
                circuit_builder, cost_function, params, i
            )
        elif method == 'finite_difference':
            gradients[i] = finite_difference_gradient(
                cost_function, params, i
            )
        else:
            raise ValueError(f"Unknown gradient method: {method}")
    
    return gradients


def gradient_descent_step(
    params: np.ndarray,
    gradients: np.ndarray,
    learning_rate: float
) -> np.ndarray:
    """
    Perform one gradient descent step.
    
    θ_new = θ_old - η * ∇f
    
    Args:
        params: Current parameters
        gradients: Gradient vector
        learning_rate: Step size η
        
    Returns:
        Updated parameters
    """
    return params - learning_rate * gradients
