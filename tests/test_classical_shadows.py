"""Tests for classical shadows."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    collect_shadows,
    estimate_observable,
    shadow_estimates,
)


def _bell():
    return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)


class TestUnbiasedEstimates:
    def test_bell_correlators(self):
        r = shadow_estimates(_bell(), ["XX", "YY", "ZZ", "ZI"], shots=4000, seed=1)
        # Bell |Phi+>: <XX>=1, <YY>=-1, <ZZ>=1, <ZI>=0.
        assert abs(r["estimates"]["XX"] - 1.0) < 0.15
        assert abs(r["estimates"]["YY"] + 1.0) < 0.15
        assert abs(r["estimates"]["ZZ"] - 1.0) < 0.15
        assert abs(r["estimates"]["ZI"]) < 0.15

    def test_many_observables_one_dataset(self):
        # All observables estimated from the SAME measurements.
        obs = ["XX", "YY", "ZZ", "XI", "IZ"]
        r = shadow_estimates(_bell(), obs, shots=4000, seed=2)
        assert set(r["estimates"]) == set(obs)
        assert r["max_error"] < 0.2

    def test_true_values_reported(self):
        r = shadow_estimates(_bell(), ["ZZ"], shots=500, seed=0)
        assert abs(r["true_values"]["ZZ"] - 1.0) < 1e-12

    def test_converges_with_more_shots(self):
        errs = [
            shadow_estimates(_bell(), ["XX", "YY", "ZZ"], shots=s, seed=3)["max_error"]
            for s in (200, 1000, 5000)
        ]
        assert errs[-1] < errs[0]  # more shots -> smaller error


class TestSingleQubit:
    def test_plus_state(self):
        # |+>: <X>=1, <Y>=0, <Z>=0.
        r = shadow_estimates(
            np.array([1, 1], dtype=complex) / np.sqrt(2),
            ["X", "Y", "Z"],
            shots=4000,
            seed=5,
        )
        assert abs(r["estimates"]["X"] - 1.0) < 0.15
        assert abs(r["estimates"]["Y"]) < 0.15
        assert abs(r["estimates"]["Z"]) < 0.15


class TestReuse:
    def test_shadows_reusable_across_observables(self):
        shadows = collect_shadows(_bell(), shots=3000, seed=7)
        assert abs(estimate_observable(shadows, "XX") - 1.0) < 0.2
        assert abs(estimate_observable(shadows, "ZZ") - 1.0) < 0.2

    def test_identity_observable_is_one(self):
        shadows = collect_shadows(_bell(), shots=500, seed=0)
        # <II> = Tr(rho) = 1, estimated exactly per snapshot (Tr of the snapshot).
        assert abs(estimate_observable(shadows, "II") - 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
