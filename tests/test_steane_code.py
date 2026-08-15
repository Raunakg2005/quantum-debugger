"""Tests for the Steane 7-qubit code [[7,1,3]]."""

import numpy as np
import pytest

from quantum_debugger.algorithms import steane_code, steane_stabilizers

_ALL_ERRORS = ["I"] + [f"{p}{q}" for q in range(7) for p in "XYZ"]


class TestSteaneCode:
    @pytest.mark.parametrize("error", _ALL_ERRORS)
    def test_corrects_every_error_logical_zero(self, error):
        assert abs(steane_code(1.0, 0.0, error=error)["fidelity"] - 1.0) < 1e-9

    @pytest.mark.parametrize("error", _ALL_ERRORS)
    def test_corrects_every_error_superposition(self, error):
        assert abs(steane_code(0.6, 0.8j, error=error)["fidelity"] - 1.0) < 1e-9

    def test_all_syndromes_distinct(self):
        seen = {steane_code(1.0, 0.0, error=e)["syndrome"] for e in _ALL_ERRORS}
        assert len(seen) == 22  # 1 + 21 single-qubit errors, all distinct

    def test_no_error_trivial_syndrome(self):
        r = steane_code(1.0, 0.0, error="I")
        assert r["syndrome"] == (0, 0, 0, 0, 0, 0)
        assert r["correction"] == "I"

    def test_css_x_error_only_trips_z_stabilizers(self):
        # X-type stabilizers are the first three; a pure X error leaves them +1.
        r = steane_code(1.0, 0.0, error="X0")
        assert r["syndrome"][:3] == (0, 0, 0)  # X-type unaffected by X error
        assert r["syndrome"][3:] != (0, 0, 0)  # Z-type detect it
        assert r["correction"] == "X0"

    def test_css_z_error_only_trips_x_stabilizers(self):
        r = steane_code(1.0, 0.0, error="Z6")
        assert r["syndrome"][3:] == (0, 0, 0)  # Z-type unaffected by Z error
        assert r["syndrome"][:3] != (0, 0, 0)  # X-type detect it

    def test_invalid_error_rejected(self):
        with pytest.raises(ValueError):
            steane_code(1.0, 0.0, error="Z7")

    def test_stabilizers_shape(self):
        stabs = steane_stabilizers()
        assert len(stabs) == 6 and all(len(s) == 7 for s in stabs)


class TestTransversalGates:
    @pytest.mark.parametrize(
        "gate,expected",
        [
            ("X", "X"),
            ("Z", "Z"),
            ("H", "H"),
            ("S", "Sdg"),
            ("Sdg", "S"),
        ],
    )
    def test_logical_action(self, gate, expected):
        from quantum_debugger.algorithms import steane_transversal

        r = steane_transversal(gate, 0.6, 0.8j)
        assert r["logical_action"] == expected
        assert abs(r["fidelity"] - 1.0) < 1e-9

    def test_transversal_s_is_not_logical_s(self):
        # On |+_L>, logical S and logical S-dagger give different states; the
        # transversal S must match S-dagger, NOT S.
        import numpy as np
        from quantum_debugger.algorithms.steane_code import (
            _encode,
            _S_GATE,
            apply_gate_tensor,
            _N,
        )

        acted = _encode(1.0, 1.0)
        for q in range(_N):
            acted = apply_gate_tensor(np, acted, _S_GATE, [q], _N)
        ideal_s = _encode(1.0, 1j)  # logical S on |+_L>
        ideal_sdg = _encode(1.0, -1j)  # logical S-dagger on |+_L>
        assert abs(np.vdot(ideal_sdg, acted)) ** 2 > 1 - 1e-9
        assert abs(np.vdot(ideal_s, acted)) ** 2 < 0.6

    def test_invalid_gate_rejected(self):
        from quantum_debugger.algorithms import steane_transversal

        with pytest.raises(ValueError):
            steane_transversal("T")


class TestTransversalCNOT:
    @pytest.mark.parametrize(
        "ctrl,tgt",
        [
            ((1, 0), (1, 0)),
            ((0, 1), (1, 0)),
            ((1, 0), (0, 1)),
            ((0, 1), (0, 1)),
        ],
    )
    def test_logical_basis(self, ctrl, tgt):
        from quantum_debugger.algorithms import steane_transversal_cnot

        assert abs(steane_transversal_cnot(ctrl, tgt)["fidelity"] - 1.0) < 1e-9

    def test_superposition_control_entangles(self):
        # (|0>+|1>)_A |0>_B -> encoded logical Bell state, exactly.
        from quantum_debugger.algorithms import steane_transversal_cnot

        r = steane_transversal_cnot((1.0, 1.0), (1.0, 0.0))
        assert abs(r["fidelity"] - 1.0) < 1e-9

    def test_random_logical_inputs(self):
        import numpy as np
        from quantum_debugger.algorithms import steane_transversal_cnot

        rng = np.random.default_rng(5)
        for _ in range(3):
            ctrl = tuple(rng.normal(size=2) + 1j * rng.normal(size=2))
            tgt = tuple(rng.normal(size=2) + 1j * rng.normal(size=2))
            assert abs(steane_transversal_cnot(ctrl, tgt)["fidelity"] - 1.0) < 1e-9


class TestSteaneUnderContinuousNoise:
    def test_perfect_channel_is_lossless(self):
        from quantum_debugger.algorithms import steane_code_noisy

        assert abs(steane_code_noisy(0.0)["corrected"] - 1.0) < 1e-9

    def test_quadratic_error_suppression(self):
        # Distance 3: doubling p quadruples the logical error (small p).
        from quantum_debugger.algorithms import steane_code_noisy

        e1 = 1 - steane_code_noisy(0.002)["corrected"]
        e2 = 1 - steane_code_noisy(0.004)["corrected"]
        assert 3.5 < e2 / e1 < 4.5

    @pytest.mark.parametrize("p", [0.01, 0.05])
    def test_exceeds_weight1_floor(self, p):
        from quantum_debugger.algorithms import steane_code_noisy

        r = steane_code_noisy(p)
        assert r["corrected"] >= r["weight1_bound"] - 1e-9

    def test_beats_bare_qubit_below_pseudothreshold(self):
        from quantum_debugger.algorithms import steane_code_noisy

        r = steane_code_noisy(0.01)
        assert (1 - r["corrected"]) < (1 - r["uncorrected"]) / 4  # ~5x better

    def test_worse_above_pseudothreshold(self):
        from quantum_debugger.algorithms import steane_code_noisy

        r = steane_code_noisy(0.25)
        assert (1 - r["corrected"]) > (1 - r["uncorrected"])

    def test_superposition_codeword_protected(self):
        from quantum_debugger.algorithms import steane_code_noisy

        r = steane_code_noisy(0.05, alpha=1.0, beta=1j)
        assert r["corrected"] >= r["weight1_bound"] - 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
