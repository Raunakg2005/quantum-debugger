"""Tests for Clifford Data Regression (CDR)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import fit_cdr_model, apply_cdr, cdr_mitigate
from quantum_debugger.density_matrix import DensityMatrix, depolarizing

_Z = np.diag([1, -1]).astype(complex)
_ZZ = np.kron(_Z, _Z)


def _noisy(psi, p=0.15):
    dm = DensityMatrix(state_vector=psi)
    for q in (0, 1):
        dm.apply_channel(depolarizing(p), [q])
    return float(np.real(np.trace(_ZZ @ dm.rho)))


def _ideal(psi):
    return float(np.real(psi.conj() @ _ZZ @ psi))


def _training(seed, n=30):
    rng = np.random.default_rng(seed)
    states = []
    for _ in range(n):
        v = rng.normal(size=4) + 1j * rng.normal(size=4)
        states.append(v / np.linalg.norm(v))
    return states


class TestFitModel:
    def test_recovers_linear_relation(self):
        # ideal = 2*noisy - 0.5 exactly.
        x = np.linspace(-1, 1, 20)
        y = 2 * x - 0.5
        m = fit_cdr_model(x, y)
        assert abs(m["slope"] - 2.0) < 1e-9
        assert abs(m["intercept"] + 0.5) < 1e-9
        assert abs(m["r_squared"] - 1.0) < 1e-9

    def test_apply_model(self):
        m = {"slope": 1.4, "intercept": 0.1}
        assert abs(apply_cdr(m, 0.5) - 0.8) < 1e-9

    def test_depolarizing_is_rescaling(self):
        # Global depolarizing -> ideal = slope * noisy, intercept ~ 0.
        states = _training(0)
        m = fit_cdr_model([_noisy(s) for s in states], [_ideal(s) for s in states])
        assert m["slope"] > 1.0
        assert abs(m["intercept"]) < 1e-6
        assert m["r_squared"] > 0.999


class TestCDRMitigate:
    def test_corrects_target(self):
        psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)  # Bell
        r = cdr_mitigate(_noisy, _ideal, _training(1), psi)
        assert r["improved"]
        assert r["mitigated_error"] < 1e-6
        assert r["raw_error"] > 0.1

    def test_reports_model(self):
        psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        r = cdr_mitigate(_noisy, _ideal, _training(2), psi)
        assert "slope" in r["model"] and "r_squared" in r["model"]

    def test_explicit_ideal_target(self):
        psi = np.array([0, 1, 1, 0], dtype=complex) / np.sqrt(2)  # |Psi+>, <ZZ> = -1
        r = cdr_mitigate(_noisy, _ideal, _training(3), psi, ideal_target=-1.0)
        assert abs(r["ideal"] + 1.0) < 1e-12
        assert r["mitigated_error"] < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
