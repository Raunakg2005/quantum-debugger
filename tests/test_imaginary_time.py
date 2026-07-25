"""Tests for imaginary-time evolution (cooling to the ground state)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    imaginary_time_evolution,
    fermi_hubbard_hamiltonian,
    hamiltonian_matrix,
    tfim_hamiltonian,
    heisenberg_hamiltonian,
)


class TestConvergence:
    def test_hubbard_dimer(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        r = imaginary_time_evolution(H, dtau=0.1, steps=200)
        assert r["error"] < 1e-6

    def test_tfim(self):
        H = hamiltonian_matrix(tfim_hamiltonian(4, 1.0, 1.0), 4)
        r = imaginary_time_evolution(H, dtau=0.1, steps=300)
        assert r["error"] < 1e-6

    def test_heisenberg(self):
        H = hamiltonian_matrix(heisenberg_hamiltonian(3), 3)
        r = imaginary_time_evolution(H, dtau=0.1, steps=300)
        assert r["error"] < 1e-6

    def test_energy_monotonically_decreases(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        traj = imaginary_time_evolution(H, dtau=0.1, steps=150)["energy_trajectory"]
        assert all(b <= a + 1e-12 for a, b in zip(traj, traj[1:]))

    def test_converged_state_is_ground_eigenstate(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        r = imaginary_time_evolution(H, dtau=0.1, steps=300)
        psi = r["state"]
        # H|psi> = E|psi> at the ground energy.
        residual = H @ psi - r["exact_energy"] * psi
        assert np.linalg.norm(residual) < 1e-4


class TestGroundStateAlwaysWins:
    def test_orthogonal_start_still_reaches_ground(self):
        # Even from a start numerically orthogonal to the ground state, the ~1e-16
        # residual overlap is re-amplified: cooling reaches the GROUND state, not an
        # excited one. (Plain ITE cannot target excited levels.)
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 1.0), 3)
        evals, evecs = np.linalg.eigh(H)
        ground = evecs[:, 0]
        rng = np.random.default_rng(1)
        psi0 = rng.normal(size=8) + 1j * rng.normal(size=8)
        psi0 = psi0 - (ground.conj() @ psi0) * ground
        r = imaginary_time_evolution(H, initial_state=psi0, dtau=0.15, steps=400)
        assert abs(r["energy"] - evals[0]) < 1e-4


class TestControls:
    def test_custom_initial_state(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 1.0)
        psi0 = np.zeros(16, dtype=complex)
        psi0[0b0011] = 1.0  # a half-filled basis state
        r = imaginary_time_evolution(H, initial_state=psi0, dtau=0.1, steps=200)
        assert r["error"] < 1e-6

    def test_trajectory_length(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 1.0)
        r = imaginary_time_evolution(H, dtau=0.1, steps=50)
        assert len(r["energy_trajectory"]) == 51


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
