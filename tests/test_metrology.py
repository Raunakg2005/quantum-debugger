"""Tests for quantum metrology (GHZ Heisenberg-limited phase sensing)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    phase_sensitivity,
    parity_signal,
    quantum_fisher_information,
)
from quantum_debugger.algorithms.metrology import product_probe
from quantum_debugger.algorithms import ghz_state


class TestQFI:
    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
    def test_ghz_is_heisenberg(self, n):
        qfi = quantum_fisher_information(ghz_state(n).astype(complex), n)
        assert np.isclose(qfi, n**2)

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
    def test_product_is_sql(self, n):
        qfi = quantum_fisher_information(product_probe(n), n)
        assert np.isclose(qfi, n)


class TestPhaseSensitivity:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_advantage_is_n(self, n):
        r = phase_sensitivity(n)
        assert np.isclose(r["advantage"], n)
        assert np.isclose(r["delta_phi_ghz"], 1 / n)
        assert np.isclose(r["delta_phi_product"], 1 / np.sqrt(n))


class TestParitySignal:
    def test_oscillates_as_cos_n_phi(self):
        n = 4
        for phi in np.linspace(0, np.pi, 7):
            assert np.isclose(parity_signal(n, phi), np.cos(n * phi), atol=1e-9)

    def test_faster_than_single_qubit(self):
        # GHZ parity completes a full period in phi = 2pi/n.
        n = 3
        assert np.isclose(parity_signal(n, 2 * np.pi / n), 1.0, atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestMixedStateQFI:
    def test_pure_state_is_four_var(self):
        from quantum_debugger.algorithms import qfi_mixed

        psi = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        Z_half = np.diag([0.5, -0.5]).astype(complex)
        var = 0.25  # Var(Z/2) on the equator
        assert abs(qfi_mixed(rho, Z_half) - 4 * var) < 1e-9

    def test_ghz_reaches_heisenberg_limit(self):
        from quantum_debugger.algorithms import qfi_mixed, ghz_state

        n = 3
        ghz = ghz_state(n).astype(complex)
        J = np.zeros((2**n, 2**n), dtype=complex)
        for q in range(n):
            zq = np.array([[1.0]])
            for k in range(n):
                zq = np.kron(np.diag([1.0, -1.0]) if k == q else np.eye(2), zq)
            J += zq / 2
        assert abs(qfi_mixed(np.outer(ghz, ghz.conj()), J) - n**2) < 1e-9

    @pytest.mark.parametrize("seed", range(4))
    def test_matches_bures_fidelity_derivative(self, seed):
        # Independent check: F_Q = 8 (1 - sqrt(F(rho, rho_dphi))) / dphi^2.
        from scipy.linalg import expm
        from quantum_debugger.algorithms import qfi_mixed
        from quantum_debugger.density_matrix import DensityMatrix

        rng = np.random.default_rng(seed)
        M = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        rho = M @ M.conj().T
        rho = rho / np.trace(rho).real
        G = np.diag([0.5, -0.5]).astype(complex)
        dphi = 1e-4
        U = expm(-1j * G * dphi)
        f = DensityMatrix(rho=rho).fidelity(DensityMatrix(rho=U @ rho @ U.conj().T))
        numeric = 8 * (1 - np.sqrt(f)) / dphi**2
        assert abs(qfi_mixed(rho, G) - numeric) < 1e-4

    def test_mixing_reduces_fisher_information(self):
        from quantum_debugger.algorithms import qfi_mixed

        G = np.diag([0.5, -0.5]).astype(complex)
        psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
        pure = np.outer(psi, psi.conj())
        for p in (0.2, 0.5, 0.8):
            mixed = (1 - p) * pure + p * np.eye(2) / 2
            assert qfi_mixed(mixed, G) < qfi_mixed(pure, G)

    def test_maximally_mixed_is_blind(self):
        from quantum_debugger.algorithms import qfi_mixed

        G = np.diag([0.5, -0.5]).astype(complex)
        assert qfi_mixed(np.eye(2) / 2, G) < 1e-12
