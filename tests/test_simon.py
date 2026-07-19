"""Tests for Simon's algorithm."""

import pytest

from quantum_debugger.algorithms import simon, simon_oracle


class TestSimon:
    @pytest.mark.parametrize("n", [2, 3])
    def test_recovers_all_secrets(self, n):
        for s in range(1, 2**n):
            result = simon(s=s, n=n, seed=s)
            assert result["secret"] == s

    def test_n4_examples(self):
        for s in (6, 9, 15):
            assert simon(s=s, n=4, seed=s)["secret"] == s

    def test_equations_orthogonal_to_secret(self):
        r = simon(s=5, n=3, seed=1)
        for y in r["equations"]:
            assert bin(y & 5).count("1") % 2 == 0  # y . s = 0 (mod 2)

    def test_custom_function(self):
        # f(x) = min(x, x^3) has hidden mask s = 3.
        f = lambda x: min(x, x ^ 3)
        assert simon(n=3, f=f, seed=2)["secret"] == 3


class TestSimonOracle:
    def test_oracle_is_permutation(self):
        import numpy as np

        U = simon_oracle(lambda x: min(x, x ^ 3), 2)
        assert np.allclose(U @ U.conj().T, np.eye(U.shape[0]))
        # exactly one 1 per column
        assert np.allclose(U.sum(axis=0), 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
