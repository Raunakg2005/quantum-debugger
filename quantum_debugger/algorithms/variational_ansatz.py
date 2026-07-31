"""
A hardware-efficient variational ansatz and its expectation values.

The variational-algorithms theory in this release is illustrated on the standard
hardware-efficient ansatz: alternating layers of single-qubit ``Ry`` rotations and a
CNOT entangling ladder,

    |psi(theta)> = prod_{l=1}^{L} [ CNOT-ladder . prod_q Ry(theta_{l,q}) ] |0>^n.

This module builds the ansatz state, counts its parameters, and evaluates the expectation
of a diagonal (Z-type) observable -- the cost function that the parameter-shift gradients,
barren-plateau analysis, expressibility, and natural-gradient routines all act on.
"""

import numpy as np


def _ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def _apply_1q(psi, gate, q, n):
    psi = psi.reshape([2] * n)
    psi = np.moveaxis(np.tensordot(gate, np.moveaxis(psi, q, 0), axes=(1, 0)), 0, q)
    return psi.reshape(-1)


def _apply_cnot(psi, control, target, n):
    psi = psi.reshape([2] * n)
    idx = [slice(None)] * n
    idx[control] = 1
    sub = psi[tuple(idx)]
    psi[tuple(idx)] = np.flip(sub, axis=target if target < control else target - 1)
    return psi.reshape(-1)


def ansatz_num_params(n: int, layers: int) -> int:
    """Number of parameters of the ``layers``-deep hardware-efficient ansatz on ``n``
    qubits: ``n * layers``."""
    return n * layers


def hardware_efficient_ansatz(params, n: int, layers: int) -> np.ndarray:
    """
    Build the ansatz state from a flat ``params`` array of length ``n*layers``: per layer,
    an ``Ry`` on each qubit followed by a linear CNOT entangling ladder. Returns the state
    vector.
    """
    theta = np.asarray(params, dtype=float).reshape(layers, n)
    psi = np.zeros(2 ** n, dtype=complex); psi[0] = 1.0
    for l in range(layers):
        for q in range(n):
            psi = _apply_1q(psi, _ry(theta[l, q]), q, n)
        for q in range(n - 1):
            psi = _apply_cnot(psi, q, q + 1, n)
    return psi


def z_observable(n: int, qubits=None) -> np.ndarray:
    """Diagonal of a ``sum_q Z_q`` observable (over ``qubits``, default all) -- the cost
    operator for the ansatz."""
    qubits = range(n) if qubits is None else qubits
    diag = np.zeros(2 ** n)
    for b in range(2 ** n):
        diag[b] = sum(1 - 2 * ((b >> q) & 1) for q in qubits)
    return diag


def ansatz_expectation(params, n: int, layers: int, obs_diag) -> float:
    """Expectation ``<psi(theta)| O |psi(theta)>`` of a diagonal observable for the ansatz --
    the variational cost function."""
    psi = hardware_efficient_ansatz(params, n, layers)
    return float(np.sum(np.asarray(obs_diag) * np.abs(psi) ** 2))


def random_parameters(n: int, layers: int, seed: int = 0) -> np.ndarray:
    """Uniform random angles in ``[0, 2 pi)`` for the ansatz -- a random point in the training
    landscape."""
    return np.random.default_rng(seed).uniform(0, 2 * np.pi, ansatz_num_params(n, layers))
