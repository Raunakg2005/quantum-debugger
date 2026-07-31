"""
Popescu-Rohrlich boxes and no-signaling correlations.

Quantum mechanics does not saturate the algebraic CHSH maximum of 4 -- it stops at Tsirelson's
``2 sqrt2``. A **Popescu-Rohrlich (PR) box** is a hypothetical device that *does* reach ``4``
while still respecting **no-signaling** (neither party's marginal depends on the other's
setting), so it cannot be used to communicate faster than light. PR boxes are therefore
super-quantum but not unphysical by relativity alone -- which is why "why is quantum mechanics
only as nonlocal as it is?" is a deep question. This module builds the PR-box correlations,
checks no-signaling, and shows the PR box gives CHSH ``= 4`` while local boxes stay at ``2``.
"""

import numpy as np
from itertools import product


def pr_box_correlations():
    """
    The PR-box conditional distribution ``p(a,b|x,y)``: outputs satisfy ``a XOR b = x AND y`` and
    are otherwise uniform. Returned as a dict ``{(x,y): 2x2 array over (a,b)}``.
    """
    box = {}
    for x, y in product([0, 1], repeat=2):
        p = np.zeros((2, 2))
        for a, b in product([0, 1], repeat=2):
            p[a, b] = 0.5 if (a ^ b) == (x & y) else 0.0
        box[(x, y)] = p
    return box


def correlation_value(box, x, y) -> float:
    """The correlator ``E(x,y) = sum_{a,b} (-1)^{a+b} p(a,b|x,y)`` for a behaviour ``box``."""
    p = box[(x, y)]
    return float(sum((-1) ** (a + b) * p[a, b] for a in (0, 1) for b in (0, 1)))


def chsh_from_box(box) -> float:
    """CHSH value ``E(0,0)+E(0,1)+E(1,0)-E(1,1)`` of a behaviour -- ``4`` for the PR box, ``<=2``
    for local boxes, ``<=2 sqrt2`` for quantum."""
    return float(correlation_value(box, 0, 0) + correlation_value(box, 0, 1)
                 + correlation_value(box, 1, 0) - correlation_value(box, 1, 1))


def is_no_signaling(box, atol: float = 1e-9) -> bool:
    """
    No-signaling test: Alice's marginal ``p(a|x)`` must not depend on Bob's setting ``y`` and vice
    versa. Verified True for the PR box (so it cannot transmit information despite CHSH ``= 4``).
    """
    for x in (0, 1):
        m0 = box[(x, 0)].sum(axis=1)
        m1 = box[(x, 1)].sum(axis=1)
        if not np.allclose(m0, m1, atol=atol):
            return False
    for y in (0, 1):
        m0 = box[(0, y)].sum(axis=0)
        m1 = box[(1, y)].sum(axis=0)
        if not np.allclose(m0, m1, atol=atol):
            return False
    return True


def local_deterministic_box(a_func, b_func):
    """
    A local deterministic behaviour where Alice outputs ``a_func(x)`` and Bob ``b_func(y)`` --
    the building blocks of the local (classical) polytope, all with CHSH ``<= 2``.
    """
    box = {}
    for x, y in product([0, 1], repeat=2):
        p = np.zeros((2, 2))
        p[a_func(x), b_func(y)] = 1.0
        box[(x, y)] = p
    return box


def pr_box_is_superquantum() -> bool:
    """Verify the PR box exceeds Tsirelson's bound: its CHSH value ``4`` is above ``2 sqrt2`` --
    super-quantum yet no-signaling."""
    return bool(chsh_from_box(pr_box_correlations()) > 2 * np.sqrt(2))
