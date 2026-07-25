"""Tests for block encoding and qubitization."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    block_encode,
    top_left_block,
    is_block_encoding,
    qubitization_walk,
    chebyshev_of_matrix,
)


def _random_hermitian(d, seed, norm=0.8):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    A = (M + M.conj().T) / 2
    return A / (np.linalg.norm(A, 2) / norm)  # rescale to spectral norm `norm`


class TestBlockEncoding:
    @pytest.mark.parametrize("d,seed", [(2, 0), (3, 1), (4, 2)])
    def test_is_valid_block_encoding(self, d, seed):
        A = _random_hermitian(d, seed)
        U = block_encode(A)
        assert is_block_encoding(U, A)

    def test_top_block_is_matrix(self):
        A = _random_hermitian(3, 0)
        assert np.allclose(top_left_block(block_encode(A), 3), A, atol=1e-9)

    def test_unitary(self):
        A = _random_hermitian(3, 5)
        U = block_encode(A)
        assert np.allclose(U.conj().T @ U, np.eye(6), atol=1e-9)

    def test_rejects_non_encoding(self):
        A = _random_hermitian(3, 0)
        assert not is_block_encoding(np.eye(6), A)


class TestQubitizationChebyshev:
    @pytest.mark.parametrize("degree", [1, 2, 3, 4, 5, 6])
    def test_matches_matrix_chebyshev(self, degree):
        A = _random_hermitian(3, degree)
        w, v = np.linalg.eigh(A)
        classical = v @ np.diag(np.cos(degree * np.arccos(np.clip(w, -1, 1)))) @ v.conj().T
        assert np.allclose(chebyshev_of_matrix(A, degree), classical, atol=1e-9)

    def test_degree_one_is_matrix(self):
        A = _random_hermitian(3, 0)
        assert np.allclose(chebyshev_of_matrix(A, 1), A, atol=1e-9)

    def test_degree_two_is_2A2_minus_I(self):
        A = _random_hermitian(3, 1)
        expected = 2 * A @ A - np.eye(3)
        assert np.allclose(chebyshev_of_matrix(A, 2), expected, atol=1e-9)

    def test_walk_is_unitary(self):
        A = _random_hermitian(3, 2)
        W = qubitization_walk(block_encode(A))
        assert np.allclose(W.conj().T @ W, np.eye(6), atol=1e-9)

    def test_diagonal_matrix(self):
        # For a diagonal A, T_d(A) is diagonal with T_d(a_ii).
        A = np.diag([0.3, -0.5, 0.8]).astype(complex)
        out = chebyshev_of_matrix(A, 3)
        expected = np.diag([np.cos(3 * np.arccos(x)) for x in (0.3, -0.5, 0.8)])
        assert np.allclose(out, expected, atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
