"""Tests for the 5-qubit perfect code [[5,1,3]]."""

import numpy as np
import pytest

from quantum_debugger.algorithms import five_qubit_code, five_qubit_stabilizers

_ALL_ERRORS = ["I"] + [f"{p}{q}" for q in range(5) for p in "XYZ"]


class TestFiveQubitCode:
    @pytest.mark.parametrize("error", _ALL_ERRORS)
    def test_corrects_every_single_qubit_error_logical_zero(self, error):
        r = five_qubit_code(1.0, 0.0, error=error)
        assert abs(r["fidelity"] - 1.0) < 1e-9

    @pytest.mark.parametrize("error", _ALL_ERRORS)
    def test_corrects_every_single_qubit_error_superposition(self, error):
        # An arbitrary logical state must be recovered, not just basis codewords.
        r = five_qubit_code(0.6, 0.8j, error=error)
        assert abs(r["fidelity"] - 1.0) < 1e-9

    def test_all_syndromes_distinct(self):
        seen = {}
        for error in _ALL_ERRORS:
            syn = five_qubit_code(1.0, 0.0, error=error)["syndrome"]
            seen[syn] = error
        assert (
            len(seen) == 16
        )  # 1 + 15 single-qubit errors, all distinct (perfect code)

    def test_no_error_has_trivial_syndrome(self):
        r = five_qubit_code(1.0, 0.0, error="I")
        assert r["syndrome"] == (0, 0, 0, 0)
        assert r["correction"] == "I"

    def test_specific_error_decoded(self):
        r = five_qubit_code(1.0, 0.0, error="X2")
        assert r["correction"] == "X2"
        assert r["fidelity"] == pytest.approx(1.0, abs=1e-9)

    def test_invalid_error_rejected(self):
        with pytest.raises(ValueError):
            five_qubit_code(1.0, 0.0, error="X5")

    def test_stabilizers_shape(self):
        stabs = five_qubit_stabilizers()
        assert len(stabs) == 4 and all(len(s) == 5 for s in stabs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
