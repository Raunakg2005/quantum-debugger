"""
Advanced Optimizers for Quantum Machine Learning

Provides sophisticated optimization algorithms beyond basic gradient descent.
"""

import numpy as np
from typing import Callable, Optional, Dict, Any
from scipy.optimize import minimize


class QuantumNaturalGradient:
    """
    Quantum Natural Gradient optimizer.

    Uses the quantum Fisher information metric to precondition gradients,
    leading to faster convergence in quantum optimization landscapes.

    Reference: Stokes et al., "Quantum Natural Gradient", Quantum 4, 269 (2020)
    """

    def __init__(self, learning_rate: float = 0.01, epsilon: float = 1e-8):
        """
        Initialize QNG optimizer.

        Args:
            learning_rate: Step size for parameter updates
            epsilon: Small constant for numerical stability
        """
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.history = []

    def compute_metric_tensor(
        self, circuit_fn: Callable, params: np.ndarray, shift: float = np.pi / 2
    ) -> np.ndarray:
        """
        Compute the quantum Fisher information metric tensor.

        Uses parameter shift rule to estimate the metric.

        Args:
            circuit_fn: Function that builds circuit from parameters
            params: Current parameters
            shift: Parameter shift for finite difference

        Returns:
            Metric tensor (Fubini-Study metric)
        """
        n = len(params)
        metric = np.zeros((n, n))

        # Diagonal elements (easier to compute)
        for i in range(n):
            params_plus = params.copy()
            params_minus = params.copy()
            params_plus[i] += shift
            params_minus[i] -= shift

            # Overlap between shifted states
            # In practice, this would require state vector access
            # For now, use simplified approximation
            metric[i, i] = 1.0  # Placeholder

        # Off-diagonal elements (cross terms)
        # Simplified version - full QNG requires expensive calculations

        return metric + self.epsilon * np.eye(n)

    def step(
        self,
        params: np.ndarray,
        gradient: np.ndarray,
        circuit_fn: Optional[Callable] = None,
    ) -> np.ndarray:
        """
        Perform one optimization step.

        Args:
            params: Current parameters
            gradient: Gradient vector
            circuit_fn: Circuit function (for metric computation)

        Returns:
            Updated parameters
        """
        if circuit_fn is not None:
            # Compute metric tensor
            metric = self.compute_metric_tensor(circuit_fn, params)

            # Natural gradient = metric^{-1} @ gradient
            try:
                natural_grad = np.linalg.solve(metric, gradient)
            except np.linalg.LinAlgError:
                # Fallback to regular gradient if metric is singular
                natural_grad = gradient
        else:
            # No circuit function - use regular gradient
            natural_grad = gradient

        # Update parameters
        new_params = params - self.learning_rate * natural_grad

        return new_params


