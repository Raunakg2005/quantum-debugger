"""
SPSA -- Simultaneous Perturbation Stochastic Approximation

A gradient-free optimizer (Spall 1998) that estimates the gradient from just two
objective evaluations per iteration, *regardless of the number of parameters*.
This makes it a natural fit for variational quantum algorithms, where each
objective evaluation is an expensive circuit run and parameter-shift gradients
cost 2 evaluations per parameter.
"""

import numpy as np


class SPSA:
    """
    SPSA optimizer with the standard gain sequences.

    a_k = a / (k + 1 + A)**alpha ,  c_k = c / (k + 1)**gamma

    Examples:
        >>> opt = SPSA(a=0.2, c=0.1, maxiter=200)
        >>> result = opt.minimize(lambda x: (x[0] - 3) ** 2 + (x[1] + 1) ** 2, [0.0, 0.0])
        >>> result["x"]        # ~[3, -1]
    """

    def __init__(
        self,
        a: float = 0.2,
        c: float = 0.1,
        alpha: float = 0.602,
        gamma: float = 0.101,
        A: float = None,
        maxiter: int = 200,
        seed: int = None,
    ):
        self.a = a
        self.c = c
        self.alpha = alpha
        self.gamma = gamma
        self.maxiter = maxiter
        # Stability constant A ~ 10% of maxiter is the usual recommendation.
        self.A = A if A is not None else max(1, maxiter // 10)
        self._rng = np.random.default_rng(seed)

    def _gains(self, k: int):
        a_k = self.a / (k + 1 + self.A) ** self.alpha
        c_k = self.c / (k + 1) ** self.gamma
        return a_k, c_k

    def step(self, objective, params: np.ndarray, k: int) -> np.ndarray:
        """One SPSA update from ``params`` at iteration ``k`` (2 evaluations)."""
        params = np.asarray(params, dtype=float)
        a_k, c_k = self._gains(k)

        delta = self._rng.choice([-1.0, 1.0], size=params.shape)
        f_plus = objective(params + c_k * delta)
        f_minus = objective(params - c_k * delta)
        grad_est = (f_plus - f_minus) / (2.0 * c_k) * delta  # 1/delta == delta for +/-1
        return params - a_k * grad_est

    def minimize(self, objective, x0, iterations: int = None) -> dict:
        """
        Minimize ``objective`` starting from ``x0``.

        Returns:
            dict with 'x' (best params), 'fun' (best value), and 'history'.
        """
        iterations = iterations if iterations is not None else self.maxiter
        params = np.asarray(x0, dtype=float).copy()

        best_params = params.copy()
        best_value = float(objective(params))
        history = [best_value]

        for k in range(iterations):
            params = self.step(objective, params, k)
            value = float(objective(params))
            history.append(value)
            if value < best_value:
                best_value = value
                best_params = params.copy()

        return {
            "x": best_params,
            "fun": best_value,
            "iterations": iterations,
            "history": history,
        }
