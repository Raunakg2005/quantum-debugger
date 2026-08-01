"""
Fourier analysis on the Boolean cube.

Every Boolean function ``f : {0,1}^n -> {-1,1}`` expands in the orthonormal character basis
``chi_S(x) = (-1)^{sum_{i in S} x_i}``,

    f(x) = sum_S fhat(S) chi_S(x),   fhat(S) = 2^{-n} sum_x f(x) chi_S(x).

The Fourier weights ``fhat(S)^2`` form a probability distribution (**Parseval**:
``sum_S fhat(S)^2 = 1``), from which follow the **influence** of a variable, the **total
influence** (average sensitivity), and the **noise stability** -- the tools behind hardness of
approximation, learning, and quantum query lower bounds. This module computes the spectrum and
these quantities, verified against Parseval and the known values for parity/dictator functions.
"""

import numpy as np
from itertools import combinations


def to_pm1(tt) -> np.ndarray:
    """Convert a ``0/1`` truth table to the ``{-1, +1}`` convention (``0 -> +1``, ``1 -> -1``)."""
    return 1 - 2 * np.asarray(tt, dtype=int)


def _chi(S, x, n):
    return (-1) ** sum((x >> i) & 1 for i in S)


def fourier_coefficients(tt, n: int) -> dict:
    """
    All Fourier coefficients ``fhat(S) = 2^{-n} sum_x f(x) chi_S(x)`` of a ``{-1,+1}`` function
    (pass a ``0/1`` truth table; it is converted). Returned as ``{frozenset(S): coeff}``.
    """
    f = to_pm1(tt)
    out = {}
    for size in range(n + 1):
        for S in combinations(range(n), size):
            out[frozenset(S)] = float(sum(f[x] * _chi(S, x, n) for x in range(2 ** n)) / 2 ** n)
    return out


def parseval(tt, n: int) -> float:
    """The total Fourier weight ``sum_S fhat(S)^2`` -- equal to 1 for any ``{-1,+1}`` function
    (Parseval's identity). The verification anchor."""
    return float(sum(c ** 2 for c in fourier_coefficients(tt, n).values()))


def influence(tt, n: int, i: int) -> float:
    """Influence of variable ``i``: ``sum_{S : i in S} fhat(S)^2`` -- the probability that flipping
    bit ``i`` changes ``f``."""
    return float(sum(c ** 2 for S, c in fourier_coefficients(tt, n).items() if i in S))


def total_influence(tt, n: int) -> float:
    """Total influence (average sensitivity) ``sum_S |S| fhat(S)^2 = sum_i Inf_i`` -- the mean
    number of pivotal coordinates. ``n`` for parity, 1 for a dictator."""
    return float(sum(len(S) * c ** 2 for S, c in fourier_coefficients(tt, n).items()))


def noise_stability(tt, n: int, rho: float) -> float:
    """
    Noise stability ``Stab_rho(f) = sum_S rho^{|S|} fhat(S)^2`` -- the correlation between ``f(x)``
    and ``f(y)`` when ``y`` is a ``rho``-correlated copy of ``x``. 1 at ``rho=1``, ``fhat(emptyset)^2``
    at ``rho=0``.
    """
    return float(sum(rho ** len(S) * c ** 2 for S, c in fourier_coefficients(tt, n).items()))


def fourier_weight_above_degree(tt, n: int, k: int) -> float:
    """The Fourier weight on sets of size ``> k`` -- the high-degree part of ``f`` (small for
    low-degree / smooth functions)."""
    return float(sum(c ** 2 for S, c in fourier_coefficients(tt, n).items() if len(S) > k))


def degree_from_fourier(tt, n: int, atol: float = 1e-9) -> int:
    """The real (Fourier) degree of ``f``: the size of the largest set with a non-zero
    coefficient -- equal to the multilinear polynomial degree."""
    return int(max((len(S) for S, c in fourier_coefficients(tt, n).items() if abs(c) > atol),
                   default=0))
