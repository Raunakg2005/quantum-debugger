"""
Schmidt decomposition, entanglement spectrum & the area law

Any pure bipartite state can be written as a single sum

    |psi> = sum_i lambda_i |i>_A |i>_B,      lambda_i >= 0,  sum lambda_i^2 = 1,

the Schmidt decomposition (a singular-value decomposition of the state reshaped as an
A-by-B matrix). The Schmidt coefficients ``lambda_i`` are the square roots of the
reduced density matrix's eigenvalues, so the entanglement entropy is
``S = -sum lambda_i^2 log2 lambda_i^2`` and the number of non-zero ``lambda_i`` (the
Schmidt rank) is the minimal bond dimension needed to represent the state.

The decay of the Schmidt spectrum is what makes tensor networks work: ground states of
gapped, local 1D Hamiltonians obey an **area law** -- only a few ``lambda_i`` are
appreciable, so the state compresses to a low-bond-dimension matrix product state. A
generic (volume-law) state has a flat spectrum and cannot be compressed. This module
computes the decomposition, the spectrum, and the truncation fidelity that quantifies
that compressibility.
"""

import numpy as np


def _bipartition_matrix(state, n, region):
    rest = [q for q in range(n) if q not in region]
    perm = list(region) + rest
    tensor = np.asarray(state, dtype=complex).reshape([2] * n).transpose(perm)
    return tensor.reshape(2 ** len(region), 2 ** len(rest))


def schmidt_decomposition(state_vector, region) -> dict:
    """
    Schmidt decomposition of ``state_vector`` across ``region`` vs the rest.

    Returns dict with ``schmidt_values`` (the ``lambda_i``, descending),
    ``schmidt_rank`` (count of non-negligible values), and ``entropy`` (the
    entanglement entropy in bits). The Schmidt values are the singular values of the
    state reshaped as an A-by-B matrix.
    """
    state = np.asarray(state_vector, dtype=complex)
    state = state / np.linalg.norm(state)
    n = int(round(np.log2(len(state))))
    M = _bipartition_matrix(state, n, list(region))
    s = np.linalg.svd(M, compute_uv=False)
    s = s[s > 1e-12]
    s2 = s**2
    entropy = float(-np.sum(s2 * np.log2(s2)))
    return {
        "schmidt_values": s,
        "schmidt_rank": int(len(s)),
        "entropy": entropy,
    }


def truncation_fidelity(state_vector, region, bond_dim: int) -> float:
    """
    Fidelity retained when the Schmidt spectrum is truncated to the largest
    ``bond_dim`` values: ``sum_{i < bond_dim} lambda_i^2``. Near 1 for an area-law
    (compressible) state at small ``bond_dim``; far from 1 for a volume-law state.
    """
    s = schmidt_decomposition(state_vector, region)["schmidt_values"]
    kept = s[:bond_dim] ** 2
    return float(np.sum(kept))


def area_law_compressibility(state_vector, region, bond_dim: int = 2) -> dict:
    """
    Quantify how well ``state_vector`` compresses to bond dimension ``bond_dim`` across
    the ``region`` cut.

    Returns dict with ``entropy``, ``schmidt_rank``, ``truncation_fidelity`` (at
    ``bond_dim``), and ``compressible`` (fidelity > 0.99 -- an area-law state keeps
    almost all its weight in a handful of Schmidt values).
    """
    d = schmidt_decomposition(state_vector, region)
    fid = truncation_fidelity(state_vector, region, bond_dim)
    return {
        "entropy": d["entropy"],
        "schmidt_rank": d["schmidt_rank"],
        "truncation_fidelity": fid,
        "compressible": fid > 0.99,
    }
