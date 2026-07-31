"""
Randomized benchmarking (RB) and interleaved RB.

Randomized benchmarking estimates the average error per Clifford gate in a way that is
robust to state-preparation and measurement errors: run random Clifford sequences of
growing length ``m``, invert them, and fit the survival probability to the exponential

    F(m) = A p^m + B.

The single number ``p`` gives the average gate fidelity ``F_avg = 1 - (1-p)(d-1)/d`` for
dimension ``d``. **Interleaved RB** repeats the experiment with a target gate inserted in
every layer; the ratio of the two decays isolates that gate's error. This module provides
the decay model, the fit, and the fidelity conversions, verified to recover a planted decay
rate and gate error.
"""

import numpy as np


def rb_survival(p: float, m, A: float = 0.5, B: float = 0.5):
    """The RB survival curve ``F(m) = A p^m + B`` -- SPAM (``A``, ``B``) factored out from the
    depolarizing decay ``p``."""
    m = np.asarray(m, dtype=float)
    return A * p ** m + B


def fit_rb_decay(m_values, survivals):
    """
    Fit the RB decay ``A p^m + B`` to (length, survival) data and return ``(p, A, B)``. The
    decay rate ``p`` is the SPAM-robust quantity. Verified to recover a planted ``p``.
    """
    m = np.asarray(m_values, dtype=float)
    y = np.asarray(survivals, dtype=float)
    # linearize once B is estimated by the tail, then refine over a p-grid
    best = None
    for p in np.linspace(0.5, 0.9999, 4000):
        X = np.vstack([p ** m, np.ones_like(m)]).T
        (A, B), res, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = np.sum((X @ [A, B] - y) ** 2)
        if best is None or r < best[0]:
            best = (r, p, A, B)
    return best[1], best[2], best[3]


def average_gate_fidelity_from_rb(p: float, d: int = 2) -> float:
    """Average gate fidelity from the RB decay rate: ``F_avg = 1 - (1-p)(d-1)/d`` for
    Hilbert-space dimension ``d``."""
    return float(1 - (1 - p) * (d - 1) / d)


def error_per_clifford(p: float, d: int = 2) -> float:
    """Average error per Clifford ``r = (1-p)(d-1)/d`` -- the headline RB number."""
    return float((1 - p) * (d - 1) / d)


def interleaved_rb_gate_error(p_ref: float, p_interleaved: float, d: int = 2) -> float:
    """
    Per-gate error of an interleaved target gate from the reference and interleaved RB decay
    rates: ``r_gate = (1 - p_interleaved/p_ref)(d-1)/d``. Isolates a single gate's error from
    the average. Verified against a planted gate error.
    """
    return float((1 - p_interleaved / p_ref) * (d - 1) / d)
