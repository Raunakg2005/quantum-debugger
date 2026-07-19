"""Tests for gate decomposition / synthesis."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    zyz_decompose,
    abc_decomposition,
    kak_decompose,
    canonical_coordinates,
)

try:
    from scipy.stats import unitary_group

    _HAVE_SCIPY_STATS = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY_STATS = False

CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
ISWAP = np.array(
    [[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, 1]], dtype=complex
)


def _rand_u(dim, seed):
    if _HAVE_SCIPY_STATS:
        return unitary_group.rvs(dim, random_state=seed)
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    q, r = np.linalg.qr(z)
    return q @ np.diag(np.exp(1j * np.angle(np.diag(r))))


class TestZYZ:
    @pytest.mark.parametrize("seed", range(20))
    def test_reconstructs_random(self, seed):
        assert zyz_decompose(_rand_u(2, seed))["reconstruction_error"] < 1e-9

    def test_named_gates(self):
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        assert zyz_decompose(H)["reconstruction_error"] < 1e-9


class TestABC:
    @pytest.mark.parametrize("seed", range(20))
    def test_abc_is_identity_and_reconstructs(self, seed):
        d = abc_decomposition(_rand_u(2, seed))
        assert d["abc_is_identity"] < 1e-9
        assert d["reconstruction_error"] < 1e-9


class TestKAK:
    @pytest.mark.parametrize("gate", [CNOT, SWAP, ISWAP])
    def test_named_gates(self, gate):
        assert kak_decompose(gate)["reconstruction_error"] < 1e-9

    @pytest.mark.parametrize("seed", range(30))
    def test_reconstructs_random_su4(self, seed):
        assert kak_decompose(_rand_u(4, seed))["reconstruction_error"] < 1e-8

    def test_canonical_coordinates(self):
        a, b, c = canonical_coordinates(CNOT)
        assert np.isclose(abs(a), np.pi / 4, atol=1e-6)
        assert abs(b) < 1e-6 and abs(c) < 1e-6

    def test_pure_local_has_zero_interaction(self):
        loc = np.kron(_rand_u(2, 7), _rand_u(2, 8))
        d = kak_decompose(loc)
        assert d["reconstruction_error"] < 1e-8
        assert max(abs(x) for x in d["coefficients"]) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
