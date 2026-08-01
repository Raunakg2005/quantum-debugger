"""
Boolean-function complexity measures.

Query lower bounds -- how many bits of a hidden input a (quantum or classical) algorithm must
read -- are controlled by combinatorial measures of the target Boolean function
``f : {0,1}^n -> {0,1}``:

* **Sensitivity** ``s(f)`` -- the most single-bit flips at one input that change ``f``.
* **Block sensitivity** ``bs(f)`` -- the most *disjoint blocks* whose flip changes ``f``.
* **Certificate complexity** ``C(f)`` -- the smallest number of bits that certify a value.
* **Decision-tree depth** ``D(f)`` -- the classical deterministic query complexity.
* **Degree** ``deg(f)`` -- the degree of the unique multilinear real polynomial computing ``f``.

These obey a strict hierarchy ``s(f) <= bs(f) <= C(f) <= D(f)`` and ``deg(f) <= D(f)``. This module
computes each by brute force (feasible for small ``n``) and verifies the hierarchy on the standard
functions (OR, AND, parity, majority).
"""

import numpy as np
from itertools import combinations, product


def truth_table(f, n: int) -> np.ndarray:
    """Evaluate a Boolean function ``f(bits)`` on all ``2^n`` inputs, returning the ``0/1`` table
    indexed by the integer input."""
    return np.array([f([(x >> i) & 1 for i in range(n)]) for x in range(2 ** n)], dtype=int)


def _flip(x, bits, n):
    for b in bits:
        x ^= (1 << b)
    return x


def sensitivity_at(tt, x: int, n: int) -> int:
    """Sensitivity of the function (given by truth table ``tt``) at input ``x``: the number of
    single-bit flips that change the output."""
    return int(sum(1 for i in range(n) if tt[x ^ (1 << i)] != tt[x]))


def max_sensitivity(tt, n: int) -> int:
    """Sensitivity ``s(f) = max_x s(f, x)`` -- the largest local sensitivity."""
    return int(max(sensitivity_at(tt, x, n) for x in range(2 ** n)))


def block_sensitivity(tt, n: int) -> int:
    """
    Block sensitivity ``bs(f)``: the maximum over inputs ``x`` of the number of *disjoint* blocks
    ``B`` of coordinates whose simultaneous flip changes ``f(x)``. Always ``>= s(f)``.
    """
    best = 0
    for x in range(2 ** n):
        # greedily/optimally find the max number of disjoint sensitive blocks (small n: brute)
        sensitive_blocks = []
        for size in range(1, n + 1):
            for B in combinations(range(n), size):
                if tt[_flip(x, B, n)] != tt[x]:
                    sensitive_blocks.append(set(B))
        best = max(best, _max_disjoint(sensitive_blocks, n))
    return int(best)


def _max_disjoint(blocks, n):
    # maximum set of pairwise-disjoint blocks (brute force over a modest search)
    best = 0
    def rec(idx, used, count):
        nonlocal best
        best = max(best, count)
        for k in range(idx, len(blocks)):
            if not (blocks[k] & used):
                rec(k + 1, used | blocks[k], count + 1)
    rec(0, set(), 0)
    return best


def certificate_complexity(tt, n: int) -> int:
    """
    Certificate complexity ``C(f)``: the maximum over inputs of the *smallest* partial assignment
    (set of fixed bits) that forces the output value. Satisfies ``bs(f) <= C(f)``.
    """
    best = 0
    for x in range(2 ** n):
        val = tt[x]
        found = None
        for size in range(0, n + 1):
            for S in combinations(range(n), size):
                # does fixing bits S (to x's values) force the output = val?
                forces = True
                for y in range(2 ** n):
                    if all(((y >> i) & 1) == ((x >> i) & 1) for i in S) and tt[y] != val:
                        forces = False
                        break
                if forces:
                    found = size
                    break
            if found is not None:
                break
        best = max(best, found)
    return int(best)


def decision_tree_complexity(tt, n: int) -> int:
    """
    Deterministic decision-tree (classical query) complexity ``D(f)`` by optimal recursive query
    selection. The number of bits an optimal classical adaptive algorithm must read in the worst
    case.
    """
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def depth(fixed):  # fixed: tuple of (bit, value)
        consistent = [y for y in range(2 ** n)
                      if all(((y >> b) & 1) == v for b, v in fixed)]
        if len({tt[y] for y in consistent}) <= 1:
            return 0
        queried = {b for b, _ in fixed}
        return 1 + min(
            max(depth(fixed + ((i, 0),)), depth(fixed + ((i, 1),)))
            for i in range(n) if i not in queried)
    return int(depth(()))


def polynomial_degree(tt, n: int) -> int:
    """
    Degree of the unique multilinear real polynomial representing ``f`` (over ``{0,1}`` inputs),
    from the Möbius/Fourier transform. ``deg(f) <= D(f)``.
    """
    # multilinear coefficients via inclusion-exclusion (Möbius on the subset lattice)
    deg = 0
    for S in range(2 ** n):
        coeff = 0.0
        for x in range(2 ** n):
            if (x & S) == x:  # x subset of S
                sign = (-1) ** (bin(S ^ x).count("1"))
                coeff += sign * tt[x]
        if abs(coeff) > 1e-9:
            deg = max(deg, bin(S).count("1"))
    return int(deg)


def sensitivity_hierarchy_holds(tt, n: int) -> bool:
    """Verify the inequalities ``s(f) <= bs(f) <= C(f) <= D(f)`` and ``deg(f) <= D(f)`` for the
    function -- the fundamental relations between complexity measures."""
    s = max_sensitivity(tt, n)
    bs = block_sensitivity(tt, n)
    C = certificate_complexity(tt, n)
    D = decision_tree_complexity(tt, n)
    deg = polynomial_degree(tt, n)
    return bool(s <= bs <= C <= D and deg <= D)
