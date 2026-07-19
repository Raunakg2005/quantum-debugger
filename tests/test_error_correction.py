"""Tests for quantum error-correcting codes."""

import pytest

from quantum_debugger.algorithms import bit_flip_code, phase_flip_code, shor_code


class TestBitFlipCode:
    @pytest.mark.parametrize("error_qubit", [None, 0, 1, 2])
    def test_corrects_x_error(self, error_qubit):
        r = bit_flip_code(0.6, 0.8, error_qubit=error_qubit, seed=1)
        assert r["fidelity"] > 0.999

    def test_syndrome_locates_error(self):
        assert bit_flip_code(1, 0, error_qubit=0)["syndrome"] == (1, 0)
        assert bit_flip_code(1, 0, error_qubit=1)["syndrome"] == (1, 1)
        assert bit_flip_code(1, 0, error_qubit=2)["syndrome"] == (0, 1)
        assert bit_flip_code(1, 0, error_qubit=None)["syndrome"] == (0, 0)

    def test_no_error_not_detected(self):
        assert bit_flip_code(0.6, 0.8, error_qubit=None)["error_detected"] is False


class TestPhaseFlipCode:
    @pytest.mark.parametrize("error_qubit", [None, 0, 1, 2])
    def test_corrects_z_error(self, error_qubit):
        r = phase_flip_code(0.6, 0.8, error_qubit=error_qubit, seed=1)
        assert r["fidelity"] > 0.999


class TestShorCode:
    @pytest.mark.parametrize("error_type", [None, "X", "Y", "Z"])
    @pytest.mark.parametrize("error_qubit", [0, 4, 8])
    def test_corrects_arbitrary_error(self, error_type, error_qubit):
        r = shor_code(0.6, 0.8, error_qubit=error_qubit, error_type=error_type, seed=1)
        assert r["fidelity"] > 0.999

    def test_superposition_preserved(self):
        # An equal superposition must survive an X error intact.
        r = shor_code(1, 1, error_qubit=2, error_type="X", seed=3)
        assert r["fidelity"] > 0.999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
