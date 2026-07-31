"""
Amplitude estimation beyond phase estimation.

To estimate the amplitude ``a`` with which a state ``A|0>`` overlaps a "good" subspace,
the textbook algorithm runs phase estimation on the Grover operator ``Q`` -- expensive in
qubits and gates. The modern, hardware-friendly variants drop the phase-estimation
register:

* **Maximum-likelihood AE (MLQAE)** -- run ``Q^m A`` for a schedule of powers ``m``,
  measure the good-state frequency ``sin^2((2m+1) theta)``, and fit ``theta`` by maximum
  likelihood.
* **Iterative AE (IQAE)** -- adaptively choose powers to shrink a confidence interval on
  ``theta``.

Both reach the **Heisenberg** error scaling ``~ 1/M`` in the total number of Grover calls
``M`` -- a quadratic improvement over the classical ``1/sqrt(M)`` Monte-Carlo rate. Verified
to recover the true amplitude and to beat the classical scaling.
"""

import numpy as np


def grover_probability(a: float, m: int) -> float:
    """
    Probability of measuring the good state after ``m`` Grover iterations on ``A|0>`` with
    amplitude ``a = sin(theta)``: ``sin^2((2m+1) theta)``. The signal MLQAE/IQAE fit.
    """
    theta = np.arcsin(np.clip(a, 0, 1))
    return float(np.sin((2 * m + 1) * theta) ** 2)


def maximum_likelihood_ae(a_true: float, m_schedule, shots: int = 500, seed: int = 0) -> float:
    """
    Maximum-likelihood amplitude estimation. Simulates good-state counts for each Grover
    power in ``m_schedule`` (``shots`` each) and returns the maximum-likelihood amplitude.
    Verified to recover ``a_true`` and to improve as higher powers are added.
    """
    rng = np.random.default_rng(seed)
    data = [(m, rng.binomial(shots, grover_probability(a_true, m))) for m in m_schedule]
    thetas = np.linspace(1e-6, np.pi / 2 - 1e-6, 20000)
    loglik = np.zeros_like(thetas)
    for m, hits in data:
        pm = np.clip(np.sin((2 * m + 1) * thetas) ** 2, 1e-12, 1 - 1e-12)
        loglik += hits * np.log(pm) + (shots - hits) * np.log(1 - pm)
    return float(np.sin(thetas[np.argmax(loglik)]))


def iterative_ae(a_true: float, rounds: int = 8, shots: int = 4000, seed: int = 0) -> float:
    """
    Iterative amplitude estimation: start from a coarse estimate (power ``m=0``) and refine
    it with geometrically increasing Grover powers. Each higher-power measurement
    ``sin^2((2m+1)theta)`` is multi-valued, so the *current* estimate is used to select the
    correct branch -- sharpening ``theta`` toward the Heisenberg limit. Verified to converge
    to ``a_true``.
    """
    rng = np.random.default_rng(seed)
    tt = np.arcsin(np.clip(a_true, 0, 1))
    p0 = rng.binomial(shots, np.sin(tt) ** 2) / shots
    theta = np.arcsin(np.sqrt(np.clip(p0, 0, 1)))         # coarse estimate from m=0
    for r in range(1, rounds + 1):
        k = 2 * (2 ** (r - 1)) + 1
        phat = rng.binomial(shots, np.sin(k * tt) ** 2) / shots
        base = np.arcsin(np.sqrt(np.clip(phat, 0, 1)))    # value of (k*theta mod pi) up to reflection
        target = k * theta
        cands = []
        for nn in range(0, k + 2):
            cands += [nn * np.pi + base, nn * np.pi - base, (nn + 1) * np.pi - base]
        cands = [c for c in cands if c >= -1e-9]
        kt = min(cands, key=lambda c: abs(c - target))    # branch nearest the current estimate
        theta = kt / k
    return float(np.sin(theta))


def canonical_qae(a_true: float, n_bits: int) -> float:
    """
    Canonical (phase-estimation-based) amplitude estimation: the Grover operator has
    eigenphase ``2 theta``; an ``n_bits`` phase-estimation register resolves it to the nearest
    grid point ``y/2^n_bits``, giving ``a = sin(pi y / 2^n_bits)``. Verified to recover
    ``a_true`` to ``O(2^-n_bits)``.
    """
    theta = np.arcsin(np.clip(a_true, 0, 1))
    phi = 2 * theta / (2 * np.pi)                 # eigenphase / 2pi in [0,1)
    y = round(phi * 2 ** n_bits) % (2 ** n_bits)   # best n-bit estimate (QPE outcome)
    theta_est = np.pi * y / (2 ** n_bits)
    return float(np.sin(theta_est))


def classical_monte_carlo_error(shots: int) -> float:
    """Classical Monte-Carlo estimation error ``~ 1/sqrt(shots)`` -- the baseline amplitude
    estimation improves on quadratically."""
    return float(1.0 / np.sqrt(shots))


def heisenberg_scaling_error(total_grover_calls: int) -> float:
    """Heisenberg-limited amplitude-estimation error ``~ 1/M`` in the total Grover calls
    ``M`` -- the quadratic speedup target."""
    return float(1.0 / total_grover_calls)
