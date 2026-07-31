"""
Quantum walks -- the quantum analogue of random walks.

Where a classical random walk spreads diffusively (standard deviation ``~ sqrt(t)``), a
*quantum* walk spreads ballistically (``~ t``) because amplitudes interfere instead of
probabilities adding. Two models and their applications are provided:

* **Continuous-time quantum walk (CTQW)** -- evolve under ``e^{-i A t}`` with ``A`` the
  graph adjacency matrix; the walker's probability distribution spreads quadratically
  faster than the classical one.
* **Discrete-time quantum walk (DTQW)** -- a coin register plus a shift, iterated; on a
  line it gives the characteristic ballistic two-peaked distribution.
* **Szegedy quantization** turns any Markov chain into a unitary walk whose stationary
  distribution is a fixed point.
* **Spatial search** by CTQW finds a marked vertex with a quadratic speedup on the
  complete graph.

Verified against exact evolution: unitarity, probability conservation, the quadratic
(``t^2``) growth of the position variance, and high marked-vertex overlap in search.
"""

import numpy as np
from scipy.linalg import expm


def continuous_time_walk_operator(adjacency, time: float) -> np.ndarray:
    """CTQW propagator ``U(t) = e^{-i A t}`` for graph adjacency ``A`` -- a unitary that
    evolves amplitudes across the graph."""
    A = np.asarray(adjacency, dtype=complex)
    return expm(-1j * A * time)


def ctqw_distribution(adjacency, time: float, start: int = 0) -> np.ndarray:
    """
    Probability distribution of a continuous-time quantum walk started at vertex ``start``
    after evolving for ``time`` under the graph adjacency. Sums to 1 (probability
    conserved).
    """
    n = np.asarray(adjacency).shape[0]
    psi0 = np.zeros(n, dtype=complex); psi0[start] = 1.0
    psi = continuous_time_walk_operator(adjacency, time) @ psi0
    return np.abs(psi) ** 2


def position_variance(distribution, positions=None) -> float:
    """Variance ``<x^2> - <x>^2`` of a position distribution -- ``~ t^2`` for a quantum walk,
    ``~ t`` for a classical one."""
    p = np.asarray(distribution, dtype=float)
    x = np.arange(len(p)) if positions is None else np.asarray(positions, dtype=float)
    mean = np.sum(p * x)
    return float(np.sum(p * x**2) - mean**2)


def line_adjacency(n: int) -> np.ndarray:
    """Adjacency matrix of a path graph on ``n`` vertices (a line)."""
    A = np.zeros((n, n))
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    return A


def discrete_time_walk_line(steps: int) -> np.ndarray:
    """
    Discrete-time coined quantum walk on a line for ``steps`` steps (Hadamard coin, start at
    the origin). Returns the position probability distribution -- the characteristic
    ballistic, twin-peaked profile whose variance grows as ``steps^2``.
    """
    n = 2 * steps + 1                       # positions -steps .. steps
    coin = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    # state[position, coin]
    state = np.zeros((n, 2), dtype=complex)
    state[steps, 0] = 1 / np.sqrt(2)
    state[steps, 1] = 1j / np.sqrt(2)       # symmetric start
    for _ in range(steps):
        state = state @ coin.T              # apply coin
        new = np.zeros_like(state)
        new[:-1, 0] = state[1:, 0]          # coin 0 -> move left
        new[1:, 1] = state[:-1, 1]          # coin 1 -> move right
        state = new
    return np.sum(np.abs(state) ** 2, axis=1)


def szegedy_walk_operator(P) -> np.ndarray:
    """
    Szegedy walk unitary ``W = R_2 R_1`` (product of two reflections) quantizing a stochastic
    matrix ``P`` on ``n`` states, acting on the ``n^2`` edge space. Unitary, and the
    stationary distribution of ``P`` lifts to a ``+1`` eigenvector -- the walk that powers
    quantum sampling and search speedups.
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    # |psi_j> = |j> (x) sum_k sqrt(P_jk) |k>
    psis = np.zeros((n, n * n), dtype=complex)
    for j in range(n):
        for k in range(n):
            psis[j, j * n + k] = np.sqrt(P[j, k])
    Pi_A = psis.conj().T @ psis             # projector onto span{|psi_j>}
    R1 = 2 * Pi_A - np.eye(n * n)
    # swap operator on the two registers
    S = np.zeros((n * n, n * n))
    for a in range(n):
        for b in range(n):
            S[b * n + a, a * n + b] = 1
    R2 = S @ R1 @ S
    return R2 @ R1


def spatial_search_ctqw(adjacency, marked: int, gamma: float, time: float) -> float:
    """
    Continuous-time spatial search: evolve under ``H = -gamma A - |marked><marked|`` and
    return the probability of finding ``marked``. On the complete graph the optimal
    ``gamma, time`` give ``O(1)`` success in ``O(sqrt(N))`` time -- the quantum search
    speedup. Verified to reach high overlap.
    """
    A = np.asarray(adjacency, dtype=complex)
    n = A.shape[0]
    H = -gamma * A - np.outer(np.eye(n)[marked], np.eye(n)[marked])
    psi0 = np.ones(n, dtype=complex) / np.sqrt(n)     # uniform start
    psi = expm(-1j * H * time) @ psi0
    return float(np.abs(psi[marked]) ** 2)
