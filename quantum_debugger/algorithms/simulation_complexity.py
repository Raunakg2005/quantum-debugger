"""
Gate-count complexity of Hamiltonian-simulation methods.

Different simulation methods trade off differently as the Hamiltonian and precision change.
This module collects their asymptotic gate counts so they can be compared and the best method
picked for a given problem:

* **First-order Trotter** -- steps ``~ (sum ||[H_i,H_j]||) t^2 / (2 eps)``, times the number of
  terms per step.
* **Second-order Trotter** -- steps ``~ t^{3/2}``-scaling, fewer for the same error.
* **qDRIFT** -- ``~ 2 lambda^2 t^2 / eps`` gates, independent of the number of terms.
* **Taylor / LCU** -- ``~ log(1/eps)`` in the precision, exponentially better in ``eps``.

The counts are exact formulas (verified by evaluation and by the crossover where qDRIFT beats
Trotter for many small terms).
"""

import numpy as np
from math import factorial


def trotter_first_order_steps(commutator_sum: float, t: float, epsilon: float) -> int:
    """Trotter steps for first-order precision ``epsilon``:
    ``r = ceil((commutator_sum) t^2 / (2 eps))`` from the error bound."""
    return int(np.ceil(commutator_sum * t ** 2 / (2 * epsilon)))


def trotter_first_order_gate_count(n_terms: int, commutator_sum: float, t: float,
                                   epsilon: float) -> int:
    """Total first-order Trotter gate count: ``n_terms`` term-exponentials per step times the
    number of steps."""
    return int(n_terms * trotter_first_order_steps(commutator_sum, t, epsilon))


def trotter_second_order_steps(second_order_bound_coeff: float, t: float, epsilon: float) -> int:
    """Trotter steps for second-order precision: ``r = ceil(sqrt(coeff t^3 / eps))`` -- fewer
    than first order for the same error at small ``eps``."""
    return int(np.ceil(np.sqrt(second_order_bound_coeff * t ** 3 / epsilon)))


def qdrift_gate_count(lam: float, t: float, epsilon: float) -> int:
    """qDRIFT gate count ``ceil(2 lambda^2 t^2 / eps)`` -- independent of the number of terms."""
    return int(np.ceil(2 * lam ** 2 * t ** 2 / epsilon))


def taylor_gate_count(norm_Ht: float, epsilon: float) -> int:
    """
    Truncated-Taylor / LCU order needed for precision ``epsilon``: the smallest ``K`` with
    ``norm_Ht^{K+1}/(K+1)! < eps`` -- logarithmic in ``1/eps`` (exponentially fewer than Trotter
    in the precision).
    """
    for K in range(200):
        if norm_Ht ** (K + 1) / factorial(K + 1) < epsilon:
            return K
    return 200


def qdrift_beats_trotter(n_terms: int, commutator_sum: float, lam: float, t: float,
                         epsilon: float) -> bool:
    """
    True when qDRIFT needs fewer gates than first-order Trotter -- typically for a Hamiltonian
    with *many* terms (Trotter cost carries the ``n_terms`` factor, qDRIFT does not). The
    verifiable crossover.
    """
    return qdrift_gate_count(lam, t, epsilon) < trotter_first_order_gate_count(
        n_terms, commutator_sum, t, epsilon)


def cheapest_method(n_terms: int, commutator_sum: float, lam: float, norm_Ht: float,
                    t: float, epsilon: float) -> str:
    """
    Return the name of the method (``'trotter1'``, ``'qdrift'``, ``'taylor'``) with the smallest
    gate count for the given parameters -- a simple simulation-method selector.
    """
    counts = {
        "trotter1": trotter_first_order_gate_count(n_terms, commutator_sum, t, epsilon),
        "qdrift": qdrift_gate_count(lam, t, epsilon),
        "taylor": taylor_gate_count(norm_Ht, epsilon),
    }
    return min(counts, key=counts.get)
