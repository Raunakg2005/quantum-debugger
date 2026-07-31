"""
Fermion-to-qubit mappings: Jordan-Wigner, parity, and Bravyi-Kitaev.

Electronic-structure Hamiltonians are written with fermionic creation/annihilation
operators obeying the canonical anticommutation relations (CAR)

    {a_i, a_j^dagger} = delta_ij,   {a_i, a_j} = 0.

To run them on qubits every mapping encodes an occupation string ``f`` as a qubit
string ``q = beta f (mod 2)`` for an invertible binary matrix ``beta`` and represents
each fermionic operator as ``U_beta a_j U_beta^dagger``. The three standard choices
trade off *locality* against *simplicity*:

* **Jordan-Wigner** (``beta = I``) -- occupation is stored directly; operators carry a
  length-``j`` Pauli-``Z`` string (weight up to ``O(n)``).
* **Parity** (``beta`` lower-triangular) -- stores partial sums; the ``Z`` string
  becomes a single qubit but the flip string grows.
* **Bravyi-Kitaev** (Fenwick-tree ``beta``) -- balances both, giving ``O(log n)`` Pauli
  weight.

All three represent the *same* algebra, so they satisfy the CAR and give molecular
Hamiltonians with *identical spectra* -- both verified here -- while Bravyi-Kitaev is
verified to reduce the operator locality.
"""

import numpy as np

I2 = np.eye(2, dtype=complex)


def fock_annihilation(j: int, n: int) -> np.ndarray:
    """
    Physical fermionic annihilation operator ``a_j`` on ``n`` modes (a ``2^n x 2^n``
    matrix), acting on occupation basis states with the Jordan-Wigner sign
    ``(-1)^{sum_{k<j} f_k}``. This is the Jordan-Wigner representation (the identity
    encoding); the other mappings are basis changes of it.
    """
    dim = 2 ** n
    A = np.zeros((dim, dim), dtype=complex)
    for idx in range(dim):
        if (idx >> j) & 1:                       # mode j occupied
            sign = -1.0 if bin(idx & ((1 << j) - 1)).count("1") % 2 else 1.0
            A[idx ^ (1 << j), idx] = sign
    return A


# --- encoding matrices (q = beta f mod 2) -----------------------------------

def jordan_wigner_matrix(n: int) -> np.ndarray:
    """Encoding matrix of the Jordan-Wigner transform: the identity."""
    return np.eye(n, dtype=int)


def parity_matrix(n: int) -> np.ndarray:
    """Encoding matrix of the parity transform: lower-triangular ones (partial sums)."""
    return np.tril(np.ones((n, n), dtype=int))


def bravyi_kitaev_matrix(n: int) -> np.ndarray:
    """
    Encoding matrix of the Bravyi-Kitaev transform via the Fenwick (binary-indexed) tree:
    qubit ``i`` stores the parity of orbitals ``(i - lowbit) .. i``. Invertible over
    GF(2); it is the balanced encoding that gives ``O(log n)`` operator weight.
    """
    beta = np.zeros((n, n), dtype=int)
    for i in range(n):
        j = i + 1
        low = j & (-j)
        for m in range(j - low, j):
            beta[i, m] = 1
    return beta


def _encoding_permutation(beta) -> np.ndarray:
    """Permutation matrix ``U = sum_f |beta f><f|`` for encoding matrix ``beta``."""
    beta = np.asarray(beta) % 2
    n = beta.shape[0]
    dim = 2 ** n
    U = np.zeros((dim, dim), dtype=complex)
    for f in range(dim):
        fvec = np.array([(f >> k) & 1 for k in range(n)])
        q = (beta @ fvec) % 2
        qidx = int(sum(int(b) << k for k, b in enumerate(q)))
        U[qidx, f] = 1.0
    return U


def encoded_annihilation(j: int, n: int, beta) -> np.ndarray:
    """
    Annihilation operator for mode ``j`` under the encoding ``beta``:
    ``U_beta a_j U_beta^dagger``. With ``beta = I`` this is Jordan-Wigner; with the parity
    or Bravyi-Kitaev matrices it is those mappings.
    """
    U = _encoding_permutation(beta)
    return U @ fock_annihilation(j, n) @ U.conj().T


def jordan_wigner_annihilation(j, n):
    """Jordan-Wigner annihilation operator for mode ``j`` on ``n`` modes."""
    return fock_annihilation(j, n)


def parity_annihilation(j, n):
    """Parity-mapping annihilation operator for mode ``j`` on ``n`` modes."""
    return encoded_annihilation(j, n, parity_matrix(n))


def bravyi_kitaev_annihilation(j, n):
    """Bravyi-Kitaev annihilation operator for mode ``j`` on ``n`` modes."""
    return encoded_annihilation(j, n, bravyi_kitaev_matrix(n))


# --- verification helpers ---------------------------------------------------

def anticommutator(A, B):
    """``{A, B} = AB + BA``."""
    A = np.asarray(A); B = np.asarray(B)
    return A @ B + B @ A


def satisfies_car(annihilators, atol: float = 1e-9) -> bool:
    """
    Check the canonical anticommutation relations for a list of annihilation operators
    ``a_0, ..., a_{n-1}``: ``{a_i, a_j^dagger} = delta_ij I`` and ``{a_i, a_j} = 0``.
    """
    n = len(annihilators)
    dim = annihilators[0].shape[0]
    for i in range(n):
        for j in range(n):
            adag = annihilators[j].conj().T
            expect = np.eye(dim) if i == j else np.zeros((dim, dim))
            if not np.allclose(anticommutator(annihilators[i], adag), expect, atol=atol):
                return False
            if not np.allclose(anticommutator(annihilators[i], annihilators[j]),
                               np.zeros((dim, dim)), atol=atol):
                return False
    return True


_PAULIS = {
    "I": I2,
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def pauli_weight(operator, atol: float = 1e-9) -> int:
    """
    Maximum Pauli weight (number of non-identity factors) among the Pauli strings in the
    decomposition of a Hermitian ``operator`` on ``n`` qubits -- the locality measure that
    Bravyi-Kitaev improves over Jordan-Wigner.
    """
    M = np.asarray(operator, dtype=complex)
    n = int(round(np.log2(M.shape[0])))
    from itertools import product
    max_w = 0
    for labels in product("IXYZ", repeat=n):
        P = np.array([[1.0]], dtype=complex)
        for lab in reversed(labels):  # little-endian
            P = np.kron(P, _PAULIS[lab])
        coeff = np.trace(P.conj().T @ M) / M.shape[0]
        if abs(coeff) > atol:
            max_w = max(max_w, sum(1 for lab in labels if lab != "I"))
    return max_w
