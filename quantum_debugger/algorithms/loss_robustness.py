"""
Entanglement robustness under particle loss (GHZ vs W)

The two inequivalent classes of 3-qubit entanglement respond to losing a qubit in
opposite ways -- the standard demonstration of why "how much" entanglement is not
the only question; "how it is shared" matters:

  * **GHZ**: ``(|0...0> + |1...1>)/sqrt(2)`` is maximally entangled, but tracing out
    ANY single qubit leaves the classical mixture ``(|0..0><0..0| + |1..1><1..1|)/2``
    -- zero negativity, fully separable. All the entanglement was global.
  * **W**: ``(|0..01> + |0..10> + ... + |10..0>)/sqrt(n)`` keeps its pairwise
    entanglement: tracing to any pair leaves
    ``(n-2)/n |00><00| + 2/n |Psi+><Psi+|`` with negativity exactly

        N_W(n) = ( sqrt((n-2)^2 + 4) - (n-2) ) / (2n)  >  0   for every n.

Both computed on the density-matrix engine (partial trace + partial transpose) and
verified against the closed forms.
"""

import numpy as np

from ..density_matrix import DensityMatrix
from .state_preparation import ghz_state, w_state


def loss_robustness(n: int = 3) -> dict:
    """
    Prepare the ``n``-qubit GHZ and W states (genuine circuits), trace out one qubit,
    and measure the negativity of a remaining pair (for the W state: the two lowest
    qubits; GHZ is symmetric).

    Returns dict with:
      * ``ghz_pair_negativity``  -- exactly 0 (loss kills GHZ entanglement)
      * ``w_pair_negativity``    -- exactly ``(sqrt((n-2)^2+4) - (n-2)) / (2n)``
      * ``w_analytic``           -- that closed form
      * ``ghz_before_loss``      -- one-vs-rest negativity of the intact GHZ (1/2)
    """
    if n < 3:
        raise ValueError("n must be >= 3")

    ghz = DensityMatrix(state_vector=ghz_state(n))
    w = DensityMatrix(state_vector=w_state(n))

    ghz_before = ghz.negativity([0])

    ghz_pair = ghz.partial_trace([0, 1])
    w_pair = w.partial_trace([0, 1])

    analytic = (np.sqrt((n - 2) ** 2 + 4) - (n - 2)) / (2 * n)
    return {
        "ghz_pair_negativity": ghz_pair.negativity([0]),
        "w_pair_negativity": w_pair.negativity([0]),
        "w_analytic": float(analytic),
        "ghz_before_loss": ghz_before,
    }
