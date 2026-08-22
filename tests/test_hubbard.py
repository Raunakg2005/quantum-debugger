"""Tests for the Fermi-Hubbard model."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    fermi_hubbard_hamiltonian,
    hubbard_ground_energy,
    hubbard_dimer_energy,
    jw_total_number,
)


class TestHamiltonian:
    def test_hermitian(self):
        H = fermi_hubbard_hamiltonian(2, t=1.0, u=2.5)
        assert np.allclose(H, H.conj().T)

    def test_conserves_particle_number(self):
        H = fermi_hubbard_hamiltonian(2, t=1.0, u=3.0)
        N = jw_total_number(4)
        assert np.allclose(H @ N - N @ H, 0, atol=1e-12)

    def test_conserves_spin_populations(self):
        # Total up-count and down-count are separately conserved.
        H = fermi_hubbard_hamiltonian(2, t=1.0, u=3.0)
        n_modes = 4
        from quantum_debugger.algorithms import jw_number

        N_up = jw_number(0, n_modes) + jw_number(2, n_modes)
        assert np.allclose(H @ N_up - N_up @ H, 0, atol=1e-12)


class TestDimer:
    @pytest.mark.parametrize("u", [0.0, 1.0, 3.0, 8.0, 20.0])
    def test_ground_energy_matches_analytic(self, u):
        r = hubbard_dimer_energy(t=1.0, u=u)
        assert abs(r["ground_energy"] - r["analytic"]) < 1e-9

    def test_noninteracting_is_minus_2t(self):
        assert abs(hubbard_dimer_energy(t=1.3, u=0.0)["ground_energy"] + 2 * 1.3) < 1e-9

    def test_approaches_heisenberg_at_large_u(self):
        # E_0 -> -4 t^2 / U as U grows.
        r = hubbard_dimer_energy(t=1.0, u=50.0)
        assert abs(r["ground_energy"] - r["heisenberg_limit"]) < 0.02

    def test_energy_increases_with_repulsion(self):
        energies = [
            hubbard_dimer_energy(1.0, u)["ground_energy"] for u in (0, 2, 5, 10)
        ]
        assert all(b > a for a, b in zip(energies, energies[1:]))


class TestParticleSectors:
    def test_half_filling_is_the_ground_sector(self):
        # Hopping lowers the half-filled energy below the empty lattice, so the
        # global minimum coincides with the half-filled sector.
        overall = hubbard_ground_energy(2, 1.0, 3.0)
        half = hubbard_ground_energy(2, 1.0, 3.0, n_particles=2)
        assert abs(overall - half) < 1e-9
        assert half < 0

    def test_single_particle_is_bonding_energy(self):
        # One electron on a dimer: bonding orbital at -t; U is irrelevant (no pair).
        e = hubbard_ground_energy(2, 1.0, 5.0, n_particles=1)
        assert abs(e + 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
