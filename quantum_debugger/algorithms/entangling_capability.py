"""
Entangling capability -- the Meyer-Wallach measure.

An ansatz that cannot entangle can only reach product states, no matter how many
parameters it has. The **Meyer-Wallach** ``Q`` measures the global (multipartite)
entanglement of a state as the average single-qubit mixedness,

    Q = 2 (1 - (1/n) sum_k Tr[rho_k^2]),

which is ``0`` for a product state and ``1`` for a maximally entangled state (GHZ, Bell). The
ansatz's **entangling capability** is ``Q`` averaged over random parameters. This module
computes both, verified against product/GHZ states and against the intuition that adding
entangling layers raises the capability.
"""

import numpy as np

from .variational_ansatz import hardware_efficient_ansatz, ansatz_num_params


def _single_qubit_purity(state, q, n) -> float:
    psi = np.asarray(state, dtype=complex).reshape([2] * n)
    axes = tuple(a for a in range(n) if a != q)
    rho = np.tensordot(psi, psi.conj(), axes=(axes, axes))
    return float(np.real(np.trace(rho @ rho)))


def meyer_wallach(state) -> float:
    """
    Meyer-Wallach global entanglement ``Q = 2(1 - (1/n) sum_k Tr[rho_k^2])`` of a pure state.
    ``0`` for a product state, ``1`` for a maximally entangled (GHZ/Bell) state. Verified on
    both.
    """
    psi = np.asarray(state, dtype=complex)
    n = int(round(np.log2(len(psi))))
    avg_purity = np.mean([_single_qubit_purity(psi, q, n) for q in range(n)])
    return float(2 * (1 - avg_purity))


def entangling_capability(n: int, layers: int, samples: int = 200, seed: int = 0) -> float:
    """
    Entangling capability of the ansatz: the Meyer-Wallach ``Q`` averaged over random
    parameters. Higher means the ansatz reaches more-entangled states; verified to grow when
    entangling layers are added.
    """
    rng = np.random.default_rng(seed)
    npar = ansatz_num_params(n, layers)
    return float(np.mean([
        meyer_wallach(hardware_efficient_ansatz(rng.uniform(0, 2 * np.pi, npar), n, layers))
        for _ in range(samples)]))


def average_entanglement(states) -> float:
    """Mean Meyer-Wallach entanglement over a list of states."""
    return float(np.mean([meyer_wallach(s) for s in states]))


def is_product_state(state, atol: float = 1e-9) -> bool:
    """True iff a pure state is a product state (Meyer-Wallach ``Q = 0``) -- reachable by a
    non-entangling ansatz."""
    return bool(meyer_wallach(state) < atol)
