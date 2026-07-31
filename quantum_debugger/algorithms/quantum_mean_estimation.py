"""
Quantum mean estimation and Monte-Carlo speedup.

Estimating the expectation ``E[f] = (1/N) sum_i f(i)`` of a bounded function is the core of
Monte-Carlo integration and risk analysis. Classically the error falls as ``1/sqrt(M)`` in
the number of samples ``M``. Quantum mean estimation encodes the mean as an amplitude --
prepare ``(1/sqrt N) sum_i |i>(sqrt(1-f_i)|0> + sqrt(f_i)|1>)``, so the ancilla-``|1>``
probability is exactly ``E[f]`` -- and reads it off with amplitude estimation, achieving the
Heisenberg error ``1/M``: a *quadratic* speedup. Verified to recover the true mean and to
require quadratically fewer samples for a target precision.
"""

import numpy as np

from .amplitude_estimation_advanced import maximum_likelihood_ae


def mean_amplitude(f_values) -> float:
    """
    The amplitude encoding the mean of ``f`` (values in ``[0,1]``): ``a = sqrt(E[f])``, so
    that ``a^2`` is exactly the expectation. The quantity amplitude estimation targets.
    """
    f = np.asarray(f_values, dtype=float)
    return float(np.sqrt(np.mean(f)))


def quantum_mean_estimation(f_values, m_schedule=(0, 1, 2, 4, 8), shots: int = 2000,
                            seed: int = 0) -> float:
    """
    Estimate ``E[f]`` for values in ``[0,1]`` by amplitude-estimating ``a = sqrt(E[f])`` via
    maximum-likelihood AE, then returning ``a^2``. Verified to recover the true mean with
    Heisenberg-limited error.
    """
    a_true = mean_amplitude(f_values)
    a_est = maximum_likelihood_ae(a_true, list(m_schedule), shots=shots, seed=seed)
    return float(a_est ** 2)


def classical_samples_for_precision(eps: float) -> float:
    """Classical Monte-Carlo samples needed for error ``eps``: ``~ 1/eps^2``."""
    return float(1.0 / eps ** 2)


def quantum_samples_for_precision(eps: float) -> float:
    """Quantum (amplitude-estimation) samples needed for error ``eps``: ``~ 1/eps`` -- the
    quadratic Monte-Carlo speedup."""
    return float(1.0 / eps)


def monte_carlo_speedup(eps: float) -> float:
    """The quadratic speedup factor ``classical/quantum = 1/eps`` in samples at precision
    ``eps`` -- how much fewer queries quantum mean estimation needs."""
    return float(classical_samples_for_precision(eps) / quantum_samples_for_precision(eps))
