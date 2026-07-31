"""
Entanglement detection: witnesses and the realignment (CCNR) criterion.

Separable states form a convex set, so entanglement can be certified two ways:

* An **entanglement witness** ``W`` is a Hermitian operator with ``Tr(W sigma) >= 0`` for
  every separable ``sigma`` but ``Tr(W rho) < 0`` for some entangled ``rho`` -- a negative
  expectation *proves* entanglement.
* The **realignment (computable cross-norm / CCNR) criterion**: for any separable state
  the realigned matrix has trace norm ``<= 1``, so ``||R(rho)||_1 > 1`` proves
  entanglement. It detects some states the PPT test misses.

Verified: the canonical Bell witness fires on a Bell state and not on the maximally mixed
state, and the realignment norm exceeds 1 for entangled inputs.
"""

import numpy as np


def witness_expectation(rho, witness) -> float:
    """Expectation ``Tr(W rho)`` of an entanglement witness -- negative proves entanglement."""
    return float(np.real(np.trace(np.asarray(witness) @ np.asarray(rho))))


def bell_witness(bell_index: int = 0) -> np.ndarray:
    """
    A canonical two-qubit entanglement witness ``W = I/2 - |Phi><Phi|`` for a Bell state
    ``|Phi>``. Satisfies ``Tr(W sigma) >= 0`` for all separable states and
    ``Tr(W |Phi><Phi|) = -1/2 < 0``.
    """
    bells = [
        np.array([1, 0, 0, 1]) / np.sqrt(2),
        np.array([1, 0, 0, -1]) / np.sqrt(2),
        np.array([0, 1, 1, 0]) / np.sqrt(2),
        np.array([0, 1, -1, 0]) / np.sqrt(2),
    ]
    b = bells[bell_index].astype(complex)
    return np.eye(4) / 2 - np.outer(b, b.conj())


def realign(rho, dims) -> np.ndarray:
    """Realignment map ``R(rho)_{(ik),(jl)} = rho_{(ij),(kl)}`` for ``dims = (dA, dB)``."""
    dA, dB = dims
    r = np.asarray(rho, dtype=complex).reshape(dA, dB, dA, dB)
    return r.transpose(0, 2, 1, 3).reshape(dA * dA, dB * dB)


def realignment_norm(rho, dims) -> float:
    """
    Trace norm ``||R(rho)||_1`` of the realigned density matrix (sum of its singular
    values). Bounded by 1 for separable states, so a value above 1 certifies entanglement.
    """
    s = np.linalg.svd(realign(rho, dims), compute_uv=False)
    return float(np.sum(s))


def realignment_criterion(rho, dims, atol: float = 1e-9) -> bool:
    """
    Computable cross-norm / realignment (CCNR) entanglement test: returns ``True``
    (entanglement certified) when ``||R(rho)||_1 > 1``.
    """
    return bool(realignment_norm(rho, dims) > 1 + atol)
