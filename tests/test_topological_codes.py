"""
Tests for the 1.3.0 topological-QEC backfill: the general CSS-code machinery,
the hypergraph product, the planar surface code, the color code's transversal
Clifford gates, and the toric-code logical bookkeeping. Everything is checked
against the exact stabilizer / logical structure.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.css_code import (
    CSSCode, gf2_rank, gf2_nullspace, css_from_classical, hypergraph_product)
from quantum_debugger.algorithms.surface_code import (
    repetition_check_matrix, hamming_check_matrix, planar_surface_code,
    surface_code_parameters, corrects_all_errors_up_to)
from quantum_debugger.algorithms.color_code import (
    steane_color_code, is_self_dual_css, transversal_hadamard_valid,
    transversal_cnot_valid)
from quantum_debugger.algorithms.toric_code import ToricCode


_STEANE_H = np.array([[0, 0, 0, 1, 1, 1, 1],
                      [0, 1, 1, 0, 0, 1, 1],
                      [1, 0, 1, 0, 1, 0, 1]])


class TestCSSCode:
    def test_steane_parameters(self):
        code = CSSCode(_STEANE_H, _STEANE_H)
        assert (code.n, code.num_logical_qubits(), code.distance()) == (7, 1, 3)
        assert code.all_commute()

    def test_logical_operators_anticommute(self):
        code = CSSCode(_STEANE_H, _STEANE_H)
        xl, zl = code.logical_operators()
        assert len(xl) == 1 and len(zl) == 1
        assert int(xl[0] @ zl[0]) % 2 == 1  # Xbar, Zbar anticommute

    def test_422_detection_code(self):
        c = CSSCode(np.array([[1, 1, 1, 1]]), np.array([[1, 1, 1, 1]]))
        assert (c.n, c.num_logical_qubits(), c.distance()) == (4, 2, 2)

    def test_min_weight_decoder(self):
        code = CSSCode(_STEANE_H, _STEANE_H)
        for q in range(7):
            e = np.zeros(7, dtype=np.int8); e[q] = 1
            assert np.array_equal(code.decode_min_weight(e, 1), e)

    def test_css_condition_enforced(self):
        with pytest.raises(ValueError):
            CSSCode(np.array([[1, 1, 0]]), np.array([[0, 1, 1]]))  # Hx Hz^T != 0

    def test_gf2_rank_nullspace(self):
        M = np.array([[1, 1, 0], [0, 1, 1]])
        assert gf2_rank(M) == 2
        for v in gf2_nullspace(M):
            assert not np.any((M @ v) % 2)


class TestHypergraphProduct:
    def test_orthogonality_generic(self):
        code = hypergraph_product(repetition_check_matrix(2), repetition_check_matrix(3))
        assert code.all_commute()

    def test_surface_from_repetition(self):
        code = planar_surface_code(3)
        assert (code.n, code.num_logical_qubits(), code.distance()) == (13, 1, 3)
        assert code.all_commute()

    def test_css_from_classical(self):
        code = css_from_classical(hamming_check_matrix(3))
        assert (code.n, code.num_logical_qubits(), code.distance()) == (7, 1, 3)
        with pytest.raises(ValueError):
            css_from_classical(np.array([[1, 1, 1]]))  # odd weight => H H^T != 0


class TestSurfaceCode:
    def test_parameters(self):
        assert surface_code_parameters(3) == {"n": 13, "k": 1, "d": 3}
        assert surface_code_parameters(5)["n"] == 41

    def test_corrects_weight_one(self):
        assert corrects_all_errors_up_to(planar_surface_code(3), 1)

    def test_d5_structure(self):
        code = planar_surface_code(5)
        assert code.n == 41 and code.num_logical_qubits() == 1 and code.all_commute()


class TestColorCode:
    def test_steane_self_dual(self):
        code = steane_color_code()
        assert (code.n, code.num_logical_qubits(), code.distance()) == (7, 1, 3)
        assert is_self_dual_css(code)

    def test_transversal_gates(self):
        code = steane_color_code()
        assert transversal_hadamard_valid(code)
        assert transversal_cnot_valid(code)

    def test_surface_not_self_dual(self):
        sc = planar_surface_code(3)
        assert not is_self_dual_css(sc)          # no transversal Hadamard
        assert transversal_cnot_valid(sc)        # but CSS => transversal CNOT


class TestToricExtensions:
    def test_parameters(self):
        for L in (3, 4, 5):
            tc = ToricCode(L)
            assert tc.code_parameters() == {"n": 2 * L * L, "k": 2, "d": L}
            assert tc.logicals_valid()

    def test_logical_class(self):
        tc = ToricCode(3)
        lo = tc.logical_operators()
        star_x, star_z = tc.stars[0]
        assert tc.logical_class(star_x, star_z) == "I"       # stabilizer
        assert tc.logical_class(*lo["Z"]) == "Z"             # Zbar is logical Z
        assert tc.logical_class(*lo["X"]) == "X"             # Xbar is logical X

    def test_decode_class_success(self):
        tc = ToricCode(4)
        for q in range(tc.n):
            z = np.zeros(tc.n, dtype=int); z[q] = 1
            assert tc.decode_z_class(z) == "I"   # every weight-1 Z error corrected

    def test_pure_logical_detected(self):
        tc = ToricCode(3)
        zbar = tc.logical_operators()["Z"][1]
        assert tc.decode_z_class(zbar) == "Z"    # syndrome-free logical survives


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
