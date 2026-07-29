"""
Matrix Product Operators (MPO)

The operator analogue of a matrix product state: a many-body operator ``H`` written as
a chain of rank-4 tensors ``W[i]`` of shape ``(D_left, 2, 2, D_right)`` (bond, physical
out, physical in, bond). Local Hamiltonians have a *small* MPO bond dimension -- the
transverse-field Ising model needs only 3 -- so ``<psi|H|psi>`` on a matrix product
state costs ``O(n * chi^2 * D^2)`` with no dense operator ever formed. MPOs are the
operator input to DMRG and MPS-based time evolution.
"""

import numpy as np

_I = np.eye(2, dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)


def tfim_mpo(n: int, j_coupling: float = 1.0, field: float = 1.0) -> list:
    """
    Bond-dimension-3 MPO for the transverse-field Ising Hamiltonian
    ``H = -J sum Z Z - h sum X`` on ``n`` sites. Returns the list of ``W`` tensors.
    """
    W = np.zeros((3, 2, 2, 3), dtype=complex)
    W[0, :, :, 0] = _I
    W[1, :, :, 0] = _Z
    W[2, :, :, 0] = -field * _X
    W[2, :, :, 1] = -j_coupling * _Z
    W[2, :, :, 2] = _I
    tensors = []
    for i in range(n):
        if i == 0:
            tensors.append(W[2:3, :, :, :])   # left boundary row
        elif i == n - 1:
            tensors.append(W[:, :, :, 0:1])   # right boundary column
        else:
            tensors.append(W)
    return tensors


def mpo_expectation(mps, mpo) -> float:
    """
    Expectation ``<psi|H|psi>`` of an MPO ``mpo`` for a matrix product state ``mps``, by
    sweeping the three-layer (bra, operator, ket) contraction -- no dense operator.
    """
    E = np.ones((1, 1, 1), dtype=complex)  # (bra bond, mpo bond, ket bond)
    for A, W in zip(mps.tensors, mpo):
        E = np.einsum("lmn,nSr->lmSr", E, A)        # absorb ket tensor
        E = np.einsum("lmSr,mSTw->lTrw", E, W)      # apply operator tensor
        E = np.einsum("lTrw,lTb->wrb", E, np.conj(A))  # absorb bra tensor
        E = E.transpose(2, 0, 1)
    return float(np.real(E[0, 0, 0]))


def mpo_to_matrix(mpo) -> np.ndarray:
    """Contract an MPO into its dense ``2^n x 2^n`` operator (small ``n``, for checking)."""
    n = len(mpo)
    T = mpo[0]
    for W in mpo[1:]:
        T = np.tensordot(T, W, axes=(T.ndim - 1, 0))
    # T axes: bond_l, (out,in) per site, bond_r -> reshape
    T = T[0, ..., 0]  # drop trivial boundary bonds
    outs = list(range(0, 2 * n, 2))
    ins = list(range(1, 2 * n, 2))
    T = T.transpose(outs + ins)
    dim = 2**n
    M = T.reshape(dim, dim)
    # little-endian reordering to match the rest of the library
    perm = list(range(n - 1, -1, -1))
    Mt = M.reshape([2] * (2 * n)).transpose(perm + [n + p for p in perm]).reshape(dim, dim)
    return Mt
