"""
Uncertainty relations (Robertson & Maassen-Uffink)

Two rigorous forms of Heisenberg's principle, both verified state-by-state:

  * **Robertson (1929)**: for any observables A, B and any state,

        dA * dB >= |<[A, B]>| / 2.

    For X and Y on a Z eigenstate the bound is *tight*: dX = dY = 1 and
    ``|<[X,Y]>|/2 = |<Z>| = 1``.

  * **Maassen-Uffink (1988), entropic**: measurement entropies obey

        H(A) + H(B) >= -log2 max_{i,j} |<a_i|b_j>|^2,

    which for complementary qubit bases (X and Z, mutually unbiased) reads
    ``H(X) + H(Z) >= 1`` bit -- with equality exactly on an eigenstate of either
    observable. Unlike Robertson's bound, the right-hand side never degenerates to
    zero: complementarity is unconditional.
"""

import numpy as np


def robertson_bound(A, B, state_vector) -> dict:
    """
    Evaluate Robertson's uncertainty relation for observables ``A``, ``B`` on a
    pure state: returns dict with ``dA``, ``dB``, ``product`` (``dA * dB``),
    ``bound`` (``|<[A,B]>|/2``), and ``satisfied``.
    """
    psi = np.asarray(state_vector, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    A = np.asarray(A, dtype=complex)
    B = np.asarray(B, dtype=complex)

    def var(M):
        m = np.real(psi.conj() @ M @ psi)
        m2 = np.real(psi.conj() @ (M @ M) @ psi)
        return max(0.0, m2 - m**2)

    dA, dB = np.sqrt(var(A)), np.sqrt(var(B))
    comm = A @ B - B @ A
    bound = abs(psi.conj() @ comm @ psi) / 2
    return {
        "dA": float(dA),
        "dB": float(dB),
        "product": float(dA * dB),
        "bound": float(bound),
        "satisfied": bool(dA * dB >= bound - 1e-12),
    }


def entropic_uncertainty(A, B, state_vector) -> dict:
    """
    Evaluate the Maassen-Uffink entropic uncertainty relation: measure ``A`` and
    ``B`` (Hermitian matrices) on the pure state, compute the Shannon entropies of
    the two outcome distributions, and compare with ``-log2 c`` where ``c`` is the
    largest squared overlap between any eigenvector of A and any of B.

    Returns dict with ``H_A``, ``H_B``, ``sum``, ``bound``, and ``satisfied``.
    """
    psi = np.asarray(state_vector, dtype=complex)
    psi = psi / np.linalg.norm(psi)

    def outcome_entropy(M):
        _, vecs = np.linalg.eigh(np.asarray(M, dtype=complex))
        probs = np.abs(vecs.conj().T @ psi) ** 2
        probs = probs[probs > 1e-15]
        return float(-np.sum(probs * np.log2(probs))), vecs

    H_A, vecs_a = outcome_entropy(A)
    H_B, vecs_b = outcome_entropy(B)
    overlaps = np.abs(vecs_a.conj().T @ vecs_b) ** 2
    bound = float(-np.log2(np.max(overlaps)))
    return {
        "H_A": H_A,
        "H_B": H_B,
        "sum": H_A + H_B,
        "bound": bound,
        "satisfied": bool(H_A + H_B >= bound - 1e-9),
    }
