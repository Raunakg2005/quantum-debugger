"""
Random-matrix theory: the universal statistics of chaotic quantum spectra.

Quantum systems whose classical limit is chaotic have energy spectra that behave like the
eigenvalues of a *random matrix*. The relevant ensembles are the Gaussian Orthogonal Ensemble
(GOE, time-reversal-symmetric) and Gaussian Unitary Ensemble (GUE, broken time reversal). Their
nearest-neighbour level-spacing distributions follow the **Wigner surmise** -- level repulsion,
``P(s) -> 0`` as ``s -> 0`` -- in contrast to the ``P(s) = e^{-s}`` of an integrable (Poisson)
spectrum. The averaged spectral density is the Wigner semicircle.

This module builds GOE/GUE matrices, the Wigner-surmise and Poisson spacing densities, the
semicircle law, and unfolded level spacings, each checked against its analytic normalization and the
sampled statistics.
"""

import numpy as np


def goe_matrix(n, seed=0):
    """A Gaussian Orthogonal Ensemble matrix: a real symmetric ``n x n`` matrix ``(A + A^T)/2`` with
    ``A_ij ~ N(0, 1)`` -- time-reversal symmetric, ``beta = 1``."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    return (A + A.T) / np.sqrt(2.0)


def gue_matrix(n, seed=0):
    """A Gaussian Unitary Ensemble matrix: a complex Hermitian ``n x n`` matrix -- broken time
    reversal, ``beta = 2``."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    return (A + A.conj().T) / 2.0


def wigner_surmise(s, beta=1):
    """
    The Wigner surmise for the nearest-neighbour spacing density (mean spacing 1):
    GOE (``beta=1``): ``(pi/2) s exp(-pi s^2 / 4)``; GUE (``beta=2``): ``(32/pi^2) s^2 exp(-4 s^2/pi)``.
    Both vanish at ``s = 0`` (level repulsion).
    """
    s = np.asarray(s, dtype=float)
    if beta == 1:
        return (np.pi / 2.0) * s * np.exp(-np.pi * s ** 2 / 4.0)
    if beta == 2:
        return (32.0 / np.pi ** 2) * s ** 2 * np.exp(-4.0 * s ** 2 / np.pi)
    raise ValueError("beta must be 1 (GOE) or 2 (GUE)")


def poisson_spacing_pdf(s):
    """The Poisson (integrable) spacing density ``P(s) = e^{-s}`` -- no level repulsion."""
    return np.exp(-np.asarray(s, dtype=float))


def semicircle_density(x, radius=2.0):
    """The Wigner semicircle spectral density ``(2 / (pi R^2)) sqrt(R^2 - x^2)`` for ``|x| <= R`` --
    the averaged eigenvalue density of a large Gaussian ensemble."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    mask = np.abs(x) <= radius
    out[mask] = (2.0 / (np.pi * radius ** 2)) * np.sqrt(radius ** 2 - x[mask] ** 2)
    return out


def unfolded_spacings(eigenvalues):
    """Nearest-neighbour spacings of a spectrum, normalized to mean 1 (a simple global unfolding)."""
    e = np.sort(np.asarray(eigenvalues, dtype=float))
    gaps = np.diff(e)
    m = gaps.mean()
    return gaps / m if m > 0 else gaps


def level_spacing_ratios(eigenvalues):
    """The dimensionless gap ratios ``r_i = min(g_i, g_{i+1}) / max(g_i, g_{i+1})`` -- unfolding-free
    chaos diagnostics in ``[0, 1]``."""
    e = np.sort(np.asarray(eigenvalues, dtype=float))
    gaps = np.diff(e)
    ratios = []
    for i in range(len(gaps) - 1):
        a, b = gaps[i], gaps[i + 1]
        mx = max(a, b)
        ratios.append(min(a, b) / mx if mx > 0 else 0.0)
    return np.array(ratios)


def mean_ratio(eigenvalues):
    """The mean gap ratio ``<r>`` -- near ``0.386`` for Poisson, ``0.53`` for GOE, ``0.60`` for GUE."""
    r = level_spacing_ratios(eigenvalues)
    return float(r.mean()) if r.size else 0.0


def surmise_normalization(beta=1, s_max=8.0, points=4000):
    """The integral of the Wigner surmise (should be 1) -- a check that the density is normalized."""
    s = np.linspace(0, s_max, points)
    return float(np.trapezoid(wigner_surmise(s, beta), s))


def surmise_mean(beta=1, s_max=8.0, points=4000):
    """The mean spacing under the Wigner surmise (should be 1)."""
    s = np.linspace(0, s_max, points)
    p = wigner_surmise(s, beta)
    return float(np.trapezoid(s * p, s))
