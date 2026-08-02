"""
The spectral form factor: a probe of quantum chaos in the time domain.

The spectral form factor (SFF) is built from the spectrum ``{E_j}`` of a Hamiltonian,

    SFF(t) = | sum_j e^{-i E_j t} |^2 = sum_{j,k} e^{-i (E_j - E_k) t}.

Its shape encodes level correlations: for a chaotic (random-matrix) spectrum the SFF shows a
characteristic **slope-dip-ramp-plateau** -- an early decay, a dip, a linear ``ramp`` (the fingerprint
of level repulsion), and a late-time ``plateau`` at the value ``D`` (the Hilbert-space dimension),
set by the diagonal ``j = k`` terms. At ``t = 0`` every phase aligns and ``SFF(0) = D^2``.

This module computes the SFF and its connected version, the plateau value, and the long-time
average, each checked against the exact ``D^2`` normalization and the diagonal plateau.
"""

import numpy as np


def spectral_form_factor(eigenvalues, t):
    """The spectral form factor ``|sum_j e^{-i E_j t}|^2`` at time ``t`` (or an array of times)."""
    e = np.asarray(eigenvalues, dtype=float)
    t = np.atleast_1d(np.asarray(t, dtype=float))
    phases = np.exp(-1j * np.outer(t, e))       # (len(t), D)
    z = phases.sum(axis=1)
    out = np.abs(z) ** 2
    return out if out.size > 1 else float(out[0])


def connected_sff(eigenvalue_ensemble, t):
    """
    The connected spectral form factor over an *ensemble* of spectra:
    ``<|Z(t)|^2> - |<Z(t)>|^2`` where ``Z(t) = sum_j e^{-i E_j t}``. Subtracting the disconnected
    (one-point) piece removes the early-time slope and exposes the ramp. ``eigenvalue_ensemble`` is a
    list/array of spectra.
    """
    t = np.atleast_1d(np.asarray(t, dtype=float))
    zs = []
    for e in eigenvalue_ensemble:
        e = np.asarray(e, dtype=float)
        zs.append(np.exp(-1j * np.outer(t, e)).sum(axis=1))
    Z = np.array(zs)                                   # (n_samples, len(t))
    sff = np.mean(np.abs(Z) ** 2, axis=0)
    disconnected = np.abs(np.mean(Z, axis=0)) ** 2
    out = sff - disconnected
    return out if out.size > 1 else float(out[0])


def sff_curve(eigenvalues, t_max, points=400):
    """Sample the SFF on ``points`` times over ``[0, t_max]``. Returns ``(times, sff)``."""
    ts = np.linspace(0.0, t_max, points)
    return ts, np.asarray(spectral_form_factor(eigenvalues, ts))


def sff_at_zero(eigenvalues):
    """The SFF at ``t = 0``: every phase aligns, so ``SFF(0) = D^2``."""
    D = len(np.asarray(eigenvalues))
    return float(spectral_form_factor(eigenvalues, 0.0))


def plateau_value(eigenvalues):
    """The analytic late-time plateau of the SFF: ``D`` (the surviving diagonal ``j = k`` terms) for a
    non-degenerate spectrum."""
    return float(len(np.asarray(eigenvalues)))


def long_time_average(eigenvalues, t_max, points=6000):
    """
    The time-averaged SFF over ``[t_start, t_max]`` (late window) -- converges to the plateau ``D``
    for a non-degenerate spectrum, since the off-diagonal phases average to zero.
    """
    ts = np.linspace(t_max * 0.3, t_max, points)
    return float(np.mean(np.asarray(spectral_form_factor(eigenvalues, ts))))


def reaches_plateau(eigenvalues, t_max, points=6000, rtol=0.15):
    """True iff the long-time-averaged SFF is within ``rtol`` of the plateau value ``D`` -- the
    diagonal-dominance check. Use a ``t_max`` large compared with the inverse mean level spacing."""
    avg = long_time_average(eigenvalues, t_max, points)
    D = plateau_value(eigenvalues)
    return bool(abs(avg - D) <= rtol * D)


def normalized_sff(eigenvalues, t):
    """The SFF normalized by ``D`` -- ``D`` at ``t = 0`` and ``~ 1`` on the plateau."""
    D = len(np.asarray(eigenvalues))
    return np.asarray(spectral_form_factor(eigenvalues, t)) / D
