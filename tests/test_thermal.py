"""Tests for Gibbs states and quantum thermodynamics."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    gibbs_state,
    partition_function,
    thermal_properties,
    fermi_hubbard_hamiltonian,
)

_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class TestGibbsState:
    def test_valid_density_matrix(self):
        rho = gibbs_state(fermi_hubbard_hamiltonian(2, 1.0, 2.0), beta=0.8)
        assert abs(np.trace(rho).real - 1.0) < 1e-12
        assert np.allclose(rho, rho.conj().T)
        assert np.linalg.eigvalsh(rho).min() > -1e-12

    def test_infinite_temperature_is_maximally_mixed(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        d = H.shape[0]
        rho = gibbs_state(H, beta=1e-7)
        assert np.allclose(rho, np.eye(d) / d, atol=1e-4)

    def test_zero_temperature_is_ground_state(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 3.0)
        rho = gibbs_state(H, beta=300)
        gs = np.linalg.eigvalsh(H).real.min()
        assert abs(np.real(np.trace(rho @ H)) - gs) < 1e-6

    def test_partition_function_counts_states_at_zero_beta(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 1.0)
        assert abs(partition_function(H, 1e-9) - H.shape[0]) < 1e-3


class TestThermodynamics:
    @pytest.mark.parametrize("beta", [0.2, 0.5, 1.0, 2.0, 5.0])
    def test_free_energy_identity(self, beta):
        # F = E - S/beta exactly (F = E - T S).
        r = thermal_properties(fermi_hubbard_hamiltonian(2, 1.0, 2.0), beta)
        assert abs(r["free_energy"] - r["free_energy_check"]) < 1e-9

    def test_entropy_decreases_with_beta(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        entropies = [thermal_properties(H, b)["entropy"] for b in (0.1, 0.5, 2.0, 10.0)]
        assert all(b < a for a, b in zip(entropies, entropies[1:]))

    def test_entropy_bounds(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        d = H.shape[0]
        hot = thermal_properties(H, 1e-6)["entropy"]
        assert abs(hot - np.log(d)) < 1e-3          # max entropy = ln(d)
        assert thermal_properties(H, 100)["entropy"] < 1e-3  # -> 0 at T=0

    def test_heat_capacity_nonnegative(self):
        H = fermi_hubbard_hamiltonian(2, 1.0, 2.0)
        for beta in (0.2, 1.0, 3.0):
            assert thermal_properties(H, beta)["heat_capacity"] >= -1e-12

    def test_single_qubit_analytic(self):
        # H = Z: two levels +/-1. Analytic <H> = -tanh(beta), Z = 2 cosh(beta).
        for beta in (0.3, 1.0, 2.5):
            r = thermal_properties(_Z, beta)
            assert abs(r["energy"] + np.tanh(beta)) < 1e-9
            assert abs(partition_function(_Z, beta) - 2 * np.cosh(beta)) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
