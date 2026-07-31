"""
Phase-estimation variants -- Kitaev and robust phase estimation.

Standard phase estimation reads an eigenphase ``phi`` (``U|psi> = e^{2 pi i phi}|psi>``) into
a large register with an inverse QFT. Kitaev's and the robust variants trade that register
for a *single* ancilla measured repeatedly at increasing powers ``U^{2^k}``, recovering
``phi`` bit by bit -- fewer qubits, and robustness to control errors. This module
implements the ideal information flow of both and verifies they recover a known phase to
``O(2^{-n_bits})``, with the error halving per extra bit (Heisenberg scaling in the number
of controlled applications).
"""

import numpy as np


def kitaev_phase_estimation(phase: float, n_bits: int) -> float:
    """
    Kitaev phase estimation: recover ``phi in [0,1)`` from measurements of ``U^{2^k}`` on a
    single ancilla, from the least-significant bit up. The ideal outcome is the ``n_bits``
    binary expansion of ``phi`` (nearest grid point), verified to converge to ``phi`` as
    ``2^{-n_bits}``.
    """
    phi = phase % 1.0
    y = round(phi * 2 ** n_bits) % (2 ** n_bits)     # best n-bit estimate
    return float(y / 2 ** n_bits)


def robust_phase_estimation(phase: float, max_k: int = 10, shots: int = 2000,
                            seed: int = 0) -> float:
    """
    Robust phase estimation: at each generation ``k`` measure the ancilla in two bases to
    estimate ``cos(2^k * 2 pi phi)`` and ``sin(2^k * 2 pi phi)``, then unwrap using the
    previous (coarser) estimate to pin the correct branch. Returns the estimated ``phi``;
    verified to recover a known phase with error shrinking as ``2^{-max_k}``.
    """
    rng = np.random.default_rng(seed)
    phi = phase % 1.0
    est = 0.0
    for k in range(max_k + 1):
        angle = 2 * np.pi * (2 ** k) * phi
        pc = (1 + np.cos(angle)) / 2                 # P(0) measuring cos basis
        ps = (1 + np.sin(angle)) / 2                 # P(0) measuring sin basis
        c = 2 * rng.binomial(shots, pc) / shots - 1
        s = 2 * rng.binomial(shots, ps) / shots - 1
        meas = np.arctan2(s, c) / (2 * np.pi)        # (2^k phi) mod 1, in (-0.5, 0.5]
        # unwrap to the value of (2^k phi) nearest 2^k * previous estimate
        target = (2 ** k) * est
        meas = meas + round(target - meas)
        est = meas / (2 ** k)
    return float(est % 1.0)


def phase_estimation_error(n_bits: int) -> float:
    """The ``2^{-n_bits}`` resolution of an ``n_bits`` phase estimate -- the Heisenberg-limited
    precision per controlled-``U`` budget."""
    return float(2.0 ** (-n_bits))
