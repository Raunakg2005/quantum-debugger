"""
Belief-propagation (sum-product) decoding of LDPC codes.

Belief propagation decodes by passing probabilistic messages along the Tanner graph. Working in
log-likelihood ratios (LLRs), each variable node sends its current belief to its checks, each check
node combines the incoming beliefs via the ``tanh`` parity rule, and the process iterates until the
hard-decision word satisfies all parity checks (a valid codeword) or a maximum number of rounds is
reached. On a loop-free (or large-girth) Tanner graph this converges to the exact bitwise
posterior; on real sparse codes it is near-optimal and linear-time.

This module implements the sum-product and min-sum decoders over a binary symmetric channel and is
verified to match the exact maximum-likelihood decoder on the correctable errors of small codes.
"""

import numpy as np

from .ldpc_codes import syndrome, tanner_graph


def bsc_llr(received, p):
    """Channel log-likelihood ratios for a binary symmetric channel of crossover ``p``:
    ``L_j = (1 - 2 y_j) log((1-p)/p)``."""
    y = np.asarray(received, dtype=int)
    return (1 - 2 * y) * np.log((1 - p) / p)


def sum_product_decode(H, received, p=0.05, max_iter=50):
    """
    Sum-product (belief-propagation) decoding over a BSC. Returns ``(decoded_word, converged)`` where
    ``converged`` is True iff the hard decision satisfies every parity check.
    """
    H = np.asarray(H, dtype=int)
    m, n = H.shape
    tg = tanner_graph(H)
    Lch = bsc_llr(received, p)
    # messages M[i][j] variable j -> check i, initialised to channel LLR
    M = {i: {j: Lch[j] for j in tg["checks"][i]} for i in range(m)}
    E = {i: {j: 0.0 for j in tg["checks"][i]} for i in range(m)}
    decoded = np.asarray(received, dtype=int).copy()
    for _ in range(max_iter):
        # check -> variable
        for i in range(m):
            nbrs = tg["checks"][i]
            for j in nbrs:
                prod = 1.0
                for k in nbrs:
                    if k != j:
                        prod *= np.tanh(np.clip(M[i][k] / 2.0, -30, 30))
                prod = np.clip(prod, -1 + 1e-12, 1 - 1e-12)
                E[i][j] = 2.0 * np.arctanh(prod)
        # variable -> check + posterior
        total = Lch.copy()
        for j in range(n):
            total[j] = Lch[j] + sum(E[i][j] for i in tg["bits"][j])
        for i in range(m):
            for j in tg["checks"][i]:
                M[i][j] = Lch[j] + sum(E[k][j] for k in tg["bits"][j] if k != i)
        decoded = (total < 0).astype(int)
        if np.all(syndrome(H, decoded) == 0):
            return decoded, True
    return decoded, False


def min_sum_decode(H, received, p=0.05, max_iter=50):
    """
    Min-sum decoding: the low-complexity approximation to sum-product, replacing the ``tanh`` rule
    with a sign-product and minimum magnitude. Returns ``(decoded_word, converged)``.
    """
    H = np.asarray(H, dtype=int)
    m, n = H.shape
    tg = tanner_graph(H)
    Lch = bsc_llr(received, p)
    M = {i: {j: Lch[j] for j in tg["checks"][i]} for i in range(m)}
    E = {i: {j: 0.0 for j in tg["checks"][i]} for i in range(m)}
    decoded = np.asarray(received, dtype=int).copy()
    for _ in range(max_iter):
        for i in range(m):
            nbrs = tg["checks"][i]
            for j in nbrs:
                others = [M[i][k] for k in nbrs if k != j]
                if not others:
                    E[i][j] = 0.0
                    continue
                sign = np.prod([np.sign(o) if o != 0 else 1.0 for o in others])
                E[i][j] = sign * min(abs(o) for o in others)
        total = Lch.copy()
        for j in range(n):
            total[j] = Lch[j] + sum(E[i][j] for i in tg["bits"][j])
        for i in range(m):
            for j in tg["checks"][i]:
                M[i][j] = Lch[j] + sum(E[k][j] for k in tg["bits"][j] if k != i)
        decoded = (total < 0).astype(int)
        if np.all(syndrome(H, decoded) == 0):
            return decoded, True
    return decoded, False


def bp_decode_error(H, error, p=0.05, max_iter=50, decoder=sum_product_decode):
    """
    Decode the received word ``codeword=0 XOR error`` (transmitting the all-zero codeword) and return
    the *recovered error estimate*. Correct iff it equals ``error``.
    """
    error = np.asarray(error, dtype=int)
    decoded, _ = decoder(H, error, p=p, max_iter=max_iter)
    return decoded


def bp_corrects(H, error, p=0.05, max_iter=50, decoder=sum_product_decode):
    """True iff belief propagation recovers the all-zero codeword from ``error`` (i.e. the decoded
    word is the zero codeword)."""
    decoded = bp_decode_error(H, error, p=p, max_iter=max_iter, decoder=decoder)
    return bool(np.all(decoded == 0))


def bp_matches_ml_on_weight1(H, p=0.05, max_iter=50):
    """
    Verify belief propagation corrects *every* single-bit error (matching the maximum-likelihood
    decoder) -- the acid test on a code whose minimum distance is ``>= 3``. Returns True iff all
    ``n`` weight-1 errors decode back to the zero codeword.
    """
    H = np.asarray(H, dtype=int)
    n = H.shape[1]
    for j in range(n):
        e = np.zeros(n, dtype=int)
        e[j] = 1
        if not bp_corrects(H, e, p=p, max_iter=max_iter):
            return False
    return True
