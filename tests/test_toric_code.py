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



class TestDecoder:
    @pytest.mark.parametrize("L", [3, 4, 5])
    def test_corrects_all_weight_one_errors(self, L):
        code = ToricCode(L)
        for e in range(code.n):
            z = np.zeros(code.n, dtype=int)
            z[e] = 1
            assert code.decode_z(z)["success"]

    def test_no_error_trivial_syndrome(self):
        code = ToricCode(3)
        r = code.decode_z(np.zeros(code.n, dtype=int))
        assert r["syndrome"] == []
        assert r["success"]

    def test_syndrome_even_number_of_defects(self):
        code = ToricCode(3)
        rng = np.random.default_rng(0)
        for _ in range(10):
            z = rng.integers(0, 2, code.n)
            assert len(code.z_syndrome(z)) % 2 == 0

    def test_single_error_two_defects(self):
        code = ToricCode(3)
        z = np.zeros(code.n, dtype=int)
        z[0] = 1
        assert len(code.z_syndrome(z)) == 2

    def test_stabilizer_error_no_syndrome(self):
        # Applying a whole plaquette (a Z-stabilizer) triggers no star defects.
        code = ToricCode(3)
        _, zplaq = code.plaquettes[4]
        assert code.z_syndrome(zplaq) == []
        assert code.decode_z(zplaq)["success"]

    def test_logical_error_detected_for_half_loop(self):
        # A Z string along a full logical loop is uncorrectable (it IS a logical op):
        # its syndrome is trivial but it flips the logical qubit.
        code = ToricCode(3)
        _, zlog = code.logical_z
        r = code.decode_z(zlog)
        assert r["syndrome"] == []          # no defects to see
        assert r["logical_error"]           # but it is a logical flip

class TestXDecoder:
    @pytest.mark.parametrize("L", [3, 4, 5])
    def test_corrects_all_weight_one_x_errors(self, L):
        code = ToricCode(L)
        for e in range(code.n):
            x = np.zeros(code.n, dtype=int)
            x[e] = 1
            assert code.decode_x(x)["success"]

    def test_x_single_error_two_defects(self):
        code = ToricCode(3)
        x = np.zeros(code.n, dtype=int)
        x[0] = 1
        assert len(code.x_syndrome(x)) == 2

    def test_x_stabilizer_no_syndrome(self):
        # A whole star (X-stabilizer) triggers no plaquette defects.
        code = ToricCode(3)
        xstar, _ = code.stars[4]
        assert code.x_syndrome(xstar) == []
        assert code.decode_x(xstar)["success"]

    def test_x_logical_loop_is_logical_error(self):
        code = ToricCode(3)
        xlog, _ = code.logical_x
        r = code.decode_x(xlog)
        assert r["syndrome"] == []
        assert r["logical_error"]



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
