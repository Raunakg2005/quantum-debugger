"""
Low-density parity-check (LDPC) codes and their Tanner graphs.

A linear code is defined by a parity-check matrix ``H`` over GF(2): the codewords are the vectors
``c`` with ``H c = 0 (mod 2)``. LDPC codes are the special case where ``H`` is *sparse* -- few ones
per row and column -- which is exactly what makes iterative message-passing decoding (belief
propagation, bit-flipping) efficient and near-capacity. The sparsity structure is captured by the
**Tanner graph**: a bipartite graph with one node per code bit and one per parity check, an edge
wherever ``H`` has a one.

This module builds parity-check matrices (repetition, Hamming, random regular LDPC), the Tanner
graph and its degree/girth structure, the syndrome map, and the code parameters ``[n, k, d]`` -- the
last two from GF(2) rank and brute-force minimum distance. Every property is checked against an
exact reference (the ``2^k`` enumerated codewords, distinct single-error syndromes, and the
``[7,4,3]`` Hamming code).
"""

import itertools

import numpy as np

from .css_code import gf2_rank, gf2_nullspace


def repetition_check(n):
    """Parity-check matrix of the length-``n`` repetition code ``[n, 1, n]`` -- ``n-1`` checks each
    tying two adjacent bits."""
    H = np.zeros((n - 1, n), dtype=int)
    for i in range(n - 1):
        H[i, i] = 1
        H[i, i + 1] = 1
    return H


def hamming_code_check(r=3):
    """Parity-check matrix of the ``[2^r - 1, 2^r - 1 - r, 3]`` Hamming code: its columns are all the
    non-zero length-``r`` binary vectors. For ``r = 3`` this is the ``[7, 4, 3]`` code."""
    n = 2 ** r - 1
    cols = [np.array([(j >> b) & 1 for b in range(r)]) for j in range(1, n + 1)]
    return np.array(cols).T


def syndrome(H, word):
    """The syndrome ``H w (mod 2)`` of a word -- zero iff ``w`` is a codeword."""
    H = np.asarray(H, dtype=int)
    w = np.asarray(word, dtype=int)
    return (H @ w) % 2


def is_codeword(H, word):
    """True iff ``word`` satisfies every parity check (zero syndrome)."""
    return bool(np.all(syndrome(H, word) == 0))


def all_codewords(H):
    """Enumerate every codeword (the GF(2) null space of ``H``), returned as rows -- feasible only
    for small codes."""
    basis = gf2_nullspace(np.asarray(H, dtype=int))
    k = len(basis)
    if k == 0:
        return np.zeros((1, np.asarray(H).shape[1]), dtype=int)
    words = []
    B = np.array(basis, dtype=int)
    for bits in itertools.product([0, 1], repeat=k):
        words.append((np.array(bits) @ B) % 2)
    return np.array(words, dtype=int)


def code_dimension(H):
    """The number of logical bits ``k = n - rank(H)`` over GF(2)."""
    H = np.asarray(H, dtype=int)
    return H.shape[1] - gf2_rank(H)


def code_rate(H):
    """The code rate ``k / n``."""
    H = np.asarray(H, dtype=int)
    return code_dimension(H) / H.shape[1]


def code_parameters(H):
    """The ``[n, k, d]`` parameters: block length, dimension (``n - rank H``), and minimum
    distance (brute force over non-zero codewords)."""
    H = np.asarray(H, dtype=int)
    return {"n": H.shape[1], "k": code_dimension(H), "d": minimum_distance(H)}


def minimum_distance(H):
    """The minimum distance: the smallest Hamming weight among non-zero codewords (brute force)."""
    cw = all_codewords(H)
    weights = cw.sum(axis=1)
    nonzero = weights[weights > 0]
    return int(nonzero.min()) if nonzero.size else 0


def tanner_graph(H):
    """
    The Tanner graph of ``H`` as an adjacency dict: ``{'checks': {check -> [bits]}, 'bits': {bit ->
    [checks]}}``. An edge joins check ``i`` to bit ``j`` iff ``H[i, j] = 1``.
    """
    H = np.asarray(H, dtype=int)
    m, n = H.shape
    checks = {i: [j for j in range(n) if H[i, j]] for i in range(m)}
    bits = {j: [i for i in range(m) if H[i, j]] for j in range(n)}
    return {"checks": checks, "bits": bits}


def column_weights(H):
    """Number of checks each bit participates in (the column weights of ``H``)."""
    return np.asarray(H, dtype=int).sum(axis=0)


def row_weights(H):
    """Number of bits each check involves (the row weights of ``H``)."""
    return np.asarray(H, dtype=int).sum(axis=1)


def is_regular(H):
    """True iff every column has the same weight and every row has the same weight (a regular LDPC
    code)."""
    cw = column_weights(H)
    rw = row_weights(H)
    return bool(np.all(cw == cw[0]) and np.all(rw == rw[0]))


def tanner_girth(H, max_len=12):
    """
    The girth of the Tanner graph -- the length of its shortest cycle (always even), or ``inf`` if
    it is a forest. Short cycles (girth 4) hurt belief-propagation decoding.
    """
    H = np.asarray(H, dtype=int)
    m, n = H.shape
    # BFS from each check node over the bipartite graph, tracking the shortest cycle
    adj = {("c", i): [("b", j) for j in range(n) if H[i, j]] for i in range(m)}
    adj.update({("b", j): [("c", i) for i in range(m) if H[i, j]] for j in range(n)})
    best = np.inf
    for src in adj:
        dist = {src: 0}
        parent = {src: None}
        stack = [src]
        while stack:
            u = stack.pop(0)
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    stack.append(v)
                elif parent[u] != v:
                    best = min(best, dist[u] + dist[v] + 1)
    return best if best == np.inf else int(best)


def random_regular_ldpc(n, col_weight, row_weight, seed=0):
    """
    A random regular LDPC parity-check matrix with the given column/row weights (via a permuted
    edge socket assignment). Requires ``n * col_weight`` divisible by ``row_weight``; the result is
    a valid (possibly with a few multi-edges collapsed) sparse ``H``.
    """
    rng = np.random.default_rng(seed)
    n_edges = n * col_weight
    if n_edges % row_weight != 0:
        raise ValueError("n*col_weight must be divisible by row_weight")
    m = n_edges // row_weight
    bit_sockets = np.repeat(np.arange(n), col_weight)
    rng.shuffle(bit_sockets)
    H = np.zeros((m, n), dtype=int)
    for e, bit in enumerate(bit_sockets):
        check = e // row_weight
        H[check, bit] = 1  # collapse any accidental double edge to a single one
    return H
