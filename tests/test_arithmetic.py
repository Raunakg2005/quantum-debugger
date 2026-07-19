"""Tests for quantum arithmetic (Draper QFT adder)."""

import pytest

from quantum_debugger.algorithms import (
    qft_add,
    quantum_adder,
    qft_subtract,
    quantum_compare,
    ripple_carry_add,
)


class TestConstantAdder:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_all_pairs(self, n):
        mod = 2**n
        assert all(
            qft_add(a, b, n) == (a + b) % mod for a in range(mod) for b in range(mod)
        )

    def test_wraps_modulo(self):
        assert qft_add(13, 7, 4) == 4  # 20 mod 16
        assert qft_add(15, 15, 4) == 14  # 30 mod 16


class TestQuantumAdder:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_all_pairs(self, n):
        mod = 2**n
        assert all(
            quantum_adder(a, b, n) == (a + b) % mod
            for a in range(mod)
            for b in range(mod)
        )

    def test_examples(self):
        assert quantum_adder(9, 6, 4) == 15
        assert quantum_adder(1, 0, 3) == 1
        assert quantum_adder(0, 0, 3) == 0


class TestSubtractor:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_all_pairs(self, n):
        mod = 2**n
        assert all(
            qft_subtract(a, b, n) == (a - b) % mod
            for a in range(mod)
            for b in range(mod)
        )

    def test_examples(self):
        assert qft_subtract(5, 8, 4) == 13  # -3 mod 16
        assert qft_subtract(7, 7, 4) == 0


class TestRippleCarryAdder:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_exact_sum_all_pairs(self, n):
        mod = 2**n
        assert all(
            ripple_carry_add(a, b, n) == a + b for a in range(mod) for b in range(mod)
        )

    def test_carry_out(self):
        assert ripple_carry_add(15, 15, 4) == 30  # carry-out set
        assert ripple_carry_add(9, 7, 4) == 16


class TestComparator:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_all_pairs(self, n):
        mod = 2**n
        for a in range(mod):
            for b in range(mod):
                r = quantum_compare(a, b, n)
                assert r["a_geq_b"] == (a >= b)
                assert r["a_lt_b"] == (a < b)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
