"""
Entanglement measures for two-qubit and bipartite states.

For two qubits, Wootters' **concurrence** gives entanglement in closed form even for
mixed states, and the **entanglement of formation** (the minimal average pure-state
entanglement in any decomposition) follows from it. For pure bipartite states the
**Schmidt decomposition** exposes the entanglement directly. All are verified against
Bell states (maximal), product states (zero), and the Werner-state entanglement
threshold.
"""

import numpy as np

_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_YY = np.kron(_Y, _Y)


def concurrence(rho) -> float:
    """
    Wootters concurrence of a two-qubit density matrix:
    ``C = max(0, l1 - l2 - l3 - l4)`` where ``l_i`` are the square roots of the eigenvalues
    (descending) of ``rho (Y (x) Y) rho^* (Y (x) Y)``. ``1`` for a Bell state, ``0`` for a
    separable state.
    """
    rho = np.asarray(rho, dtype=complex)
    R = rho @ _YY @ rho.conj() @ _YY
    ev = np.linalg.eigvals(R)
    ls = np.sort(np.sqrt(np.clip(np.real(ev), 0, None)))[::-1]
    return float(max(0.0, ls[0] - ls[1] - ls[2] - ls[3]))


def _binary_entropy(x):
    if x <= 0 or x >= 1:
        return 0.0
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


def entanglement_of_formation(rho) -> float:
    """
    Entanglement of formation of a two-qubit state, from the concurrence ``C`` via
    ``E = h((1 + sqrt(1 - C^2))/2)`` with ``h`` the binary entropy. The minimal average
    entanglement (in bits) over all pure-state decompositions; ``1`` for a Bell pair.
    """
    C = concurrence(rho)
    return float(_binary_entropy((1 + np.sqrt(max(1 - C**2, 0.0))) / 2))


def tangle(rho) -> float:
    """Tangle ``C^2`` (concurrence squared) -- the measure obeying CKW monogamy."""
    return float(concurrence(rho) ** 2)


def schmidt_coefficients(state, dims) -> np.ndarray:
    """
    Schmidt coefficients (descending singular values) of a bipartite pure ``state`` with
    subsystem dimensions ``dims = (dA, dB)``. Their squares sum to 1; a single nonzero
    value means the state is a product state.
    """
    psi = np.asarray(state, dtype=complex).reshape(dims)
    return np.sort(np.linalg.svd(psi, compute_uv=False))[::-1]


def schmidt_rank(state, dims, atol: float = 1e-9) -> int:
    """
    Schmidt rank: the number of non-zero Schmidt coefficients. ``1`` iff the state is a
    product state; larger means more entanglement structure.
    """
    return int(np.sum(schmidt_coefficients(state, dims) > atol))
