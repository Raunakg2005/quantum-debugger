"""
Communication complexity.

Two parties, Alice with ``x`` and Bob with ``y``, want to compute ``f(x, y)`` exchanging as few
bits as possible. The model exposes clean quantum-vs-classical gaps:

* **Equality** ``EQ(x,y) = [x == y]`` -- ``n+1`` bits deterministically, but only ``O(log n)`` with
  shared randomness or a **quantum fingerprint** (an exponential saving).
* **Inner product** ``IP(x,y) = <x,y> mod 2`` -- ``Theta(n)`` even with quantum communication and
  entanglement (no asymptotic quantum advantage).
* **Disjointness** -- ``Theta(n)`` classically, ``Theta(sqrt n)`` quantum (a quadratic gap).

This module returns these complexities and the quantum fingerprint length, verified against the
closed forms and their separations.
"""

import numpy as np


def equality_deterministic(n: int) -> int:
    """Deterministic communication complexity of Equality on ``n``-bit inputs: ``n + 1`` bits
    (Alice must essentially send her whole string)."""
    return int(n + 1)


def equality_randomized(n: int, error: float = 0.1) -> int:
    """Randomized (shared-coin) communication complexity of Equality: ``O(log(n/error))`` bits --
    an exponential saving over the deterministic ``n+1``."""
    return int(np.ceil(np.log2(n / error))) + 1


def quantum_fingerprint_length(n: int, error: float = 0.1) -> int:
    """
    Length of a quantum fingerprint for Equality (simultaneous-message model, no shared
    randomness): ``O(log n)`` qubits -- an exponential saving over the classical ``Omega(sqrt n)``
    fingerprint. Verified below the deterministic cost.
    """
    return int(np.ceil(np.log2(n))) + 1


def inner_product_complexity(n: int) -> dict:
    """Inner-product communication complexity: ``Theta(n)`` both classically and quantumly (with
    entanglement) -- the canonical problem with *no* quantum advantage."""
    return {"classical": n, "quantum": n}


def disjointness_complexity(n: int) -> dict:
    """Set-disjointness communication complexity: ``Theta(n)`` classical vs ``Theta(sqrt n)``
    quantum -- a provable quadratic quantum advantage."""
    return {"classical": n, "quantum": int(np.ceil(np.sqrt(n)))}


def equality_exponential_saving(n: int) -> bool:
    """Verify the exponential quantum/randomized saving for Equality: the fingerprint length is
    ``O(log n)`` while deterministic communication is ``n+1``."""
    return bool(quantum_fingerprint_length(n) < equality_deterministic(n) and
                quantum_fingerprint_length(n) <= 2 * np.log2(max(n, 2)) + 2)


def has_quantum_advantage(counts: dict) -> bool:
    """True iff a communication problem has an asymptotic quantum advantage (quantum ``<``
    classical) -- ``False`` for inner product, ``True`` for disjointness."""
    return bool(counts["quantum"] < counts["classical"])
