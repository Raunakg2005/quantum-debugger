"""
Non-Markovianity: measuring memory effects in open-system dynamics.

A dynamical map is *Markovian* (memoryless) when it is CP-divisible; a signature is that the
trace distance between any two states -- their distinguishability -- decreases monotonically, as
information flows one way into the environment. When the environment feeds information *back*,
the trace distance temporarily grows, and the dynamics is non-Markovian.

The Breuer-Laine-Piilo (BLP) measure quantifies this backflow:

    N = sup over state pairs  integral_{ (dD/dt) > 0 }  (dD/dt) dt,

the total increase of the trace distance ``D(rho_1(t), rho_2(t))`` over time. For a qubit
undergoing dephasing with coherence function ``c(t)``, the optimal pair is ``|+>, |->`` and the
trace distance is exactly ``|c(t)|`` -- so ``N`` is the summed revival of ``|c(t)|``. Pure
exponential decay (Markovian) gives ``N = 0``; an oscillating/reviving coherence gives ``N > 0``.

Verified: the ``|+>/|->`` trace distance equals ``|c(t)|`` exactly; monotone decay scores ``0``;
a reviving coherence scores a positive backflow.
"""

import numpy as np


def trace_distance(rho, sigma):
    """Trace distance ``(1/2) ||rho - sigma||_1`` between two density matrices -- their optimal
    single-shot distinguishability."""
    diff = np.asarray(rho, dtype=complex) - np.asarray(sigma, dtype=complex)
    diff = 0.5 * (diff + diff.conj().T)
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(diff))))


def dephasing_map(coherence):
    """A qubit dephasing map with coherence factor ``c`` in ``[-1, 1]``: it multiplies the
    off-diagonal elements by ``c`` and leaves populations fixed. Returns the map as a function
    of a density matrix."""
    c = complex(coherence)

    def apply(rho):
        rho = np.asarray(rho, dtype=complex).copy()
        rho[0, 1] *= c
        rho[1, 0] *= np.conj(c)
        return rho

    return apply


def coherence_trace_distance(coherence_values):
    """
    Trace distance between the dephased ``|+>`` and ``|->`` states at each time, which equals
    ``|c(t)|`` exactly. ``coherence_values`` is the array ``c(t)`` sampled on a time grid.
    """
    plus = 0.5 * np.array([[1, 1], [1, 1]], dtype=complex)
    minus = 0.5 * np.array([[1, -1], [-1, 1]], dtype=complex)
    out = []
    for c in coherence_values:
        m = dephasing_map(c)
        out.append(trace_distance(m(plus), m(minus)))
    return np.array(out)


def markovian_coherence(times, rate=1.0):
    """Coherence of purely Markovian dephasing, ``c(t) = e^{-rate t}`` -- monotone, no revivals."""
    return np.exp(-rate * np.asarray(times, dtype=float))


def nonmarkovian_coherence(times, rate=0.5, omega=3.0):
    """
    Coherence of a qubit dephasing with a memory kernel (coupling to a structured mode),
    ``c(t) = e^{-rate t} cos(omega t)`` -- the oscillation produces distinguishability revivals,
    hence non-Markovianity.
    """
    t = np.asarray(times, dtype=float)
    return np.exp(-rate * t) * np.cos(omega * t)


def distinguishability_backflow(distances):
    """
    The positive increments of a trace-distance time series -- the moments where distinguishability
    *grows* (information flows back from the environment). Returns the array of positive
    differences.
    """
    d = np.asarray(distances, dtype=float)
    dd = np.diff(d)
    return dd[dd > 0.0]


def blp_measure(distances):
    """
    The Breuer-Laine-Piilo non-Markovianity of a trace-distance time series ``D(t)``: the total
    increase ``sum_{increments > 0} Delta D``. Zero for monotone (Markovian) decay, positive when
    the distinguishability revives.
    """
    return float(distinguishability_backflow(distances).sum())


def is_markovian(distances, atol=1e-6):
    """True iff the dynamics shows no distinguishability backflow (BLP measure ``~ 0``) -- i.e. the
    trace distance is monotonically non-increasing."""
    return blp_measure(distances) <= atol


def revival_count(distances, atol=1e-9):
    """Number of separate revival episodes (maximal runs of increasing trace distance) -- how many
    times information flows back from the environment."""
    d = np.asarray(distances, dtype=float)
    rising = np.diff(d) > atol
    count, prev = 0, False
    for r in rising:
        if r and not prev:
            count += 1
        prev = r
    return count
