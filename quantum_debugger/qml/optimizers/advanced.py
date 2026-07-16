"""
Advanced Optimizers for Quantum Machine Learning

Provides sophisticated optimization algorithms beyond basic gradient descent.
"""

import numpy as np
from typing import Callable, Optional, Dict, Any
from scipy.optimize import minimize
from .basics import Adam, GradientDescent


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
        self, circuit_fn: Callable, params: np.ndarray, shift: float = 1e-4
    ) -> np.ndarray:
        """
        Compute the Fubini-Study metric tensor (quantum geometric tensor, real part).

        g_ij = Re[<d_i psi | d_j psi> - <d_i psi | psi><psi | d_j psi>]

        where |psi(theta)> = circuit_fn(theta) must return the state vector. The
        derivative states are obtained by central finite differences. When
        circuit_fn does not return a usable state vector (e.g. returns None), the
        metric cannot be computed and we fall back to the identity (equivalent to
        plain gradient descent) rather than returning a fabricated value.

        Args:
            circuit_fn: Function mapping parameters -> state vector (np.ndarray)
            params: Current parameters
            shift: Finite-difference step for the derivative states

        Returns:
            Metric tensor (n x n), symmetric positive semidefinite (+ epsilon I)
        """
        n = len(params)

        def state_at(p):
            if circuit_fn is None:
                return None
            try:
                out = circuit_fn(np.asarray(p, dtype=float))
            except Exception:
                return None
            if out is None:
                return None
            vec = np.asarray(out, dtype=complex).ravel()
            return vec if vec.size >= 2 else None

        psi = state_at(params)
        if psi is None:
            # No state vector available -> identity metric (plain gradient descent).
            return np.eye(n) + self.epsilon * np.eye(n)

        # Derivative states via central finite differences.
        dpsi = []
        for i in range(n):
            p_plus = np.array(params, dtype=float)
            p_plus[i] += shift
            p_minus = np.array(params, dtype=float)
            p_minus[i] -= shift
            s_plus = state_at(p_plus)
            s_minus = state_at(p_minus)
            if s_plus is None or s_minus is None:
                return np.eye(n) + self.epsilon * np.eye(n)
            dpsi.append((s_plus - s_minus) / (2 * shift))

        # <psi | d_i psi>
        overlaps = np.array([np.vdot(psi, d) for d in dpsi])

        metric = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                term = np.vdot(dpsi[i], dpsi[j]) - np.conj(overlaps[i]) * overlaps[j]
                metric[i, j] = np.real(term)

        # Symmetrize (guards against finite-difference asymmetry) and regularize.
        metric = 0.5 * (metric + metric.T)
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
        "adam": Adam,
        "gd": GradientDescent,
        "gradient-descent": GradientDescent,
        "sgd": GradientDescent,
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
