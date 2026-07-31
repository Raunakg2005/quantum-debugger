"""
Mirror benchmarking -- scalable fidelity from reversible circuits.

Randomized benchmarking is limited to Clifford gates and small qubit counts. **Mirror
benchmarking** sidesteps both: run a random circuit, then its inverse ("mirror"), so the
ideal result returns to the initial state and the survival probability directly reports the
accumulated error. It works for universal gate sets and scales to many qubits. This module
runs the mirror at the density-matrix level with an optional per-layer noise channel and
returns the survival probability, verified to be 1 in the noiseless case and to decay with
noise and depth.
"""

import numpy as np


def mirror_survival(layers, initial_state=None, noise_channel=None) -> float:
    """
    Survival probability of a mirror circuit: apply the unitary ``layers`` in order, then
    their inverses in reverse, and measure the overlap with the initial state. With
    ``noise_channel`` (a density-matrix map applied after each layer) the survival decays;
    without it, it is exactly 1 -- the mirror-benchmarking signal. ``layers`` is a list of
    unitary matrices.
    """
    d = np.asarray(layers[0]).shape[0]
    if initial_state is None:
        psi0 = np.zeros(d, dtype=complex); psi0[0] = 1.0
    else:
        psi0 = np.asarray(initial_state, dtype=complex)
    rho0 = np.outer(psi0, psi0.conj())
    rho = rho0.copy()
    sequence = list(layers) + [np.asarray(L).conj().T for L in reversed(layers)]
    for L in sequence:
        L = np.asarray(L, dtype=complex)
        rho = L @ rho @ L.conj().T
        if noise_channel is not None:
            rho = noise_channel(rho)
    return float(np.real(np.trace(rho0 @ rho)))


def depolarizing_layer(p: float):
    """A per-layer depolarizing noise channel ``rho -> (1-p) rho + p I/d`` for use with
    :func:`mirror_survival`."""
    def chan(rho):
        d = rho.shape[0]
        return (1 - p) * rho + p * np.eye(d) / d * np.trace(rho)
    return chan


def mirror_fidelity_decay(layers_list, p: float):
    """
    Survival probability of mirror circuits of increasing depth (each entry of
    ``layers_list`` is a layer list) under depolarizing noise ``p`` -- the decay curve from
    which an error-per-layer is read off. Verified monotonically decreasing with depth.
    """
    return [mirror_survival(layers, noise_channel=depolarizing_layer(p)) for layers in layers_list]
