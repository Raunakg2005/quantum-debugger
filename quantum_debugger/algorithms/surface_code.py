"""
The planar surface code -- the leading candidate for fault-tolerant hardware.

The surface code is the hypergraph product of two classical repetition codes. Taking
the distance-``d`` repetition code (check matrix ``(d-1) x d``) for both factors gives
the unrotated planar code

    [[ d^2 + (d-1)^2 , 1 , d ]],

a single logical qubit protected by weight-``<=4`` star/plaquette checks with
open boundaries. Because it is a hypergraph product it is automatically CSS and its
X/Z stabilizers commute by construction; here it is built through
:func:`hypergraph_product` and verified to have the advertised parameters and to
correct every error up to weight ``(d-1)//2``. The classical building blocks
(repetition and Hamming parity checks) are exposed too, since they seed the whole
CSS / hypergraph-product machinery.
"""

import numpy as np

from .css_code import CSSCode, hypergraph_product


def repetition_check_matrix(d: int) -> np.ndarray:
    """
    Parity-check matrix of the length-``d`` classical repetition code ``[d, 1, d]``: the
    ``(d-1) x d`` matrix with ``1`` s on the diagonal and first super-diagonal (each row
    checks a neighbouring pair). The classical seed of the surface/toric codes.
    """
    H = np.zeros((d - 1, d), dtype=np.int8)
    for i in range(d - 1):
        H[i, i] = 1
        H[i, i + 1] = 1
    return H


def hamming_check_matrix(r: int) -> np.ndarray:
    """
    Parity-check matrix of the ``[2^r - 1, 2^r - 1 - r, 3]`` Hamming code: columns are all
    nonzero ``r``-bit strings. ``r = 3`` gives the ``[7, 4, 3]`` Hamming code that seeds
    the Steane / color code.
    """
    n = 2 ** r - 1
    cols = []
    for c in range(1, n + 1):
        cols.append([(c >> b) & 1 for b in range(r)])
    return np.array(cols, dtype=np.int8).T


def planar_surface_code(d: int) -> CSSCode:
    """
    Distance-``d`` unrotated planar surface code ``[[d^2 + (d-1)^2, 1, d]]`` as the
    hypergraph product of two length-``d`` repetition codes. CSS and commuting by
    construction; verified to encode one logical qubit at distance ``d``.
    """
    H = repetition_check_matrix(d)
    return hypergraph_product(H, H)


def surface_code_parameters(d: int) -> dict:
    """
    The ``[[n, k, d]]`` parameters of the distance-``d`` planar surface code:
    ``n = d^2 + (d-1)^2``, ``k = 1``, distance ``d``.
    """
    return {"n": d**2 + (d - 1) ** 2, "k": 1, "d": d}


def corrects_all_errors_up_to(code: CSSCode, weight: int) -> bool:
    """
    Exhaustively verify that ``code``'s minimum-weight decoder corrects *every* X error of
    weight ``<= weight``: for each such error the decoded correction returns the state to
    the code space with no residual logical (residual is a stabilizer). The operational
    definition of "distance ``d`` corrects ``(d-1)//2`` errors".
    """
    import itertools
    n = code.n
    xl, _ = code.logical_operators()
    from .css_code import gf2_rref, _in_rowspace
    stab_rref, stab_piv = gf2_rref(code.Hx)
    for w in range(weight + 1):
        for support in itertools.combinations(range(n), w):
            e = np.zeros(n, dtype=np.int8)
            e[list(support)] = 1
            corr = code.decode_min_weight(e, max_weight=weight)
            residual = (e ^ corr) % 2
            # residual must commute with all Z-logicals (be a stabilizer, not a logical)
            if np.any(code.x_syndrome(residual)):
                return False
            if not _in_rowspace(residual, stab_rref, stab_piv):
                return False
    return True
