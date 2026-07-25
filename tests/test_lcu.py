"""Tests for Linear Combination of Unitaries (LCU)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import lcu_block_encoding, lcu_matrix

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


class TestLCU:
    def test_pauli_sum_block_encoded(self):
        coeffs = [0.5, 0.3, 0.2]
        Us = [_X, _Z, _Y]
        r = lcu_block_encoding(coeffs, Us)
        H = lcu_matrix(coeffs, Us)
        top = r["unitary"][:2, :2]
        assert np.allclose(top, H / r["subnormalization"], atol=1e-9)

    def test_unitary(self):
        r = lcu_block_encoding([0.4, 0.6], [_X, _Z])
        U = r["unitary"]
        assert np.allclose(U.conj().T @ U, np.eye(U.shape[0]), atol=1e-9)

    def test_subnormalization_is_coeff_sum(self):
        r = lcu_block_encoding([0.5, 0.3, 0.2, 0.1], [_X, _Y, _Z, _I])
        assert abs(r["subnormalization"] - 1.1) < 1e-12

    def test_non_power_of_two_terms(self):
        # 3 terms -> ancilla padded to 4; the padding acts as identity.
        coeffs = [0.5, 0.3, 0.2]
        Us = [_X, _Y, _Z]
        r = lcu_block_encoding(coeffs, Us)
        top = r["unitary"][:2, :2]
        assert np.allclose(top, lcu_matrix(coeffs, Us) / r["subnormalization"], atol=1e-9)

    def test_single_unitary(self):
        # One term: block encodes U exactly (subnormalization 1).
        r = lcu_block_encoding([1.0], [_X])
        assert abs(r["subnormalization"] - 1.0) < 1e-12
        assert np.allclose(r["unitary"][:2, :2], _X, atol=1e-9)

    def test_two_qubit_operators(self):
        coeffs = [0.6, 0.4]
        Us = [np.kron(_X, _Z), np.kron(_Z, _X)]
        r = lcu_block_encoding(coeffs, Us)
        H = lcu_matrix(coeffs, Us)
        assert np.allclose(r["unitary"][:4, :4], H / r["subnormalization"], atol=1e-9)

    def test_negative_coeff_rejected(self):
        with pytest.raises(ValueError):
            lcu_block_encoding([0.5, -0.3], [_X, _Z])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
