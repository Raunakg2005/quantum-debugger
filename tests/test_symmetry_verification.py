"""Tests for symmetry verification error mitigation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    symmetry_project,
    symmetry_verified_expectation,
)
from quantum_debugger.density_matrix import DensityMatrix, bit_flip

_Z = np.diag([1, -1]).astype(complex)
_ZZ = np.kron(_Z, _Z)


def _noisy_bell(p):
    psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)  # |Phi+>, ZZ = +1
    dm = DensityMatrix(state_vector=psi)
    for q in (0, 1):
        dm.apply_channel(bit_flip(p), [q])
    return dm.rho, psi


class TestSymmetryProjection:
    def test_projects_into_sector(self):
        rho, _ = _noisy_bell(0.15)
        ps = symmetry_project(rho, _ZZ, sector=1)
        # After projecting onto ZZ = +1, <ZZ> should be +1.
        assert abs(np.real(np.trace(_ZZ @ ps["rho"])) - 1.0) < 1e-9

    def test_acceptance_in_unit_interval(self):
        rho, _ = _noisy_bell(0.2)
        acc = symmetry_project(rho, _ZZ, sector=1)["acceptance"]
        assert 0 <= acc <= 1

    def test_result_is_density_matrix(self):
        rho, _ = _noisy_bell(0.2)
        r = symmetry_project(rho, _ZZ, 1)["rho"]
        assert abs(np.trace(r).real - 1.0) < 1e-9
        assert np.linalg.eigvalsh(r).min() > -1e-9


class TestVerification:
    def test_improves_fidelity(self):
        rho, psi = _noisy_bell(0.15)
        fidelity_obs = np.outer(psi, psi.conj())  # |Phi+><Phi+|
        r = symmetry_verified_expectation(rho, _ZZ, fidelity_obs, sector=1, ideal_state=psi)
        assert r["improved"]
        assert r["verified_error"] < r["raw_error"]

    def test_perfect_state_unchanged(self):
        psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        r = symmetry_verified_expectation(rho, _ZZ, _ZZ, sector=1, ideal_state=psi)
        assert abs(r["acceptance"] - 1.0) < 1e-9  # nothing rejected
        assert abs(r["verified"] - r["raw"]) < 1e-9

    def test_report_fields(self):
        rho, psi = _noisy_bell(0.1)
        r = symmetry_verified_expectation(rho, _ZZ, np.outer(psi, psi.conj()),
                                          sector=1, ideal_state=psi)
        assert set(r) >= {"raw", "verified", "acceptance", "ideal",
                          "raw_error", "verified_error", "improved"}

    def test_wrong_sector_rejects_most(self):
        # Projecting a mostly-even state onto the odd sector keeps little.
        rho, _ = _noisy_bell(0.1)
        acc_even = symmetry_project(rho, _ZZ, sector=1)["acceptance"]
        acc_odd = symmetry_project(rho, _ZZ, sector=-1)["acceptance"]
        assert acc_even > acc_odd


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
