"""
Tests for the 2.4.0 metrology suite: quantum Fisher information & Cramér-Rao bounds,
interferometric probe states (NOON/GHZ), spin squeezing, multiparameter estimation, and
sensing protocols. Verified against closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.quantum_metrology import (
    generator_variance, qfi_pure, cramer_rao_bound, standard_quantum_limit,
    heisenberg_limit, metrological_advantage, error_propagation)
from quantum_debugger.algorithms.interferometry import (
    collective_jz, product_probe, ghz_probe, product_probe_qfi, ghz_probe_qfi,
    noon_phase_qfi, ramsey_signal)
from quantum_debugger.algorithms.spin_squeezing_metrology import (
    coherent_spin_state, one_axis_twisting_state, wineland_squeezing_parameter,
    metrological_gain, is_squeezed, best_twisting_squeezing, collective_spin)
from quantum_debugger.algorithms.multiparameter_estimation import (
    qfi_matrix, cramer_rao_matrix, is_positive_semidefinite, parameter_incompatibility,
    total_precision_bound)
from quantum_debugger.algorithms.sensing_protocols import (
    signal_to_noise, phase_precision, frequency_precision, entanglement_gain,
    qfi_per_particle, is_heisenberg_scaling)


class TestQFI:
    def test_scaling_limits(self):
        for n in (2, 3, 4, 5):
            assert abs(product_probe_qfi(n) - n) < 1e-9
            assert abs(ghz_probe_qfi(n) - n**2) < 1e-9

    def test_cramer_rao(self):
        assert abs(cramer_rao_bound(ghz_probe_qfi(4), 1) - 0.25) < 1e-9
        assert heisenberg_limit(10) < standard_quantum_limit(10)
        assert abs(metrological_advantage(10) - np.sqrt(10)) < 1e-9

    def test_noon_and_error_prop(self):
        assert noon_phase_qfi(5) == 25
        err = error_propagation(lambda th: np.cos(4 * th), 0.3, lambda th: 1 - np.cos(4 * th)**2)
        assert abs(err - 0.25) < 1e-6

    def test_generator_variance(self):
        assert generator_variance(ghz_probe(3), collective_jz(3)) > 0


class TestSpinSqueezing:
    def test_coherent_is_sql(self):
        assert abs(wineland_squeezing_parameter(coherent_spin_state(6), 6) - 1) < 1e-3

    def test_oat_squeezes(self):
        oat = one_axis_twisting_state(6, 0.1)
        xi = wineland_squeezing_parameter(oat, 6)
        assert xi < 1 and metrological_gain(xi) > 1 and is_squeezed(oat, 6)

    def test_best_twisting(self):
        assert best_twisting_squeezing(6) < 1


class TestMultiparameter:
    def test_qfi_matrix_psd(self):
        psi = np.zeros(8, dtype=complex); psi[0] = psi[-1] = 1 / np.sqrt(2)
        F = qfi_matrix(psi, [collective_spin(3, "Z"), collective_spin(3, "X")])
        assert is_positive_semidefinite(F) and np.allclose(F, F.T)

    def test_incompatibility(self):
        Jz = collective_spin(3, "Z"); Jx = collective_spin(3, "X")
        assert parameter_incompatibility(coherent_spin_state(3), [Jz, Jz]) < 1e-9
        ystate = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        yn = ystate
        for _ in range(2):
            yn = np.kron(yn, ystate)
        assert parameter_incompatibility(yn, [Jz, Jx]) > 1e-6

    def test_cramer_rao_matrix(self):
        F = np.diag([4.0, 9.0])
        assert np.allclose(cramer_rao_matrix(F), np.diag([0.25, 1 / 9]))
        assert abs(total_precision_bound(F) - (0.25 + 1 / 9)) < 1e-9


class TestSensing:
    def test_snr_and_precision(self):
        assert abs(signal_to_noise(16, 100) - 40) < 1e-9
        assert abs(phase_precision(16, 100) - 1 / 40) < 1e-9
        assert abs(frequency_precision(16, 2.0, 100) - 1 / 80) < 1e-9

    def test_gain_and_per_particle(self):
        assert abs(entanglement_gain(9) - 3) < 1e-9
        assert abs(qfi_per_particle(25, 5) - 5) < 1e-9
        assert abs(qfi_per_particle(5, 5) - 1) < 1e-9

    def test_heisenberg_scaling(self):
        ns = np.array([2, 3, 4, 5])
        assert is_heisenberg_scaling(ns**2, ns)
        assert not is_heisenberg_scaling(ns.astype(float), ns)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
