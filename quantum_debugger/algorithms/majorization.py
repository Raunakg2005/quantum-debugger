"""
Majorization and LOCC convertibility (Nielsen's theorem).

Majorization is the order at the heart of quantum resource theories. A vector ``x``
*majorizes* ``y`` (``x > y``) if its largest ``k`` components sum to at least those of
``y`` for every ``k`` (with equal totals) -- intuitively ``x`` is "more peaked" / less
mixed. Two consequences are provided:

* **Nielsen's theorem** -- a bipartite pure state ``|psi>`` can be transformed into
  ``|phi>`` by local operations and classical communication (LOCC) *iff* the squared
  Schmidt vector of ``psi`` is majorized by that of ``phi``. Entanglement can only be
  degraded by LOCC, so a more entangled (flatter Schmidt) state converts to a less
  entangled one.
* **Schur concavity** -- majorization implies an entropy ordering (``x > y  ==>
  S(x) <= S(y)``), verified here.

Verified against Bell/product Schmidt vectors and random cases.
"""

import numpy as np


def majorizes(x, y, atol: float = 1e-9) -> bool:
    """
    True iff ``x`` majorizes ``y``: sorting both descending, every partial sum of ``x`` is
    ``>=`` that of ``y`` and the totals are equal. Both are treated as probability-like
    vectors (padded to equal length with zeros).
    """
    x = np.sort(np.asarray(x, dtype=float))[::-1]
    y = np.sort(np.asarray(y, dtype=float))[::-1]
    n = max(len(x), len(y))
    x = np.pad(x, (0, n - len(x)))
    y = np.pad(y, (0, n - len(y)))
    if abs(x.sum() - y.sum()) > atol:
        return False
    return bool(np.all(np.cumsum(x) >= np.cumsum(y) - atol))


def nielsen_convertible(psi, phi, dims, atol: float = 1e-9) -> bool:
    """
    Nielsen's theorem: ``|psi> -> |phi>`` is possible by LOCC iff the squared Schmidt
    coefficients of ``psi`` are *majorized by* those of ``phi`` -- i.e. ``phi`` is the more
    peaked (less entangled) Schmidt distribution. ``dims = (dA, dB)``.
    """
    from .entanglement_measures import schmidt_coefficients
    lam_psi = schmidt_coefficients(psi, dims) ** 2
    lam_phi = schmidt_coefficients(phi, dims) ** 2
    return majorizes(lam_phi, lam_psi, atol)


def majorization_entropy_bound(x, y) -> bool:
    """
    Schur concavity check: if ``x`` majorizes ``y`` then ``H(x) <= H(y)`` for the Shannon
    entropy. Returns True when this ordering holds for the given (sub-normalized)
    distributions -- the entropy consequence of majorization.
    """
    def H(p):
        p = np.asarray(p, dtype=float)
        p = p[p > 1e-12]
        return float(-np.sum(p * np.log2(p)))
    if majorizes(x, y):
        return H(x) <= H(y) + 1e-9
    if majorizes(y, x):
        return H(y) <= H(x) + 1e-9
    return True  # incomparable -> no ordering required
