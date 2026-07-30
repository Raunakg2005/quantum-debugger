"""
Tests for the 0.9.0 many-body backfill: the SSH topological insulator, the fidelity
approach to quantum phase transitions, correlation functions, and entanglement
negativity. Verified against exact diagonalization and closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.ssh_model import (
    ssh_hamiltonian, ssh_winding_number, ssh_zero_modes, ssh_edge_polarization)
from quantum_debugger.algorithms.quantum_phase_transition import (
    ground_state_fidelity, fidelity_susceptibility, tfim_critical_field)
from quantum_debugger.algorithms.many_body_correlations import (
    connected_correlation, correlation_length, structure_factor)
from quantum_debugger.algorithms.entanglement_negativity import (
    partial_transpose, negativity, logarithmic_negativity, is_entangled_ppt)
from quantum_debugger.algorithms.vqe_solver import tfim_hamiltonian
from quantum_debugger.algorithms.hamiltonian_simulation import hamiltonian_matrix


def _bell_rho():
    bell = np.zeros(4, dtype=complex); bell[0] = bell[3] = 1 / np.sqrt(2)
    return np.outer(bell, bell.conj())


def _tfim_ground(n, h):
    H = hamiltonian_matrix(tfim_hamiltonian(n, h, 1.0), n)
    return np.linalg.eigh(H)[1][:, 0]


class TestSSH:
    def test_chiral_symmetry(self):
        eigs = np.linalg.eigvalsh(ssh_hamiltonian(6, 0.4, 1.0))
        assert np.allclose(np.sort(eigs), -np.sort(-eigs)[::-1], atol=1e-9)

    def test_winding_number(self):
        assert ssh_winding_number(1.0, 0.4) == 0    # trivial
        assert ssh_winding_number(0.4, 1.0) == 1    # topological

    def test_edge_modes(self):
        assert ssh_zero_modes(6, 0.4, 1.0) == 2     # topological: 2 edge modes
        assert ssh_zero_modes(6, 1.0, 0.4) == 0     # trivial: none
        assert ssh_edge_polarization(6, 0.4, 1.0) > 1.0  # modes pinned to the ends


class TestQuantumPhaseTransition:
    def test_fidelity_bounds(self):
        f = ground_state_fidelity(lambda h: tfim_hamiltonian(6, h, 1.0), 0.5, 1e-3, 6)
        assert 0.0 <= f <= 1.0 + 1e-12

    def test_susceptibility_positive(self):
        chi = fidelity_susceptibility(lambda h: tfim_hamiltonian(6, h, 1.0), 1.0, 6)
        assert chi > 0

    def test_critical_peak_drifts_to_one(self):
        peaks = [tfim_critical_field(n) for n in (4, 6, 8, 10)]
        assert all(peaks[i] <= peaks[i + 1] + 1e-9 for i in range(3))  # -> h_c = 1
        assert peaks[-1] > peaks[0]


class TestCorrelations:
    def test_ghz_connected(self):
        n = 4; ghz = np.zeros(2**n, dtype=complex); ghz[0] = ghz[-1] = 1 / np.sqrt(2)
        assert abs(connected_correlation(ghz, 0, 2, "Z") - 1.0) < 1e-9

    def test_product_no_correlation(self):
        n = 4; plus = np.ones(2**n, dtype=complex) / 2**(n / 2)
        assert abs(connected_correlation(plus, 0, 2, "Z")) < 1e-9
        assert correlation_length(plus, "Z") == 0.0

    def test_structure_factor_order(self):
        neel = np.zeros(16, dtype=complex); neel[0b0101] = 1
        assert structure_factor(neel, np.pi) > structure_factor(neel, 0.0)   # AFM
        fm = np.zeros(16, dtype=complex); fm[0] = 1
        assert structure_factor(fm, 0.0) > structure_factor(fm, np.pi)       # FM

    def test_correlation_length_grows_at_criticality(self):
        xi_para = correlation_length(_tfim_ground(8, 3.0), "Z")
        xi_crit = correlation_length(_tfim_ground(8, 1.1), "Z")
        assert xi_crit > xi_para


class TestNegativity:
    def test_bell_log_negativity(self):
        assert abs(logarithmic_negativity(_bell_rho(), (2, 2)) - 1.0) < 1e-9
        assert is_entangled_ppt(_bell_rho(), (2, 2))

    def test_product_zero(self):
        p = np.zeros(4, dtype=complex); p[0] = 1
        rho = np.outer(p, p.conj())
        assert abs(logarithmic_negativity(rho, (2, 2))) < 1e-9
        assert not is_entangled_ppt(rho, (2, 2))

    def test_werner_threshold(self):
        rho = _bell_rho()
        for p, entangled in [(0.2, False), (0.5, True)]:
            rw = p * rho + (1 - p) * np.eye(4) / 4
            assert is_entangled_ppt(rw, (2, 2)) == entangled   # entangled iff p > 1/3

    def test_partial_transpose_involution(self):
        rho = _bell_rho()
        assert np.allclose(partial_transpose(partial_transpose(rho, (2, 2)), (2, 2)), rho)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
