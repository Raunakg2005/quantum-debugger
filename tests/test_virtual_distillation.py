"""Tests for virtual distillation error mitigation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import virtual_distillation, distillation_report
from quantum_debugger.density_matrix import DensityMatrix, depolarizing

_Z = np.diag([1, -1]).astype(complex)
_ZZ = np.kron(_Z, _Z)


def _noisy_bell(p):
    psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    dm = DensityMatrix(state_vector=psi)
    for q in (0, 1):
        dm.apply_channel(depolarizing(p), [q])
    return dm.rho, psi


class TestVirtualDistillation:
    def test_reduces_error(self):
        rho, psi = _noisy_bell(0.2)
        r = distillation_report(rho, _ZZ, ideal_state=psi, m=2)
        assert r["improved"]
        assert r["distilled_error"] < r["raw_error"]

    def test_higher_order_better(self):
        rho, psi = _noisy_bell(0.2)
        ideal = 1.0
        e2 = abs(virtual_distillation(rho, _ZZ, m=2) - ideal)
        e3 = abs(virtual_distillation(rho, _ZZ, m=3) - ideal)
        assert e3 < e2

    def test_m1_is_raw_expectation(self):
        rho, _ = _noisy_bell(0.2)
        assert abs(virtual_distillation(rho, _ZZ, m=1) - np.real(np.trace(_ZZ @ rho))) < 1e-12

    def test_pure_state_unchanged(self):
        # For a pure state rho = rho^m, so distillation changes nothing.
        psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        assert abs(virtual_distillation(rho, _ZZ, m=3) - 1.0) < 1e-9

    def test_report_fields(self):
        rho, psi = _noisy_bell(0.15)
        r = distillation_report(rho, _ZZ, ideal_state=psi, m=2)
        assert set(r) >= {"raw", "distilled", "ideal", "raw_error", "distilled_error", "improved"}
        assert abs(r["ideal"] - 1.0) < 1e-9

    def test_converges_to_dominant_eigenvector(self):
        # As m -> infinity, <O>_m -> <O> in the largest eigenvector of rho.
        rho, _ = _noisy_bell(0.3)
        w, v = np.linalg.eigh(rho)
        top = v[:, -1]
        limit = np.real(top.conj() @ _ZZ @ top)
        assert abs(virtual_distillation(rho, _ZZ, m=20) - limit) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
