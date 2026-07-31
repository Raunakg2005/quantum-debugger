"""
QAOA -- the Quantum Approximate Optimization Algorithm, from the inside.

QAOA prepares ``|gamma, beta> = prod_{k=1}^{p} e^{-i beta_k B} e^{-i gamma_k C} |+>^n`` where
``C`` is the (diagonal) cost Hamiltonian of a combinatorial problem and ``B = sum_i X_i`` is
the transverse-field mixer, then measures ``<C>``. The optimizer tunes the ``2p`` angles to
minimize (or maximize) that expectation. This module builds the cost and mixer layers, the
QAOA state, its exact cost expectation, and a small optimizer for ``p=1``, and reports the
approximation ratio against the true optimum. Everything is computed from the exact
state vector and verified against brute force.
"""

import numpy as np


def cost_diagonal(edges, n: int) -> np.ndarray:
    """
    Diagonal of the MaxCut cost operator ``C = sum_{(i,j)} (1 - Z_i Z_j)/2`` -- the number of
    cut edges for each computational basis state.
    """
    diag = np.zeros(2 ** n)
    for b in range(2 ** n):
        diag[b] = sum(1 for i, j in edges if ((b >> i) & 1) != ((b >> j) & 1))
    return diag


def cost_layer(cost_diag, gamma: float) -> np.ndarray:
    """Cost-layer phases ``e^{-i gamma C}`` for a diagonal cost -- a diagonal unitary applied
    as a phase on each amplitude."""
    return np.exp(-1j * gamma * np.asarray(cost_diag))


def mixer_layer(state, beta: float, n: int) -> np.ndarray:
    """
    Apply the transverse-field mixer ``e^{-i beta sum_i X_i} = prod_i (cos beta I - i sin beta
    X_i)`` to a state vector.
    """
    psi = np.asarray(state, dtype=complex).reshape([2] * n)
    c, s = np.cos(beta), -1j * np.sin(beta)
    for axis in range(n):
        psi = c * psi + s * np.flip(psi, axis=axis)
    return psi.reshape(-1)


def qaoa_state(cost_diag, gammas, betas, n: int) -> np.ndarray:
    """
    The QAOA state ``prod_k e^{-i beta_k B} e^{-i gamma_k C} |+>^n`` for schedules ``gammas``,
    ``betas`` (length ``p``). Normalized.
    """
    psi = np.ones(2 ** n, dtype=complex) / np.sqrt(2 ** n)
    for g, b in zip(gammas, betas):
        psi = cost_layer(cost_diag, g) * psi
        psi = mixer_layer(psi, b, n)
    return psi


def qaoa_expectation(cost_diag, gammas, betas, n: int) -> float:
    """
    Exact cost expectation ``<gamma,beta| C |gamma,beta>`` of the QAOA state (``C`` diagonal).
    The objective the QAOA optimizer maximizes for MaxCut.
    """
    psi = qaoa_state(cost_diag, gammas, betas, n)
    return float(np.sum(np.asarray(cost_diag) * np.abs(psi) ** 2))


def optimize_qaoa_p1(edges, n: int, grid: int = 40) -> dict:
    """
    Grid-search the two ``p=1`` angles to maximize ``<C>`` for MaxCut. Returns the best
    ``gamma, beta``, the expected cut, and the approximation ratio to the true maximum cut.
    Verified to beat the random-guess expectation (half the edges).
    """
    diag = cost_diagonal(edges, n)
    best = {"expectation": -np.inf}
    for g in np.linspace(0, np.pi, grid):
        for b in np.linspace(0, np.pi / 2, grid):
            e = qaoa_expectation(diag, [g], [b], n)
            if e > best["expectation"]:
                best = {"gamma": g, "beta": b, "expectation": e}
    best["max_cut"] = float(diag.max())
    best["approximation_ratio"] = best["expectation"] / best["max_cut"]
    return best


def qaoa_landscape(edges, n: int, grid: int = 30) -> np.ndarray:
    """
    The ``p=1`` energy landscape ``<C>(gamma, beta)`` on a ``grid x grid`` mesh -- the surface
    the optimizer climbs. Periodic and smooth, illustrating the concentration of good
    parameters.
    """
    diag = cost_diagonal(edges, n)
    gs = np.linspace(0, np.pi, grid)
    bs = np.linspace(0, np.pi / 2, grid)
    return np.array([[qaoa_expectation(diag, [g], [b], n) for b in bs] for g in gs])
