"""
Tensor-network contraction: cost analysis and optimal ordering.

Contracting a tensor network is repeated pairwise index summation, but the *order* of
contractions determines the cost -- often by orders of magnitude. The matrix-chain product is
the canonical example: multiplying ``A_1 A_2 ... A_n`` gives the same result for any
parenthesization, but the number of scalar multiplications varies widely, and the optimal order
is found by a classic dynamic program. This module contracts tensors and matrix chains, scores
the FLOP cost of a contraction, and computes the optimal vs. naive order -- verifying that the
result is order-independent while the cost is not.
"""

import numpy as np


def contract_pair(A, B, axes):
    """Contract two tensors over ``axes`` (a pair of axis lists) -- the atomic pairwise
    contraction (``numpy.tensordot``)."""
    return np.tensordot(np.asarray(A), np.asarray(B), axes=axes)


def pairwise_cost(dims_a: dict, dims_b: dict) -> int:
    """
    FLOP cost of contracting two tensors given as ``{label: dimension}`` dicts over their shared
    labels: the product of the dimensions of *all* indices involved (open plus shared).
    """
    dims = {**dims_a, **dims_b}
    return int(np.prod([dims[l] for l in dims]))


def contract_chain(matrices):
    """The matrix-chain product ``A_1 A_2 ... A_n`` -- the reference result every contraction
    order must reproduce."""
    out = np.asarray(matrices[0])
    for M in matrices[1:]:
        out = out @ np.asarray(M)
    return out


def matrix_chain_left_cost(dims) -> int:
    """
    Scalar-multiplication cost of the naive left-to-right product ``((A_1 A_2) A_3) ...`` --
    matrix ``i`` is ``dims[i-1] x dims[i]`` (``dims`` has length ``n+1``). The baseline the
    optimal order improves on.
    """
    n = len(dims) - 1
    total = 0
    for k in range(2, n + 1):
        total += dims[0] * dims[k - 1] * dims[k]
    return int(total)


def matrix_chain_optimal_cost(dims) -> int:
    """
    Optimal matrix-chain cost by the standard dynamic program: the minimal scalar-multiplication
    count over all parenthesizations. Verified ``<=`` the naive left-to-right cost.
    """
    n = len(dims) - 1
    m = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            m[i][j] = min(m[i][k] + m[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return int(m[0][n - 1])


def matrix_chain_optimal_order(dims):
    """
    The optimal parenthesization split points of a matrix chain (recovered from the dynamic
    program) -- the contraction order achieving :func:`matrix_chain_optimal_cost`.
    """
    n = len(dims) - 1
    m = [[0] * n for _ in range(n)]
    s = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            best = None
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if best is None or cost < best:
                    best, s[i][j] = cost, k
            m[i][j] = best

    def build(i, j):
        if i == j:
            return i
        return (build(i, s[i][j]), build(s[i][j] + 1, j))
    return build(0, n - 1)


def svd_bond_truncation(matrix, bond: int):
    """
    Truncate a matrix (a tensor bipartition) to bond dimension ``bond`` by keeping the largest
    ``bond`` singular values, and return ``(approx, retained_fidelity)`` where the fidelity is the
    fraction of squared-singular-value weight kept -- the core MPS/tensor-network compression
    step. Verified 1 when ``bond`` exceeds the rank.
    """
    M = np.asarray(matrix, dtype=complex)
    U, s, Vh = np.linalg.svd(M, full_matrices=False)
    k = min(bond, len(s))
    approx = (U[:, :k] * s[:k]) @ Vh[:k]
    fidelity = float(np.sum(s[:k] ** 2) / np.sum(s ** 2))
    return approx, fidelity


def contraction_speedup(dims) -> float:
    """The cost ratio ``left / optimal`` of a matrix chain -- how much the optimal order saves.
    ``>= 1``, and large for a badly shaped chain."""
    return float(matrix_chain_left_cost(dims) / matrix_chain_optimal_cost(dims))
