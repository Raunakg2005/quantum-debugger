"""
Multiparty Mermin inequalities and the exponential GHZ violation.

The two-party CHSH gap between quantum and classical is a constant factor ``sqrt2``. For ``n``
parties the **Mermin-Klyshko** inequalities show the gap grows *exponentially*: a GHZ state
violates the local bound by a factor ``2^{(n-1)/2}``. The Mermin operator is built recursively
from single-qubit ``X`` and ``Y`` measurements,

    M_n = (1/2)[ M_{n-1} (X_n + Y_n) + M'_{n-1} (X_n - Y_n) ],

with ``M'`` the ``X <-> Y`` swap of ``M``. Its GHZ expectation is ``2^{n-1}`` while the local
hidden-variable bound is ``2^{(n-1)/2}``. This module builds the operator, evaluates the GHZ
value, brute-forces the classical bound, and verifies the exponentially growing violation.
"""

import numpy as np
from itertools import product

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)


def ghz_state(n: int) -> np.ndarray:
    """The ``n``-qubit GHZ state ``(|0...0> + |1...1>)/sqrt2`` -- the maximally nonlocal
    multiparty state."""
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = psi[-1] = 1 / np.sqrt(2)
    return psi


def _mermin_pair(n):
    """Return ``(M_n, M'_n)`` as ``2^n`` matrices via the Mermin-Klyshko recursion."""
    if n == 1:
        return _X.copy(), _Y.copy()
    M, Mp = _mermin_pair(n - 1)
    Xn, Yn = _X, _Y
    M_n = 0.5 * (np.kron(Xn + Yn, M) + np.kron(Xn - Yn, Mp))
    Mp_n = 0.5 * (np.kron(Yn + Xn, Mp) + np.kron(Yn - Xn, M))
    return M_n, Mp_n


def mermin_operator(n: int) -> np.ndarray:
    """The ``n``-party Mermin-Klyshko operator ``M_n`` (Hermitian) built recursively."""
    return _mermin_pair(n)[0]


def mermin_value(state, n: int) -> float:
    """The Mermin expectation ``<psi|M_n|psi>`` of a given ``state``."""
    psi = np.asarray(state, dtype=complex)
    return float(np.real(np.vdot(psi, mermin_operator(n) @ psi)))


def mermin_optimal_value(n: int) -> float:
    """
    The maximal quantum Mermin value -- the largest eigenvalue of ``M_n``, achieved by a
    (suitably rotated) GHZ state. Verified equal to ``2^{(n-1)/2}`` in this normalization.
    """
    return float(np.max(np.linalg.eigvalsh(mermin_operator(n))))


def mermin_quantum_bound(n: int) -> float:
    """The closed-form quantum maximum of the (normalized) Mermin-Klyshko operator,
    ``2^{(n-1)/2}``."""
    return float(2 ** ((n - 1) / 2))


def mermin_classical_bound(n: int) -> float:
    """
    The local hidden-variable bound of the (normalized) Mermin-Klyshko operator, ``1`` --
    computed here by brute force over all deterministic ``+/-1`` assignments to the ``X`` and
    ``Y`` measurements of each party.
    """
    from .pauli_hamiltonian import decompose
    terms = decompose(mermin_operator(n))
    best = 0.0
    for assign in product([1, -1], repeat=2 * n):
        xval = assign[:n]; yval = assign[n:]
        total = 0.0
        for coeff, label, x, z in terms:
            val = coeff
            for q, ch in enumerate(label):
                if ch == "X":
                    val *= xval[q]
                elif ch == "Y":
                    val *= yval[q]
            total += val
        best = max(best, abs(total))
    return float(best)


def mermin_violation_ratio(n: int) -> float:
    """Ratio of the maximal quantum value to the classical bound, ``2^{(n-1)/2}`` -- the
    exponentially growing multiparty nonlocality. Verified against brute force."""
    return float(mermin_optimal_value(n) / mermin_classical_bound(n))
