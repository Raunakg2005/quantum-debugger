"""
Tests for the 1.6.0 fault-tolerance suite: magic-state distillation, code
concatenation, transversal gates (and the Eastin-Knill obstruction), gate
teleportation / T-injection, and Clifford+T synthesis. Verified against closed forms
and by logical-action checks on real code words.
"""

import numpy as np
import pytest
from scipy.stats import unitary_group

from quantum_debugger.algorithms.magic_states import (
    t_state, stabilizer_fidelity, distillation_15to1_error, distillation_threshold,
    distillation_rounds_to_target)
from quantum_debugger.algorithms.concatenation import (
    concatenated_logical_error, pseudothreshold, levels_for_target, qubit_overhead,
    double_exponential_check)
from quantum_debugger.algorithms.transversal_gates import (
    steane_codewords, steane_transversal_hadamard_is_logical_h,
    steane_transversal_s_is_logical_phase, eastin_knill_obstruction, transversal_gate,
    preserves_code_space)
from quantum_debugger.algorithms.gate_teleportation import gate_teleportation, t_injection
from quantum_debugger.algorithms.clifford_t_synthesis import (
    synthesize, synthesize_rz, enumerate_clifford_t, is_clifford_t_word, t_count)

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_S = np.diag([1, 1j]).astype(complex)
_T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)


class TestMagicStates:
    def test_stabilizer_fidelity(self):
        assert abs(stabilizer_fidelity(t_state()) - np.cos(np.pi / 8) ** 2) < 1e-9
        assert abs(stabilizer_fidelity([1, 0]) - 1) < 1e-9

    def test_cubic_suppression(self):
        p = 0.01
        assert abs(distillation_15to1_error(p) - 35 * p**3) < 1e-15
        assert distillation_15to1_error(p) < p                      # below threshold
        assert abs(distillation_threshold() - 1 / np.sqrt(35)) < 1e-9

    def test_rounds(self):
        assert distillation_rounds_to_target(0.01, 1e-12) == 3
        assert distillation_rounds_to_target(0.3, 1e-12) == -1       # above threshold


class TestConcatenation:
    def test_double_exponential(self):
        assert double_exponential_check(0.01, 3, A=1.0)
        assert double_exponential_check(0.05, 4, A=2.0)

    def test_threshold_and_levels(self):
        assert abs(pseudothreshold(1.0) - 1.0) < 1e-12
        assert levels_for_target(0.01, 1e-15) == 3
        assert levels_for_target(1.5, 1e-9) == -1                    # above threshold

    def test_overhead(self):
        assert qubit_overhead(3, 7) == 343


class TestTransversalGates:
    def test_codewords(self):
        v0, v1 = steane_codewords()
        assert abs(np.vdot(v0, v0) - 1) < 1e-9 and abs(np.vdot(v0, v1)) < 1e-9

    def test_transversal_clifford(self):
        assert steane_transversal_hadamard_is_logical_h()
        assert steane_transversal_s_is_logical_phase()

    def test_eastin_knill(self):
        assert eastin_knill_obstruction()                            # T not transversal
        assert not preserves_code_space(transversal_gate("T", 7))


class TestGateTeleportation:
    def test_clifford_gates(self):
        rng = np.random.default_rng(3)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        for U in (_H, _S, _X, _H @ _S):
            assert gate_teleportation(U, psi)

    def test_t_not_pauli_correctable(self):
        rng = np.random.default_rng(4)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        assert not gate_teleportation(_T, psi)      # non-Clifford: no Pauli correction
        assert t_injection(psi)                      # but magic-state injection works


class TestCliffordTSynthesis:
    def test_exact_pi4_multiples(self):
        assert synthesize_rz(np.pi / 4, 6)["error"] < 1e-9
        assert synthesize_rz(np.pi / 2, 6)["error"] < 1e-9

    def test_reachable_exact(self):
        target = list(enumerate_clifford_t(5).values())[20][1]
        assert synthesize(target, 5)["error"] < 1e-6

    def test_net_grows(self):
        sizes = [len(enumerate_clifford_t(L)) for L in (2, 4, 6)]
        assert sizes[0] < sizes[1] < sizes[2]

    def test_word_is_clifford_t(self):
        assert is_clifford_t_word(synthesize_rz(np.pi / 4, 4)["word"])
        assert t_count("HTHTT") == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
