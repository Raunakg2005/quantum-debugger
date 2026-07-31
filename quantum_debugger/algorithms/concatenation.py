"""
Code concatenation and the threshold theorem.

Encoding each qubit of a code inside another copy of the code -- *concatenation* --
suppresses errors extraordinarily fast. If a single level maps physical error ``p`` to
logical error ``A p^2`` (for a distance-3 code that corrects one error), then ``L`` levels
give

    p_L = p_th (p / p_th)^{2^L},        p_th = 1 / A,

a *double-exponential* fall-off in ``L`` whenever ``p < p_th`` -- the quantitative content
of the threshold theorem. Above threshold the same recursion makes things worse. This
module provides the recursion, the pseudothreshold, the levels needed for a target error,
and the qubit overhead, verified against the closed form.
"""

import numpy as np


def one_level_logical_error(p: float, A: float = 1.0) -> float:
    """
    Logical error after one level of a distance-3 concatenated code: ``A p^2`` (two faults
    needed to fail). ``A`` is the number of malignant fault pairs.
    """
    return A * p ** 2


def concatenated_logical_error(p: float, levels: int, A: float = 1.0) -> float:
    """
    Logical error after ``levels`` of concatenation, applying ``p -> A p^2`` recursively.
    Equals the closed form ``p_th (p/p_th)^{2^levels}`` with ``p_th = 1/A`` -- double-
    exponential suppression below threshold.
    """
    for _ in range(levels):
        p = one_level_logical_error(p, A)
    return float(p)


def pseudothreshold(A: float = 1.0) -> float:
    """The concatenation threshold ``p_th = 1/A``: below it errors shrink with each level,
    above it they grow. (For ``A p^2 = p``.)"""
    return float(1.0 / A)


def levels_for_target(p: float, target: float, A: float = 1.0) -> int:
    """
    Number of concatenation levels needed to bring physical error ``p`` below ``target``.
    Returns ``-1`` when ``p`` is at or above the pseudothreshold (no amount of concatenation
    helps).
    """
    if p >= pseudothreshold(A):
        return -1
    levels = 0
    cur = p
    while cur > target and levels < 100:
        cur = one_level_logical_error(cur, A)
        levels += 1
    return levels


def qubit_overhead(levels: int, block_qubits: int = 7) -> int:
    """
    Physical qubits per logical qubit after ``levels`` of concatenation with a
    ``block_qubits``-qubit code (e.g. 7 for Steane): ``block_qubits^levels``.
    """
    return int(block_qubits ** levels)


def double_exponential_check(p: float, levels: int, A: float = 1.0, atol: float = 1e-9) -> bool:
    """
    Verify the recursion matches the closed form ``p_th (p/p_th)^{2^levels}`` for
    ``p < p_th`` -- the double-exponential suppression law.
    """
    pth = pseudothreshold(A)
    closed = pth * (p / pth) ** (2 ** levels)
    return bool(abs(concatenated_logical_error(p, levels, A) - closed) < atol * max(1, closed))
