"""Tests for weak values (Aharonov-Albert-Vaidman)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    weak_value,
    weak_measurement_shift,
    weak_value_demo,
)

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class TestWeakValue:
    def test_equals_eigenvalue_when_preselect_is_eigenstate(self):
        # If pre = post = eigenstate, the weak value is the eigenvalue.
        assert abs(weak_value(_Z, [1, 0], [1, 0]) - 1.0) < 1e-12
        assert abs(weak_value(_Z, [0, 1], [0, 1]) + 1.0) < 1e-12

    def test_expectation_when_pre_equals_post(self):
        pre = np.array([np.cos(0.3), np.sin(0.3)], dtype=complex)
        aw = weak_value(_Z, pre, pre)
        assert abs(aw.imag) < 1e-12
        assert abs(aw.real - np.real(pre.conj() @ _Z @ pre)) < 1e-12

    def test_orthogonal_selection_rejected(self):
        with pytest.raises(ValueError):
            weak_value(_Z, [1, 0], [0, 1])

    def test_amplification_outside_spectrum(self):
        # Z has eigenvalues +/-1, but A_w can be ~ -20.
        pre = np.array([1, 1], dtype=complex) / np.sqrt(2)
        post = np.array([np.cos(np.pi / 4 + 0.05), -np.sin(np.pi / 4 + 0.05)], dtype=complex)
        aw = weak_value(_Z, pre, post)
        assert abs(aw.real) > 15

    def test_can_be_complex(self):
        pre = np.array([1, 0], dtype=complex)
        post = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        aw = weak_value(_X, pre, post)
        assert abs(aw.imag) > 1e-6


class TestWeakMeasurement:
    @pytest.mark.parametrize("eps", [0.5, 0.2, 0.05])
    def test_pointer_shift_converges_to_real_weak_value(self, eps):
        pre = np.array([1, 1], dtype=complex) / np.sqrt(2)
        post = np.array([np.cos(np.pi / 4 + eps), -np.sin(np.pi / 4 + eps)], dtype=complex)
        aw = weak_value(_Z, pre, post)
        shift = weak_measurement_shift(_Z, pre, post, 1e-3) / 1e-3
        assert abs(shift - aw.real) < 1e-2

    def test_demo_flags_amplification(self):
        pre = np.array([1, 1], dtype=complex) / np.sqrt(2)
        post = np.array([np.cos(np.pi / 4 + 0.05), -np.sin(np.pi / 4 + 0.05)], dtype=complex)
        r = weak_value_demo(_Z, pre, post)
        assert r["outside_spectrum"]
        assert r["matches"]

    def test_strong_coupling_stays_within_spectrum(self):
        # A projective (strong) measurement can only ever read an eigenvalue.
        pre = np.array([1, 1], dtype=complex) / np.sqrt(2)
        r = weak_value_demo(_Z, pre, pre)
        assert not r["outside_spectrum"]  # pre = post: A_w = <Z> in [-1, 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
