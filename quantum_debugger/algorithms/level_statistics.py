"""
Level-spacing statistics (quantum chaos diagnostic)

Whether a quantum system is integrable or chaotic is written in the *correlations*
between its energy levels. The symmetry-independent diagnostic (Oganesyan & Huse,
Phys. Rev. B 75, 155111, 2007) is the mean adjacent-gap ratio

    <r> = < min(s_n, s_{n+1}) / max(s_n, s_{n+1}) >,      s_n = E_{n+1} - E_n,

which needs no unfolding. It takes two universal values:

  * **Poisson** (integrable, uncorrelated levels): ``<r> ~ 0.3863``;
  * **GOE / Wigner-Dyson** (chaotic, level repulsion): ``<r> ~ 0.5307``.

This module computes ``<r>`` and validates it against both reference ensembles.

Caveat: a physical Hamiltonian only shows the clean values *within a single symmetry
sector* -- mixing sectors (or leaving degeneracies unresolved) contaminates the
statistics toward Poisson even for a chaotic system. So feed this the spectrum of one
symmetry block, or a random-matrix ensemble as a reference.
"""

import numpy as np


def level_spacing_ratio(eigenvalues) -> float:
    """
    Mean adjacent-gap ratio ``<r>`` of a spectrum (Oganesyan-Huse). Near ``0.386`` for
    Poisson (integrable) statistics and ``0.531`` for GOE (chaotic) statistics. The
    eigenvalues are sorted internally and zero gaps (exact degeneracies) dropped.
    """
    evals = np.sort(np.asarray(eigenvalues, dtype=float))
    gaps = np.diff(evals)
    gaps = gaps[gaps > 1e-12]
    if len(gaps) < 2:
        return float("nan")
    lo = np.minimum(gaps[:-1], gaps[1:])
    hi = np.maximum(gaps[:-1], gaps[1:])
    return float(np.mean(lo / hi))


def goe_reference(size: int = 200, samples: int = 20, seed: int = 0) -> float:
    """
    Mean ``<r>`` over ``samples`` Gaussian Orthogonal Ensemble matrices of dimension
    ``size`` -- the chaotic reference (converges to ``~0.5307``). GOE matrices are
    real symmetric with i.i.d. Gaussian entries.
    """
    rng = np.random.default_rng(seed)
    ratios = []
    for _ in range(samples):
        A = rng.normal(size=(size, size))
        ratios.append(level_spacing_ratio(np.linalg.eigvalsh((A + A.T) / 2)))
    return float(np.mean(ratios))


def poisson_reference(size: int = 5000, samples: int = 20, seed: int = 0) -> float:
    """
    Mean ``<r>`` over ``samples`` Poisson spectra (uncorrelated levels, i.e. sorted
    uniform random numbers) of ``size`` levels -- the integrable reference (converges
    to ``~0.3863``).
    """
    rng = np.random.default_rng(seed)
    ratios = [level_spacing_ratio(np.sort(rng.uniform(size=size))) for _ in range(samples)]
    return float(np.mean(ratios))


def classify_spectrum(eigenvalues) -> dict:
    """
    Compute ``<r>`` for a spectrum and classify it against the two universal values.

    Returns dict with ``r_statistic``, ``classification`` (``"chaotic"``,
    ``"integrable"``, or ``"intermediate"``), and the reference values
    ``poisson`` (0.386) and ``goe`` (0.531).
    """
    r = level_spacing_ratio(eigenvalues)
    poisson, goe = 0.3863, 0.5307
    midpoint = (poisson + goe) / 2
    if abs(r - poisson) < 0.03:
        label = "integrable"
    elif abs(r - goe) < 0.03:
        label = "chaotic"
    else:
        label = "chaotic" if r > midpoint else "integrable"
        label = "intermediate" if abs(r - midpoint) < 0.02 else label
    return {"r_statistic": r, "classification": label, "poisson": poisson, "goe": goe}
