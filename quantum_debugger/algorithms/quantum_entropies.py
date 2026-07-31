"""
Entropy measures for quantum states.

Entropy quantifies uncertainty and correlations. This module provides the family built
on the eigenvalue spectrum of a density matrix and on its marginals:

* **von Neumann** ``S(rho) = -Tr rho log rho`` -- the quantum Shannon entropy.
* **Rényi** ``S_alpha = (1/(1-alpha)) log Tr rho^alpha`` and **Tsallis** entropies --
  one-parameter families interpolating to von Neumann as ``alpha -> 1``.
* **Conditional entropy** ``S(A|B) = S(AB) - S(B)`` -- which can go *negative* for
  entangled states (a purely quantum effect).
* **Quantum mutual information** ``I(A:B) = S(A) + S(B) - S(AB)`` -- total correlations.

Verified: pure states have zero entropy, the maximally mixed state saturates
``log d``, a Bell state has ``S(A) = 1`` bit, ``S(A|B) = -1``, and ``I(A:B) = 2``.
"""

import numpy as np


def _eigs(rho):
    w = np.linalg.eigvalsh(np.asarray(rho, dtype=complex))
    return np.real(w[w > 1e-12])


def von_neumann_entropy(rho, base: float = 2.0) -> float:
    """
    von Neumann entropy ``S = -sum lambda_i log lambda_i`` over the density-matrix
    eigenvalues. ``0`` for a pure state, ``log d`` for the maximally mixed state.
    """
    w = _eigs(rho)
    return float(-np.sum(w * np.log(w)) / np.log(base))


def renyi_entropy(rho, alpha: float, base: float = 2.0) -> float:
    """
    Rényi-``alpha`` entropy ``(1/(1-alpha)) log Tr rho^alpha``. Recovers the von Neumann
    entropy as ``alpha -> 1``, the max-entropy ``log rank`` at ``alpha -> 0``, and
    ``-log lambda_max`` (min-entropy) as ``alpha -> inf``.
    """
    if abs(alpha - 1.0) < 1e-9:
        return von_neumann_entropy(rho, base)
    w = _eigs(rho)
    return float(np.log(np.sum(w ** alpha)) / ((1 - alpha) * np.log(base)))


def tsallis_entropy(rho, q: float) -> float:
    """
    Tsallis-``q`` entropy ``(1 - Tr rho^q)/(q - 1)`` -- a non-additive entropy family,
    reducing to the (natural-log) von Neumann entropy as ``q -> 1``.
    """
    if abs(q - 1.0) < 1e-9:
        return von_neumann_entropy(rho, base=np.e)
    w = _eigs(rho)
    return float((1 - np.sum(w ** q)) / (q - 1))


def _partial_trace(rho, dims, keep):
    """Partial trace of ``rho`` over the subsystem(s) not in ``keep`` (dims = (dA, dB))."""
    dA, dB = dims
    r = np.asarray(rho, dtype=complex).reshape(dA, dB, dA, dB)
    if keep == 0:
        return np.einsum("ijkj->ik", r)
    return np.einsum("ijil->jl", r)


def conditional_entropy(rho_ab, dims, base: float = 2.0) -> float:
    """
    Quantum conditional entropy ``S(A|B) = S(AB) - S(B)`` for a bipartite state with
    subsystem dimensions ``dims = (dA, dB)``. Negative values witness entanglement (a Bell
    state gives ``-1``).
    """
    rho_b = _partial_trace(rho_ab, dims, keep=1)
    return von_neumann_entropy(rho_ab, base) - von_neumann_entropy(rho_b, base)


def quantum_mutual_information(rho_ab, dims, base: float = 2.0) -> float:
    """
    Quantum mutual information ``I(A:B) = S(A) + S(B) - S(AB)`` -- the total (classical +
    quantum) correlation between the subsystems. Zero for a product state, ``2`` bits for a
    Bell state.
    """
    rho_a = _partial_trace(rho_ab, dims, keep=0)
    rho_b = _partial_trace(rho_ab, dims, keep=1)
    return (von_neumann_entropy(rho_a, base) + von_neumann_entropy(rho_b, base)
            - von_neumann_entropy(rho_ab, base))


def entanglement_entropy_pure(state, dims, base: float = 2.0) -> float:
    """
    Bipartite entanglement entropy of a *pure* state: the von Neumann entropy of either
    reduced density matrix. Zero for a product state, ``1`` bit for a Bell pair; equals the
    Shannon entropy of the squared Schmidt coefficients.
    """
    psi = np.asarray(state, dtype=complex).reshape(dims)
    s = np.linalg.svd(psi, compute_uv=False)
    p = (s ** 2)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)) / np.log(base))
