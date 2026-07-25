"""
Block encoding & qubitization

Quantum algorithms act with unitaries, but the objects we care about -- Hamiltonians,
data matrices -- are usually not unitary. A **block encoding** hides a matrix ``A``
(with ``||A|| <= 1``) in the top-left corner of a bigger unitary,

    U = [[ A,            sqrt(I - A^2) ],
         [ sqrt(I-A^2),  -A            ]],

so ``<0|_a U |0>_a = A``. Combined with an ancilla reflection ``2|0><0| - I`` it
becomes the **qubitization walk operator** ``W = U (2 Pi - I)``, which acts as a
rotation by ``arccos(lambda)`` in each eigenspace of a Hermitian ``A``. Its powers
therefore realize the Chebyshev polynomials of the matrix:

    <0|_a W^d |0>_a = T_d(A),

the seed of quantum singular value transformation and modern Hamiltonian-simulation
and linear-algebra algorithms. This module builds the encoding and the walk and
verifies the matrix-Chebyshev identity.
"""

import numpy as np
from scipy.linalg import sqrtm


def block_encode(matrix) -> np.ndarray:
    """
    Block-encode a Hermitian ``matrix`` ``A`` with spectral norm ``<= 1`` into a
    ``2d x 2d`` unitary whose top-left ``d x d`` block is ``A``. Uses the standard
    ``[[A, sqrt(I-A^2)], [sqrt(I-A^2), -A]]`` construction.
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    comp = sqrtm(np.eye(d) - A @ A)
    return np.block([[A, comp], [comp, -A]])


def top_left_block(unitary, dim: int) -> np.ndarray:
    """Extract the top-left ``dim x dim`` block (the ``<0|_a . |0>_a`` component)."""
    return np.asarray(unitary, dtype=complex)[:dim, :dim]


def is_block_encoding(unitary, matrix, atol: float = 1e-9) -> bool:
    """Check that ``unitary`` is a valid block encoding of ``matrix`` (unitary, and its
    top-left block equals the matrix)."""
    U = np.asarray(unitary, dtype=complex)
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    if not np.allclose(U.conj().T @ U, np.eye(U.shape[0]), atol=atol):
        return False
    return bool(np.allclose(top_left_block(U, d), A, atol=atol))


def qubitization_walk(block_encoding) -> np.ndarray:
    """
    The qubitization walk operator ``W = U (2 Pi - I)``, where ``Pi = |0><0|_a`` is the
    ancilla projector. For a Hermitian block-encoded ``A``, ``W`` rotates by
    ``arccos(lambda)`` in each eigenspace.
    """
    U = np.asarray(block_encoding, dtype=complex)
    dim2 = U.shape[0]
    d = dim2 // 2
    reflection = np.eye(dim2, dtype=complex)
    reflection[d:, d:] *= -1  # 2 Pi - I
    return U @ reflection


def chebyshev_of_matrix(matrix, degree: int) -> np.ndarray:
    """
    The Chebyshev polynomial ``T_degree(A)`` of a Hermitian ``matrix`` (``||A|| <= 1``),
    realized by ``<0|_a W^degree |0>_a`` with ``W`` the qubitization walk -- the
    quantum-walk route to a matrix function. Equals the classical
    ``sum_i T_degree(lambda_i) |v_i><v_i|``.
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    W = qubitization_walk(block_encode(A))
    return top_left_block(np.linalg.matrix_power(W, degree), d)
