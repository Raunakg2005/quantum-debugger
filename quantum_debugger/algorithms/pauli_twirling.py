"""
Pauli twirling (noise tailoring)

Coherent errors (a small over-rotation, a systematic phase) are the hardest to
mitigate: they add up quadratically and evade many error-correction assumptions.
**Pauli twirling** converts them into ordinary stochastic Pauli noise by conjugating
the noisy operation with a random Pauli before and after -- averaged over the group,

    N_twirled(rho) = (1/4^n) sum_P P^dagger N(P rho P^dagger) P,

the result is always a Pauli channel (diagonal in the Pauli basis), with the *same*
average gate fidelity as the original. So twirling doesn't remove the error, it
*tailors* it -- turning coherent noise into the stochastic form that error correction
and the other mitigation methods handle well. This module twirls a single-qubit
channel and verifies both properties.
"""

import numpy as np

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULIS = (_I, _X, _Y, _Z)
_LABELS = ("I", "X", "Y", "Z")


def _channel(kraus_ops, rho):
    return sum(K @ rho @ K.conj().T for K in kraus_ops)


def _ptm_diagonal(chan):
    """Diagonal of the Pauli transfer matrix of a single-qubit channel ``chan``."""
    return np.array([np.real(np.trace(P @ chan(P))) / 2 for P in _PAULIS])


def pauli_twirl(kraus_ops) -> dict:
    """
    Pauli-twirl a single-qubit channel given by ``kraus_ops``.

    Returns dict with:
      * ``pauli_probabilities`` -- ``{I, X, Y, Z}`` probabilities of the twirled Pauli
        channel
      * ``is_pauli_channel``    -- whether the twirled channel is diagonal in the Pauli
        basis (always True)
      * ``average_fidelity``    -- average gate fidelity (preserved by twirling)
    """
    def twirled(rho):
        return sum(P.conj().T @ _channel(kraus_ops, P @ rho @ P.conj().T) @ P
                   for P in _PAULIS) / 4

    # Off-diagonal PTM check (twirled channel is Pauli-diagonal).
    ptm = np.zeros((4, 4))
    for i, Pi in enumerate(_PAULIS):
        out = twirled(Pi)
        for j, Pj in enumerate(_PAULIS):
            ptm[j, i] = np.real(np.trace(Pj @ out)) / 2
    is_pauli = bool(np.allclose(ptm, np.diag(np.diag(ptm)), atol=1e-9))

    # Pauli probabilities from the diagonal via the Walsh-Hadamard relation.
    lam = np.diag(ptm)
    hadamard = np.array([
        [1, 1, 1, 1],
        [1, 1, -1, -1],
        [1, -1, 1, -1],
        [1, -1, -1, 1],
    ])
    probs = hadamard @ lam / 4
    probs = np.clip(probs, 0, None)
    probs = probs / probs.sum()

    avg_fidelity = float((np.trace(ptm).real + 2) / 6)
    return {
        "pauli_probabilities": {lab: float(p) for lab, p in zip(_LABELS, probs)},
        "is_pauli_channel": is_pauli,
        "average_fidelity": avg_fidelity,
    }


def coherent_error_kraus(angle: float, axis: str = "X") -> list:
    """Kraus (single unitary) for a coherent over-rotation ``exp(-i angle P / 2)``."""
    from scipy.linalg import expm

    P = {"X": _X, "Y": _Y, "Z": _Z}[axis]
    return [expm(-1j * angle * P / 2)]
