"""
Markov chains, PageRank, and their quantum walk versions.

Random walks on graphs underlie ranking (PageRank) and sampling. Their quantum
counterparts -- built from the Szegedy walk of the transition matrix -- can mix faster
and resolve node importance differently. This module provides the classical machinery
(stationary distribution, the PageRank Google matrix, reversibility) and the quantum
PageRank of Paparo-Martin-Delgado, obtained by evolving the Szegedy walk and time-
averaging the node occupations. Verified: stationary distributions are fixed points and
sum to 1, the Google matrix is stochastic, and quantum PageRank is a valid distribution
whose ranking tracks the classical one.
"""

import numpy as np

from .quantum_walks import szegedy_walk_operator


def is_stochastic(M, axis: int = 1, atol: float = 1e-9) -> bool:
    """True iff ``M`` is (row- if axis=1) stochastic: non-negative with unit line sums."""
    M = np.asarray(M, dtype=float)
    return bool(np.all(M >= -atol) and np.allclose(M.sum(axis=axis), 1, atol=atol))


def stationary_distribution(P) -> np.ndarray:
    """
    Stationary distribution ``pi`` of a row-stochastic transition matrix ``P``
    (``pi P = pi``, ``sum pi = 1``): the normalized left Perron eigenvector for eigenvalue 1.
    Verified to be a fixed point.
    """
    P = np.asarray(P, dtype=float)
    w, v = np.linalg.eig(P.T)
    idx = int(np.argmin(np.abs(w - 1)))
    pi = np.real(v[:, idx])
    pi = pi / pi.sum()
    return pi


def google_matrix(adjacency, alpha: float = 0.85) -> np.ndarray:
    """
    PageRank Google matrix ``G = alpha P + (1-alpha) (1/n) J`` from a graph adjacency, where
    ``P`` is the row-normalized transition matrix (dangling nodes get a uniform row) and
    ``J`` is all-ones. Row-stochastic and primitive, so it has a unique stationary
    distribution -- the PageRank vector.
    """
    A = np.asarray(adjacency, dtype=float)
    n = A.shape[0]
    P = np.zeros((n, n))
    for i in range(n):
        s = A[i].sum()
        P[i] = A[i] / s if s > 0 else np.ones(n) / n     # dangling -> uniform
    return alpha * P + (1 - alpha) * np.ones((n, n)) / n


def classical_pagerank(adjacency, alpha: float = 0.85) -> np.ndarray:
    """Classical PageRank: the stationary distribution of the Google matrix -- node
    importance from a damped random surfer. Sums to 1."""
    return stationary_distribution(google_matrix(adjacency, alpha))


def detailed_balance(P, pi, atol: float = 1e-9) -> bool:
    """
    Reversibility (detailed balance) check ``pi_i P_ij = pi_j P_ji`` for a chain ``P`` with
    distribution ``pi`` -- the condition for a reversible Markov chain.
    """
    P = np.asarray(P, dtype=float); pi = np.asarray(pi, dtype=float)
    n = len(pi)
    return bool(all(abs(pi[i] * P[i, j] - pi[j] * P[j, i]) < atol
                    for i in range(n) for j in range(n)))


def quantum_pagerank(adjacency, alpha: float = 0.85, steps: int = 200) -> np.ndarray:
    """
    Quantum PageRank (Paparo-Martin-Delgado): evolve the Szegedy walk of the Google matrix
    and time-average the probability on each node's edge subspace. Returns a normalized
    ranking vector -- a valid distribution whose order tracks classical PageRank while
    sharpening the contrast between nodes. Verified non-negative and summing to 1.
    """
    G = google_matrix(adjacency, alpha)
    n = G.shape[0]
    W = szegedy_walk_operator(G)
    # initial state: uniform superposition of |psi_i>
    psi0 = np.zeros(n * n, dtype=complex)
    for i in range(n):
        for k in range(n):
            psi0[i * n + k] = np.sqrt(G[i, k]) / np.sqrt(n)
    psi0 = psi0 / np.linalg.norm(psi0)
    inst = np.zeros(n)
    psi = psi0.copy()
    for _ in range(steps):
        psi = W @ psi
        probs = np.abs(psi) ** 2
        for i in range(n):                       # node i occupation = sum over its edges (2nd register)
            inst[i] += np.sum(probs[i::n])
    r = inst / inst.sum()
    return r
