"""
Two-qubit gate synthesis and the optimal CNOT count.

Any two-qubit unitary can be built from at most **three** CNOTs plus single-qubit gates.
Exactly how many it needs is a *local invariant* -- unchanged by pre/post single-qubit
gates -- captured by the **Makhlin invariants** ``(G1, G2)`` computed in the magic basis.
This module computes those invariants and classifies the minimal CNOT count (0 for local
gates, 1 for CNOT/CZ, 2 for iSWAP, 3 for SWAP and generic gates), and detects when a gate
is a pure tensor product. Verified against the canonical gates.
"""

import numpy as np

# Magic basis (maps the computational basis to the Bell basis with the right phases).
_Q = np.array([
    [1, 0, 0, 1j],
    [0, 1j, 1, 0],
    [0, 1j, -1, 0],
    [1, 0, 0, -1j],
], dtype=complex) / np.sqrt(2)


def makhlin_invariants(U):
    """
    The Makhlin local invariants ``(G1, G2)`` of a two-qubit unitary, computed from
    ``M = (Q^dagger U Q)^T (Q^dagger U Q)`` as ``G1 = tr(M)^2 / (16 det U)`` and
    ``G2 = (tr(M)^2 - tr(M^2)) / (4 det U)``. Invariant under single-qubit gates -- two gates
    are locally equivalent iff their invariants match.
    """
    U = np.asarray(U, dtype=complex)
    Um = _Q.conj().T @ U @ _Q
    M = Um.T @ Um
    detU = np.linalg.det(U)
    m = np.trace(M)
    G1 = m * m / (16 * detU)
    G2 = (m * m - np.trace(M @ M)) / (4 * detU)
    return complex(G1), complex(G2)


def is_local(U, atol: float = 1e-9) -> bool:
    """True iff a two-qubit ``U`` is a tensor product ``A (x) B`` of single-qubit gates (needs
    zero CNOTs) -- detected via the Makhlin invariants ``(G1, G2) = (1, 3)``."""
    G1, G2 = makhlin_invariants(U)
    return bool(abs(G1 - 1) < atol and abs(G2 - 3) < atol)


def locally_equivalent(U, V, atol: float = 1e-6) -> bool:
    """True iff two two-qubit gates are locally equivalent (equal Makhlin invariants) -- so
    one becomes the other with only single-qubit gates."""
    a1, a2 = makhlin_invariants(U)
    b1, b2 = makhlin_invariants(V)
    return bool(abs(a1 - b1) < atol and abs(a2 - b2) < atol)


def _M_normalized(U):
    """``M = (Q^dagger U' Q)^T (Q^dagger U' Q)`` for ``U'`` normalized to SU(4). Its spectrum
    is a local invariant, and ``tr(M)`` encodes the CNOT count."""
    U = np.asarray(U, dtype=complex)
    U = U / np.linalg.det(U) ** 0.25         # into SU(4)
    Um = _Q.conj().T @ U @ _Q
    return Um.T @ Um


def cnot_count(U, atol: float = 1e-6) -> int:
    """
    Minimal number of CNOTs (0-3) to implement a two-qubit ``U`` (Shende-Bullock-Markov):
    from ``M`` (in the magic basis, ``U`` normalized to SU(4)), a gate needs **3** CNOTs iff
    ``tr(M)`` is not real; among real ``tr(M)`` it needs **0** iff ``tr(M)=4`` (local),
    **1** iff the spectrum is ``{i,i,-i,-i}`` (``tr(M)=0``, ``tr(M^2)=-4``), and **2**
    otherwise. Verified: local=0, CNOT/CZ=1, iSWAP=2, SWAP and generic=3.
    """
    M = _M_normalized(U)
    tr = np.trace(M)
    tr2 = np.trace(M @ M)
    if abs(tr.imag) > atol:
        return 3
    if abs(tr - 4) < atol:
        return 0
    if abs(tr) < atol and abs(tr2 + 4) < atol:
        return 1
    return 2
