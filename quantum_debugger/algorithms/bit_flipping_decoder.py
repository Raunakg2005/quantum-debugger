"""
Gallager bit-flipping decoding of LDPC codes.

Bit-flipping is the simplest hard-decision LDPC decoder. It repeatedly computes the syndrome and,
for each bit, counts how many of its parity checks are *unsatisfied*; the bit(s) sitting on the most
unsatisfied checks are flipped. On a sparse code with enough column weight a single error makes its
own checks fail and no others', so the errored bit has a strict majority of unsatisfied checks and is
corrected in one step. This module implements the decoder and its diagnostics, verified to correct
low-weight errors on LDPC codes with column weight ``>= 3``.
"""

import numpy as np

from .ldpc_codes import syndrome, tanner_graph, column_weights


def unsatisfied_checks(H, word):
    """The indices of the parity checks that ``word`` fails (odd parity) -- the non-zero syndrome
    positions."""
    s = syndrome(H, word)
    return np.nonzero(s)[0]


def unsatisfied_count_per_bit(H, word):
    """For each bit, the number of *unsatisfied* checks it participates in -- the bit-flip decision
    statistic."""
    H = np.asarray(H, dtype=int)
    m, n = H.shape
    s = syndrome(H, word)
    counts = np.zeros(n, dtype=int)
    tg = tanner_graph(H)
    for j in range(n):
        counts[j] = sum(int(s[i]) for i in tg["bits"][j])
    return counts


def gallager_bit_flip(H, received, max_iter=50):
    """
    Gallager's hard-decision bit-flipping decoder. Each round flips the bit with the most unsatisfied
    checks (ties: the lowest index), stopping when the syndrome is zero. Returns
    ``(decoded_word, converged)``.
    """
    H = np.asarray(H, dtype=int)
    word = np.asarray(received, dtype=int).copy()
    for _ in range(max_iter):
        s = syndrome(H, word)
        if np.all(s == 0):
            return word, True
        counts = unsatisfied_count_per_bit(H, word)
        j = int(np.argmax(counts))
        if counts[j] == 0:
            break
        word[j] ^= 1
    return word, bool(np.all(syndrome(H, word) == 0))


def bit_flip_corrects(H, error, max_iter=50):
    """True iff bit-flipping recovers the all-zero codeword from ``error``."""
    decoded, _ = gallager_bit_flip(H, error, max_iter=max_iter)
    return bool(np.all(decoded == 0))


def bit_flip_corrects_all_weight1(H, max_iter=50):
    """
    Verify bit-flipping corrects every single-bit error. Holds for LDPC codes whose column weight is
    large enough that an errored bit strictly dominates the unsatisfied-check count.
    """
    H = np.asarray(H, dtype=int)
    n = H.shape[1]
    for j in range(n):
        e = np.zeros(n, dtype=int)
        e[j] = 1
        if not bit_flip_corrects(H, e, max_iter=max_iter):
            return False
    return True


def min_column_weight(H):
    """The smallest column weight of ``H`` -- bit-flipping reliably corrects a single error when this
    is ``>= 3``."""
    return int(column_weights(H).min())
