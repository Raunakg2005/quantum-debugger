"""
Exact syndrome decoding -- the maximum-likelihood reference for iterative decoders.

For a linear code, every received word ``y`` lies in a *coset* of the code determined by its
syndrome ``s = H y``. Maximum-likelihood decoding over a binary symmetric channel picks the
minimum-weight error consistent with the syndrome -- the *coset leader*. Building the full syndrome
-> coset-leader table by exhaustive search gives an exact decoder for small codes, against which the
efficient belief-propagation and bit-flipping decoders are checked.

Verified: the Hamming ``[7,4,3]`` code has 8 distinct syndromes each with a weight-<=1 coset leader,
and corrects every single-bit error.
"""

import itertools

import numpy as np

from .ldpc_codes import syndrome


def _syndrome_int(H, error):
    s = syndrome(H, error)
    return int("".join(map(str, s)), 2) if s.size else 0


def syndrome_table(H):
    """
    The exact syndrome -> minimum-weight coset-leader table. Iterating errors by increasing weight,
    the first error hitting each syndrome is its coset leader. Returns ``{syndrome_int: leader}``.
    """
    H = np.asarray(H, dtype=int)
    n = H.shape[1]
    table = {}
    for weight in range(n + 1):
        for support in itertools.combinations(range(n), weight):
            e = np.zeros(n, dtype=int)
            e[list(support)] = 1
            s = _syndrome_int(H, e)
            if s not in table:
                table[s] = e
        if len(table) == 2 ** (H.shape[0]):
            break
    return table


def coset_leader(H, error, table=None):
    """The minimum-weight error with the same syndrome as ``error`` -- the coset leader (the ML
    correction)."""
    H = np.asarray(H, dtype=int)
    if table is None:
        table = syndrome_table(H)
    return table[_syndrome_int(H, error)]


def ml_decode(H, received, table=None):
    """
    Maximum-likelihood decode of a received word: subtract the coset leader of its syndrome, giving
    the nearest codeword.
    """
    H = np.asarray(H, dtype=int)
    y = np.asarray(received, dtype=int)
    leader = coset_leader(H, y, table)
    return (y + leader) % 2


def corrects_all_errors_up_to(H, weight):
    """
    True iff exact syndrome decoding corrects *every* error of Hamming weight ``<= weight`` -- i.e.
    each such error is the unique minimum-weight member of its coset. Holds up to ``t = floor((d-1)/2)``.
    """
    H = np.asarray(H, dtype=int)
    n = H.shape[1]
    table = syndrome_table(H)
    for w in range(1, weight + 1):
        for support in itertools.combinations(range(n), w):
            e = np.zeros(n, dtype=int)
            e[list(support)] = 1
            if not np.array_equal(coset_leader(H, e, table), e):
                return False
    return True


def error_correcting_capability(H):
    """The guaranteed error-correcting capability ``t = floor((d - 1) / 2)`` from the minimum
    distance ``d``."""
    from .ldpc_codes import minimum_distance
    d = minimum_distance(H)
    return (d - 1) // 2
