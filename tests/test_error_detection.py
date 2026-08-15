"""Tests for the [[4,2,2]] error-detecting code."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    four_two_two_codewords,
    detect_single_errors,
    postselected_memory,
)
from quantum_debugger.stabilizer import stabilizer_to_pauli_matrix as pauli


class TestCodewords:
    def test_orthonormal(self):
        cw = four_two_two_codewords()
        keys = list(cw)
        for i, a in enumerate(keys):
            for j, b in enumerate(keys):
                expected = 1.0 if i == j else 0.0
                assert abs(abs(np.vdot(cw[a], cw[b])) - expected) < 1e-12

    def test_stabilized(self):
        cw = four_two_two_codewords()
        for sv in cw.values():
            for s in ("XXXX", "ZZZZ"):
                ev = np.real(np.vdot(sv, pauli(1, s) @ sv))
                assert abs(ev - 1.0) < 1e-9

    def test_zero_zero_is_ghz_like(self):
        sv = four_two_two_codewords()["00"]
        expected = np.zeros(16, dtype=complex)
        expected[0] = expected[15] = 1 / np.sqrt(2)
        assert abs(abs(np.vdot(sv, expected)) - 1.0) < 1e-9


class TestDetection:
    def test_every_single_error_detected(self):
        r = detect_single_errors()
        assert r["all_detected"]
        assert r["detected"] == r["total"] == 12


class TestPostselectedMemory:
    def test_quadratic_suppression(self):
        e1 = 1 - postselected_memory(0.002)["postselected_fidelity"]
        e2 = 1 - postselected_memory(0.004)["postselected_fidelity"]
        assert 3.5 < e2 / e1 < 4.5

    @pytest.mark.parametrize("p", [0.005, 0.02])
    def test_beats_bare_qubit(self, p):
        r = postselected_memory(p)
        assert (1 - r["postselected_fidelity"]) < (1 - r["unencoded_fidelity"]) / 10

    def test_acceptance_cost(self):
        # Detection is not free: acceptance drops linearly with p.
        r = postselected_memory(0.02)
        assert 0.9 < r["acceptance_probability"] < 1.0

    def test_perfect_channel(self):
        r = postselected_memory(0.0)
        assert abs(r["postselected_fidelity"] - 1.0) < 1e-12
        assert abs(r["acceptance_probability"] - 1.0) < 1e-12

    @pytest.mark.parametrize("logical", ["01", "10", "11"])
    def test_all_logical_states_protected(self, logical):
        r = postselected_memory(0.01, logical=logical)
        assert r["postselected_fidelity"] > 0.999

    def test_invalid_logical_rejected(self):
        with pytest.raises(ValueError):
            postselected_memory(0.01, logical="2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