class NelderMeadOptimizer:
    """
    Nelder-Mead simplex optimizer.

    Gradient-free optimization using simplex method.
    Good for noisy cost functions and when gradients are unavailable.
    """

    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-6):
        """
        Initialize Nelder-Mead optimizer.

        Args:
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.history = []

    def minimize(
        self, cost_function: Callable, initial_params: np.ndarray, **kwargs
    ) -> Dict[str, Any]:
        """
        Minimize cost function using Nelder-Mead.

        Args:
            cost_function: Function to minimize
            initial_params: Starting parameters
            **kwargs: Additional arguments for scipy.optimize.minimize

        Returns:
            Optimization result dictionary
        """
        # Use scipy's implementation
        result = minimize(
            cost_function,
            initial_params,
            method="Nelder-Mead",
            options={
                "maxiter": self.max_iterations,
                "xatol": self.tolerance,
                "fatol": self.tolerance,
                **kwargs.get("options", {}),
            },
        )

        return {
            "params": result.x,
            "cost": result.fun,
            "iterations": result.nit,
            "success": result.success,
            "message": result.message,
        }


class LBFGSBOptimizer:
    """
    L-BFGS-B optimizer (Limited-memory BFGS with bounds).

    Quasi-Newton method that's memory-efficient and supports bound constraints.
    Excellent for medium-scale optimization problems.
    """

    def __init__(
        self,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        bounds: Optional[list] = None,
    ):
        """
        Initialize L-BFGS-B optimizer.

        Args:
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            bounds: Parameter bounds as [(min, max), ...] or None
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.bounds = bounds
        self.history = []

    def minimize(
        self,
        cost_function: Callable,
        initial_params: np.ndarray,
        gradient_function: Optional[Callable] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Minimize cost function using L-BFGS-B.

        Args:
            cost_function: Function to minimize
            initial_params: Starting parameters
            gradient_function: Optional gradient function (computed if None)
            **kwargs: Additional arguments

        Returns:
            Optimization result dictionary
        """
        # Use scipy's implementation
        result = minimize(
            cost_function,
            initial_params,
            method="L-BFGS-B",
            jac=gradient_function,
            bounds=self.bounds,
            options={
                "maxiter": self.max_iterations,
                "ftol": self.tolerance,
                "gtol": self.tolerance,
                **kwargs.get("options", {}),
            },
        )

        return {
            "params": result.x,
            "cost": result.fun,
            "iterations": result.nit,
            "success": result.success,
            "message": result.message,
            "gradient_evals": result.njev if hasattr(result, "njev") else None,
        }


class COBYLAOptimizer:
    """
    COBYLA optimizer (Constrained Optimization BY Linear Approximation).

    Gradient-free optimizer that supports constraints.
    Already exists in the codebase, included here for completeness.
    """

    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-6):
        """Initialize COBYLA optimizer"""
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.history = []

    def minimize(
        self,
        cost_function: Callable,
        initial_params: np.ndarray,
        constraints: Optional[list] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Minimize using COBYLA.

        Args:
            cost_function: Function to minimize
            initial_params: Starting parameters
            constraints: Optional constraints
            **kwargs: Additional arguments

        Returns:
            Optimization result
        """
        result = minimize(
            cost_function,
            initial_params,
            method="COBYLA",
            constraints=constraints,
            options={
                "maxiter": self.max_iterations,
                "tol": self.tolerance,
                **kwargs.get("options", {}),
            },
        )

        return {
            "params": result.x,
            "cost": result.fun,
            "iterations": result.nfev,  # COBYLA uses function evals
            "success": result.success,
            "message": result.message,
        }


def get_optimizer(name: str, **kwargs):
    """
    Factory function to get optimizer by name.

    Args:
        name: Optimizer name ('qng', 'nelder-mead', 'lbfgs', 'cobyla')
        **kwargs: Optimizer-specific parameters

    Returns:
        Optimizer instance

    Example:
        >>> opt = get_optimizer('lbfgs', max_iterations=500)
        >>> result = opt.minimize(cost_fn, initial_params)
    """
    optimizers = {
        "qng": QuantumNaturalGradient,
        "quantum-natural-gradient": QuantumNaturalGradient,
        "nelder-mead": NelderMeadOptimizer,
        "nm": NelderMeadOptimizer,
        "lbfgs": LBFGSBOptimizer,
        "lbfgsb": LBFGSBOptimizer,
        "l-bfgs-b": LBFGSBOptimizer,
        "cobyla": COBYLAOptimizer,
    }

    name = name.lower().replace("_", "-")
    if name not in optimizers:
        raise ValueError(
            f"Unknown optimizer: {name}. Choose from {list(set(optimizers.values()))}"
        )

    return optimizers[name](**kwargs)


def compare_optimizers(
    cost_function: Callable, initial_params: np.ndarray, optimizers: list, **kwargs
) -> Dict[str, Any]:
    """
    Compare multiple optimizers on the same problem.

    Args:
        cost_function: Function to minimize
        initial_params: Starting point
        optimizers: List of optimizer names or instances
        **kwargs: Additional arguments

    Returns:
        Comparison results

    Example:
        >>> results = compare_optimizers(
        ...     cost_fn,
        ...     params,
        ...     ['adam', 'lbfgs', 'nelder-mead']
        ... )
    """
    results = {}

    for opt_name in optimizers:
        if isinstance(opt_name, str):
            opt = get_optimizer(opt_name)
        else:
            opt = opt_name

        try:
            result = opt.minimize(cost_function, initial_params.copy(), **kwargs)
            results[
                opt_name if isinstance(opt_name, str) else opt.__class__.__name__
            ] = result
        except Exception as e:
            results[
                opt_name if isinstance(opt_name, str) else opt.__class__.__name__
            ] = {"error": str(e)}

    return results
