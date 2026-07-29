"""Tests for the toric code (topological QEC)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import ToricCode


class TestStructure:
    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_qubit_count(self, L):
        assert ToricCode(L).n == 2 * L * L

    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_stabilizer_counts(self, L):
        code = ToricCode(L)
        assert len(code.stars) == L * L
        assert len(code.plaquettes) == L * L

    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_encodes_two_logical_qubits(self, L):
        assert ToricCode(L).num_logical_qubits() == 2

    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_all_stabilizers_commute(self, L):
        assert ToricCode(L).all_commute()

    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_distance_is_L(self, L):
        assert ToricCode(L).distance() == L


class TestLogicalOperators:
    @pytest.mark.parametrize("L", [2, 3, 4])
    def test_logicals_valid(self, L):
        # Commute with all stabilizers, anticommute with each other.
        assert ToricCode(L).logicals_valid()

    def test_two_independent_constraints(self):
        # 2L^2 stabilizers but rank 2L^2 - 2 (the two product constraints).
        L = 3
        code = ToricCode(L)
        from quantum_debugger.algorithms.toric_code import _gf2_rank

        assert _gf2_rank(code.check_matrix()) == 2 * L * L - 2

    def test_star_is_x_type(self):
        code = ToricCode(2)
        for x, z in code.stars:
            assert z.sum() == 0 and x.sum() == 4  # X on 4 edges

    def test_plaquette_is_z_type(self):
        code = ToricCode(2)
        for x, z in code.plaquettes:
            assert x.sum() == 0 and z.sum() == 4  # Z on 4 edges


class TestValidation:
    def test_rejects_small_lattice(self):
        with pytest.raises(ValueError):
            ToricCode(1)

    def test_check_matrix_shape(self):
        L = 3
        code = ToricCode(L)
        assert code.check_matrix().shape == (2 * L * L, 2 * code.n)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
