"""
Unitary folding -- the noise amplifier that makes ZNE possible on real hardware.

To run a circuit at a larger noise scale *without changing what it computes*, replace
a unitary ``G`` (a gate or the whole circuit) by ``G (G^dagger G)^k = G``. The extra
``G^dagger G`` pairs are the identity ideally, so the logical action is untouched, but
each real gate runs ``2k+1`` times, scaling the accumulated error by ``2k+1``. Global
folding folds the whole circuit; local folding folds individual gates to reach
non-integer scale factors. This module builds the folded sequence, checks the ideal
action is preserved, and models the amplified noise at the density-matrix level -- the
front end that feeds :mod:`zne` / :mod:`zne_extrapolation`.
"""

import numpy as np


def fold_global(unitary, num_folds: int) -> np.ndarray:
    """
    Global folding ``G -> G (G^dagger G)^{num_folds}``. The result equals ``G`` exactly
    (ideal action preserved) while every gate is executed ``2*num_folds + 1`` times.
    """
    G = np.asarray(unitary, dtype=complex)
    Gd = G.conj().T
    out = G.copy()
    for _ in range(num_folds):
        out = out @ Gd @ G
    return out


def noise_scale_factor(num_folds: int) -> int:
    """The odd noise-amplification factor ``2*num_folds + 1`` of global folding."""
    return 2 * num_folds + 1


def fold_gate_sequence(gates, fold_indices) -> list:
    """
    Local folding: replace each gate ``G_i`` with ``i in fold_indices`` by the triple
    ``G_i, G_i^dagger, G_i`` in the gate list, leaving the others alone. The folded list
    implements the same overall unitary but amplifies the noise of the selected gates,
    giving fine-grained (non-integer) control of the effective noise scale. Returns the
    new list of gate matrices.
    """
    fold = set(fold_indices)
    out = []
    for i, g in enumerate(gates):
        G = np.asarray(g, dtype=complex)
        if i in fold:
            out.extend([G, G.conj().T, G])
        else:
            out.append(G)
    return out


def folded_channel_expectation(density_matrix_factory, noise_channel, observable,
                               num_folds: int) -> float:
    """
    Expectation of ``observable`` after a folded noisy layer: the ideal unitary is
    unchanged but the noise channel is applied ``2*num_folds + 1`` times (the folded
    execution). ``density_matrix_factory()`` returns the input state; ``noise_channel``
    maps a density matrix to a density matrix. This is the density-matrix model ZNE
    extrapolates over the fold count.
    """
    rho = np.asarray(density_matrix_factory(), dtype=complex)
    for _ in range(noise_scale_factor(num_folds)):
        rho = noise_channel(rho)
    O = np.asarray(observable, dtype=complex)
    return float(np.real(np.trace(O @ rho)))
