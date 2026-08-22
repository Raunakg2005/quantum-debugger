"""Tests for Krylov subspace diagonalization (Lanczos)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    krylov_spectrum,
    krylov_ground_energy,
    hamiltonian_matrix,
    tfim_hamiltonian,
    fermi_hubbard_hamiltonian,
    heisenberg_hamiltonian,
)


class TestGroundEnergy:
    def test_tfim_converges(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        assert krylov_ground_energy(H, dim=8, seed=1)["error"] < 1e-8

    def test_hubbard_converges(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        assert krylov_ground_energy(H, dim=10, seed=0)["error"] < 1e-6

    def test_heisenberg_converges(self):
        H = hamiltonian_matrix(heisenberg_hamiltonian(3), 3)
        assert krylov_ground_energy(H, dim=8, seed=2)["error"] < 1e-6

    def test_error_decreases_with_subspace_size(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        errs = [krylov_ground_energy(H, dim=m, seed=1)["error"] for m in (2, 4, 6, 8)]
        assert errs[-1] < errs[0]
        assert errs[-1] < 1e-6


class TestExcitedStates:
    def test_recovers_low_lying_spectrum(self):
        # By dim = full, the lowest Ritz values match the exact low-lying levels.
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        exact = np.sort(np.linalg.eigvalsh(H).real)
        ritz = krylov_spectrum(H, dim=8, seed=1)
        assert np.allclose(ritz[:3], exact[:3], atol=1e-4)

    def test_first_excited_state(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        exact = np.sort(np.linalg.eigvalsh(H).real)
        ritz = krylov_spectrum(H, dim=8, seed=3)
        assert abs(ritz[1] - exact[1]) < 1e-4


class TestProperties:
    def test_ritz_values_are_real_and_sorted(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        ritz = krylov_spectrum(H, dim=6, seed=0)
        assert np.allclose(ritz.imag, 0, atol=1e-12)
        assert np.all(np.diff(ritz) >= -1e-12)

    def test_ritz_values_bracketed_by_exact_spectrum(self):
        # Ritz values lie within the exact spectral range.
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        exact = np.linalg.eigvalsh(H).real
        ritz = krylov_spectrum(H, dim=6, seed=0)
        assert ritz.min() >= exact.min() - 1e-9
        assert ritz.max() <= exact.max() + 1e-9

    def test_custom_initial_state(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        psi0 = np.zeros(16, dtype=complex)
        psi0[0b0011] = 1.0
        assert krylov_ground_energy(H, dim=12, initial_state=psi0)["error"] < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
