"""
Barren plateaus in variational quantum circuits.

The central obstacle to training deep variational circuits: for a random, expressive
ansatz the gradient's **variance shrinks as the qubit number grows**. The landscape
flattens into a plateau, so gradients vanish into the shot noise and training stalls. This
module estimates the gradient variance over random parameters and verifies the onset of the
plateau -- the gradient variance (and the cost-value variance, "cost concentration") both
decrease with system size for a sufficiently deep global-cost ansatz. It also exposes the
gradient variance for a single-qubit (local) cost as a comparison point.
"""

import numpy as np

from .variational_ansatz import (
    hardware_efficient_ansatz, ansatz_num_params, z_observable, ansatz_expectation)
from .parameter_shift import parameter_shift_gradient


def gradient_sample_variance(n: int, layers: int, obs_diag, samples: int = 200,
                             seed: int = 0) -> float:
    """
    Variance of the first parameter's gradient over ``samples`` random parameter settings --
    the empirical barren-plateau diagnostic. Small variance means an exponentially flat
    landscape.
    """
    rng = np.random.default_rng(seed)
    n_params = ansatz_num_params(n, layers)
    grads = []
    for _ in range(samples):
        params = rng.uniform(0, 2 * np.pi, n_params)
        cost = lambda p: ansatz_expectation(p, n, layers, obs_diag)
        grads.append(parameter_shift_gradient(cost, params, 0))
    return float(np.var(grads))


def barren_plateau_scaling(qubit_range, layers: int = 8, samples: int = 200) -> dict:
    """
    Gradient variance of a *global* cost (``sum_q Z_q``) as a function of qubit number, at a
    depth large enough to make the ansatz expressive -- verified to *decrease* with ``n`` (the
    barren-plateau onset). Returns ``{n: variance}``.
    """
    out = {}
    for n in qubit_range:
        out[n] = gradient_sample_variance(n, layers, z_observable(n), samples)
    return out


def local_cost_gradient_variance(n: int, layers: int, samples: int = 200, seed: int = 0) -> float:
    """
    Gradient variance for a *local* cost measuring a single qubit (``Z_0``) -- a comparison
    point for the global cost. (Whether a local cost avoids the plateau depends on the circuit
    depth and light cone; here it is exposed as a measurement.)
    """
    return gradient_sample_variance(n, layers, z_observable(n, qubits=[0]), samples, seed)


def global_cost_gradient_variance(n: int, layers: int, samples: int = 200, seed: int = 0) -> float:
    """Gradient variance for the *global* cost (all qubits) -- the barren-plateau-prone
    objective."""
    return gradient_sample_variance(n, layers, z_observable(n), samples, seed)


def cost_concentration(n: int, layers: int, samples: int = 300, seed: int = 0) -> float:
    """
    Variance of the *cost value* itself over random parameters -- concentration (small
    variance) around the mean is the flip side of the barren plateau. Decreases with system
    size for a global cost.
    """
    rng = np.random.default_rng(seed)
    obs = z_observable(n)
    vals = [ansatz_expectation(rng.uniform(0, 2 * np.pi, ansatz_num_params(n, layers)),
                               n, layers, obs) for _ in range(samples)]
    return float(np.var(vals))
