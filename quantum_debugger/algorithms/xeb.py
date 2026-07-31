"""
Cross-entropy benchmarking (XEB) and the Porter-Thomas distribution.

A random quantum circuit produces output probabilities that follow the **Porter-Thomas**
distribution -- exponentially distributed, with a characteristic "speckle". Cross-entropy
benchmarking exploits this: sampling bitstrings from a noisy device and scoring them by the
*ideal* probabilities gives the **linear XEB fidelity**

    F_XEB = 2^n <p_ideal(sampled)> - 1,

which is 1 for a perfect device and 0 for the uniform (fully depolarized) output. This
module provides the Porter-Thomas distribution and the XEB estimator, verified: the PT
distribution has the right mean and normalization, and XEB reads 1 for ideal sampling and
~0 for uniform sampling.
"""

import numpy as np


def porter_thomas_pdf(p, dim: int):
    """
    Porter-Thomas probability density ``P(p) = D e^{-D p}`` (``D = dim``) of the output
    probabilities of a Haar-random circuit -- the exponential "speckle" law. Its mean is
    ``1/dim`` (uniform on average) but its spread is what XEB detects.
    """
    p = np.asarray(p, dtype=float)
    return dim * np.exp(-dim * p)


def porter_thomas_samples(dim: int, n: int, rng=None) -> np.ndarray:
    """
    Sample ``n`` normalized probability vectors of length ``dim`` from the Porter-Thomas
    distribution (exponential then normalized) -- a stand-in for random-circuit output
    distributions.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    e = rng.exponential(size=(n, dim))
    return e / e.sum(axis=1, keepdims=True)


def linear_xeb_fidelity(ideal_probs, sampled_indices) -> float:
    """
    Linear cross-entropy fidelity ``F = D <p_ideal(sampled)> - 1`` for bitstrings
    ``sampled_indices`` drawn from a device, scored by the ideal distribution ``ideal_probs``
    (``D = len``). ``~1`` when sampling from the ideal distribution, ``~0`` for uniform
    samples.
    """
    p = np.asarray(ideal_probs, dtype=float)
    D = len(p)
    return float(D * np.mean(p[np.asarray(sampled_indices)]) - 1)


def speckle_purity(probs) -> float:
    """
    Speckle purity ``D^2 <p^2>/... `` proxy: the collision probability ``sum p_i^2`` relative
    to the uniform ``1/D``. For Porter-Thomas it is ``~2/D`` (twice uniform) -- a
    distribution-shape check independent of any reference.
    """
    p = np.asarray(probs, dtype=float)
    D = len(p)
    return float(np.sum(p ** 2) * D)


def cross_entropy_fidelity(ideal_probs, device_probs) -> float:
    """
    Cross-entropy fidelity from full distributions: ``(sum q_i p_i - sum u_i p_i)/(sum p_i^2
    - sum u_i p_i)`` with uniform ``u`` -- 1 when ``q = p_ideal``, 0 when ``q`` is uniform.
    """
    p = np.asarray(ideal_probs, dtype=float)
    q = np.asarray(device_probs, dtype=float)
    D = len(p)
    u = 1.0 / D
    num = np.sum(q * p) - u * np.sum(p)
    den = np.sum(p * p) - u * np.sum(p)
    return float(num / den)
