"""Tests for zero-noise extrapolation (in the algorithms package)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    extrapolate_zero_noise,
    zero_noise_extrapolation,
)
from quantum_debugger.density_matrix import DensityMatrix, depolarizing

_Z = np.diag([1, -1]).astype(complex)
_ZZ = np.kron(_Z, _Z)
_PSI = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)


def _factory():
    return DensityMatrix(state_vector=_PSI)


def _noise_layer(dm, p=0.1):
    for q in (0, 1):
        dm.apply_channel(depolarizing(p), [q])


class TestExtrapolate:
    def test_linear_zero_noise(self):
        # A perfectly linear trend extrapolates exactly.
        scales, values = [1, 2, 3], [0.9, 0.8, 0.7]
        assert abs(extrapolate_zero_noise(scales, values, "linear") - 1.0) < 1e-9

    def test_exponential_geometric_decay(self):
        # Geometric decay r^c extrapolates to 1 at c=0.
        r = 0.8
        scales = [1, 2, 3, 4]
        values = [r**c for c in scales]
        assert abs(extrapolate_zero_noise(scales, values, "exponential") - 1.0) < 1e-9

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            extrapolate_zero_noise([1, 2], [0.9, 0.8], "quadratic")


class TestZNE:
    def test_exponential_recovers_ideal_for_depolarizing(self):
        # Depolarizing makes <ZZ> decay exactly geometrically, so exp fit is exact.
        r = zero_noise_extrapolation(_factory, _noise_layer, _ZZ,
                                     scales=(1, 2, 3), method="exponential",
                                     ideal_state=_PSI)
        assert r["mitigated_error"] < 1e-9
        assert r["improved"]

    def test_linear_improves_over_raw(self):
        r = zero_noise_extrapolation(_factory, _noise_layer, _ZZ,
                                     scales=(1, 2, 3), method="linear",
                                     ideal_state=_PSI)
        assert r["mitigated_error"] < r["raw_error"]

    def test_values_decrease_with_noise(self):
        r = zero_noise_extrapolation(_factory, _noise_layer, _ZZ, scales=(1, 2, 3, 4))
        vals = r["values"]
        assert all(b < a for a, b in zip(vals, vals[1:]))

    def test_raw_is_first_scale(self):
        r = zero_noise_extrapolation(_factory, _noise_layer, _ZZ, scales=(1, 2, 3))
        assert r["raw"] == r["values"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
