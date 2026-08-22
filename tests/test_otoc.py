"""Tests for out-of-time-order correlators (scrambling)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    otoc,
    scrambling_time,
    hamiltonian_matrix,
    tfim_hamiltonian,
)
from quantum_debugger.algorithms.otoc import _embed, _X, _Z


def _tfim(n):
    return hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 1.0), n)


class TestOTOCProperties:
    def test_commutes_at_t0_for_separated_ops(self):
        n = 4
        H = _tfim(n)
        r = otoc(H, _embed(_X, 0, n), _embed(_X, n - 1, n), [0.0])
        assert abs(r["C"][0]) < 1e-9

    def test_anticommuting_same_site_gives_four(self):
        # C(0) = <|[X, Z]|^2> = |2iY|^2 averaged = 4.
        n = 3
        H = _tfim(n)
        r = otoc(H, _embed(_X, 0, n), _embed(_Z, 0, n), [0.0])
        assert abs(r["C"][0] - 4.0) < 1e-9

    def test_identity_C_equals_2_minus_2ReF(self):
        n = 4
        H = _tfim(n)
        r = otoc(H, _embed(_X, 0, n), _embed(_X, n - 1, n), np.linspace(0, 4, 15))
        assert r["identity_ok"]

    def test_commutator_nonnegative(self):
        n = 4
        H = _tfim(n)
        r = otoc(H, _embed(_X, 0, n), _embed(_X, n - 1, n), np.linspace(0, 6, 30))
        assert np.all(r["C"] >= -1e-12)

    def test_F_starts_at_one(self):
        n = 4
        H = _tfim(n)
        r = otoc(H, _embed(_X, 0, n), _embed(_X, n - 1, n), [0.0])
        assert abs(r["F"][0] - 1.0) < 1e-9


class TestScrambling:
    def test_commutator_grows_from_zero(self):
        n = 4
        r = scrambling_time(_tfim(n), n, t_max=6.0)
        assert r["C"][0] < 1e-9
        assert r["max_C"] > 1.0  # information reaches the far edge

    def test_scrambling_time_detected(self):
        n = 4
        r = scrambling_time(_tfim(n), n, t_max=8.0, threshold=0.5)
        assert r["scrambling_time"] is not None
        assert r["scrambling_time"] > 0

    def test_edge_operator_lags_near_neighbor(self):
        # The far qubit scrambles later than an adjacent one (locality / light cone).
        n = 5
        H = _tfim(n)
        times = np.linspace(0, 3, 60)
        c_near = otoc(H, _embed(_X, 0, n), _embed(_X, 1, n), times)["C"]
        c_far = otoc(H, _embed(_X, 0, n), _embed(_X, n - 1, n), times)["C"]
        # early on, the near commutator is larger than the far one
        assert c_near[10] > c_far[10]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
