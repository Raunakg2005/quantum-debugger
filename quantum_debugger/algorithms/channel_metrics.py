"""
Channel characterization metrics.

A noisy gate is a quantum channel; several complementary numbers summarize how well it
implements a target unitary ``U``:

* **Entanglement fidelity** ``F_e = (1/d^2) sum_k |Tr(U^dagger K_k)|^2`` and the **average
  gate fidelity** ``F_avg = (d F_e + 1)/(d+1)`` -- how close the channel is to ``U`` on
  average.
* **Unitarity** -- how *coherent* the channel is, ``1`` for any unitary and less for a
  channel with incoherent (stochastic) noise, computed from the non-identity block of the
  Pauli transfer matrix.
* The **Choi matrix** -- the channel's state representation (positive, trace ``d``), from
  which everything else can be derived.

Verified: fidelities are 1 for an exact unitary, unitarity is 1 for unitaries and drops
under depolarizing noise, and the Choi matrix is a valid (CP) state.
"""

import numpy as np
from itertools import product

_P1 = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def _pauli_basis(n):
    for labels in product("IXYZ", repeat=n):
        M = np.array([[1.0]], dtype=complex)
        for ch in reversed(labels):
            M = np.kron(M, _P1[ch])
        yield M


def _apply_channel(kraus, rho):
    return sum(K @ rho @ K.conj().T for K in kraus)


def choi_matrix(kraus, d: int) -> np.ndarray:
    """
    Choi matrix ``sum_k (I (x) K_k) |Omega><Omega| (I (x) K_k)^dagger`` of a channel given by
    Kraus operators, with ``|Omega> = sum_i |ii>``. Positive semi-definite with trace ``d``
    for a trace-preserving channel -- the channel-state duality.
    """
    omega = np.zeros(d * d, dtype=complex)
    for i in range(d):
        omega[i * d + i] = 1.0
    rho = np.outer(omega, omega.conj())
    out = np.zeros((d * d, d * d), dtype=complex)
    for K in kraus:
        IK = np.kron(np.eye(d), K)
        out += IK @ rho @ IK.conj().T
    return out


def entanglement_fidelity(kraus, U) -> float:
    """
    Entanglement fidelity ``F_e = (1/d^2) sum_k |Tr(U^dagger K_k)|^2`` between a channel and
    target unitary ``U``. ``1`` iff the channel equals ``U``.
    """
    U = np.asarray(U, dtype=complex)
    d = U.shape[0]
    return float(sum(abs(np.trace(U.conj().T @ K)) ** 2 for K in kraus) / d ** 2)


def average_gate_fidelity(kraus, U) -> float:
    """Average gate fidelity ``F_avg = (d F_e + 1)/(d+1)`` -- the Haar-averaged state fidelity
    between the channel and ``U``. ``1`` for an exact implementation."""
    d = np.asarray(U).shape[0]
    return float((d * entanglement_fidelity(kraus, U) + 1) / (d + 1))


def pauli_transfer_matrix(kraus, n: int) -> np.ndarray:
    """Pauli transfer matrix ``R_ij = (1/d) Tr(P_i E(P_j))`` of an ``n``-qubit channel -- the
    real matrix representing the channel on the Pauli basis."""
    d = 2 ** n
    paulis = list(_pauli_basis(n))
    R = np.zeros((len(paulis), len(paulis)))
    for i, Pi in enumerate(paulis):
        for j, Pj in enumerate(paulis):
            R[i, j] = np.real(np.trace(Pi @ _apply_channel(kraus, Pj))) / d
    return R


def unitarity(kraus, n: int = 1) -> float:
    """
    Unitarity of a channel: ``(1/(d^2-1)) sum_{i,j != I} R_ij^2`` over the non-identity block
    of the Pauli transfer matrix. ``1`` for any unitary (an orthogonal block) and smaller for
    incoherent noise -- e.g. ``p^2`` for depolarizing with PTM decay ``p``. Verified.
    """
    R = pauli_transfer_matrix(kraus, n)
    d = 2 ** n
    block = R[1:, 1:]
    return float(np.sum(block ** 2) / (d ** 2 - 1))
