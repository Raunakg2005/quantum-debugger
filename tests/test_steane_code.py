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
        assert r["syndrome"][:3] == (0, 0, 0)      # X-type unaffected by X error
        assert r["syndrome"][3:] != (0, 0, 0)      # Z-type detect it
        assert r["correction"] == "X0"

    def test_css_z_error_only_trips_x_stabilizers(self):
        r = steane_code(1.0, 0.0, error="Z6")
        assert r["syndrome"][3:] == (0, 0, 0)      # Z-type unaffected by Z error
        assert r["syndrome"][:3] != (0, 0, 0)      # X-type detect it

    def test_invalid_error_rejected(self):
        with pytest.raises(ValueError):
            steane_code(1.0, 0.0, error="Z7")

    def test_stabilizers_shape(self):
        stabs = steane_stabilizers()
        assert len(stabs) == 6 and all(len(s) == 7 for s in stabs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
