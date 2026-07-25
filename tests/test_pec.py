"""Tests for probabilistic error cancellation (PEC)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    invert_pauli_channel,
    depolarizing_coeffs,
    apply_pauli_channel,
    pec_mitigate,
)

_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class TestChannelInversion:
    @pytest.mark.parametrize("p", [0.05, 0.1, 0.2, 0.3])
    def test_inverse_cancels_noise(self, p):
        a = depolarizing_coeffs(p)
        b = invert_pauli_channel(a)["quasi_probabilities"]
        rng = np.random.default_rng(int(p * 100))
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        psi = psi / np.linalg.norm(psi)
        rho = np.outer(psi, psi.conj())
        noisy = apply_pauli_channel(rho, a)
        recovered = apply_pauli_channel(noisy, b)
        assert np.allclose(recovered, rho, atol=1e-9)

    def test_quasi_probabilities_sum_to_one(self):
        b = invert_pauli_channel(depolarizing_coeffs(0.2))["quasi_probabilities"]
        assert abs(b.sum() - 1.0) < 1e-9

    def test_overhead_at_least_one(self):
        for p in (0.05, 0.2, 0.4):
            assert invert_pauli_channel(depolarizing_coeffs(p))["overhead"] >= 1 - 1e-12

    def test_overhead_grows_with_noise(self):
        g_low = invert_pauli_channel(depolarizing_coeffs(0.05))["overhead"]
        g_high = invert_pauli_channel(depolarizing_coeffs(0.3))["overhead"]
        assert g_high > g_low

    def test_no_noise_is_identity_inverse(self):
        b = invert_pauli_channel(depolarizing_coeffs(0.0))["quasi_probabilities"]
        assert np.allclose(b, [1, 0, 0, 0], atol=1e-9)


class TestPECMitigation:
    def test_recovers_ideal_expectation(self):
        p = 0.2
        psi = np.array([0.6, 0.8j], dtype=complex)
        rho = np.outer(psi, psi.conj())
        noisy = apply_pauli_channel(rho, depolarizing_coeffs(p))
        r = pec_mitigate(noisy, depolarizing_coeffs(p), _Z, ideal_state=psi)
        assert r["improved"]
        assert r["mitigated_error"] < 1e-9         # exact cancellation
        assert r["raw_error"] > 1e-3               # noise mattered

    def test_reports_overhead(self):
        psi = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        noisy = apply_pauli_channel(rho, depolarizing_coeffs(0.15))
        r = pec_mitigate(noisy, depolarizing_coeffs(0.15), _Z, ideal_state=psi)
        assert r["overhead"] > 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
