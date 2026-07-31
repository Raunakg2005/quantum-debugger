"""
Tests for the 1.9.0 characterization suite: randomized benchmarking, cross-entropy
benchmarking, quantum volume, tomography / DFE, channel metrics, and mirror
benchmarking. Verified against exact channels and closed forms.
"""

import numpy as np
import pytest
from scipy.stats import unitary_group

from quantum_debugger.algorithms.randomized_benchmarking_advanced import (
    rb_survival, fit_rb_decay, average_gate_fidelity_from_rb, error_per_clifford,
    interleaved_rb_gate_error)
from quantum_debugger.algorithms.xeb import (
    porter_thomas_pdf, porter_thomas_samples, linear_xeb_fidelity, speckle_purity,
    cross_entropy_fidelity)
from quantum_debugger.algorithms.quantum_volume import (
    heavy_outputs, heavy_output_probability, quantum_volume_pass,
    ideal_heavy_output_probability, quantum_volume)
from quantum_debugger.algorithms.tomography_dfe import (
    pauli_expectations, state_tomography, is_physical_density_matrix,
    direct_fidelity_estimation)
from quantum_debugger.algorithms.channel_metrics import (
    choi_matrix, entanglement_fidelity, average_gate_fidelity, pauli_transfer_matrix,
    unitarity)
from quantum_debugger.algorithms.mirror_benchmarking import (
    mirror_survival, depolarizing_layer, mirror_fidelity_decay)


def _depol_kraus(pd):
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.diag([1, -1]).astype(complex)
    return [np.sqrt(1 - 3 * pd / 4) * I, np.sqrt(pd / 4) * X,
            np.sqrt(pd / 4) * Y, np.sqrt(pd / 4) * Z]


class TestRB:
    def test_fit_recovers_decay(self):
        m = np.array([1, 2, 5, 10, 20, 50, 100])
        p, A, B = fit_rb_decay(m, rb_survival(0.98, m))
        assert abs(p - 0.98) < 1e-3

    def test_fidelity_conversion(self):
        assert abs(average_gate_fidelity_from_rb(0.98) - 0.99) < 1e-9
        assert abs(error_per_clifford(0.98) - 0.01) < 1e-9      # (1-p)(d-1)/d = 0.02*0.5

    def test_interleaved(self):
        p_ref = 0.98
        p_int = p_ref * (1 - 2 * 0.005)          # planted gate error 0.005 (d=2)
        assert abs(interleaved_rb_gate_error(p_ref, p_int) - 0.005) < 1e-9


class TestXEB:
    def test_porter_thomas(self):
        dim = 64
        xs = np.linspace(0, 0.2, 100000)
        assert abs(np.trapezoid(porter_thomas_pdf(xs, dim), xs) - 1) < 1e-2
        assert abs(np.trapezoid(xs * porter_thomas_pdf(xs, dim), xs) * dim - 1) < 1e-2

    def test_xeb_fidelity(self):
        rng = np.random.default_rng(0)
        dim = 64
        ideal = porter_thomas_samples(dim, 1, rng)[0]
        s_ideal = rng.choice(dim, size=30000, p=ideal)
        s_unif = rng.choice(dim, size=30000)
        assert abs(linear_xeb_fidelity(ideal, s_ideal) - 1) < 0.1
        assert abs(linear_xeb_fidelity(ideal, s_unif)) < 0.1

    def test_cross_entropy(self):
        rng = np.random.default_rng(1)
        ideal = porter_thomas_samples(32, 1, rng)[0]
        assert abs(cross_entropy_fidelity(ideal, ideal) - 1) < 1e-9
        assert abs(cross_entropy_fidelity(ideal, np.ones(32) / 32)) < 1e-9


class TestQuantumVolume:
    def test_heavy_output(self):
        rng = np.random.default_rng(0)
        probs = porter_thomas_samples(16, 1, rng)[0]
        hop = heavy_output_probability(probs)
        assert hop > 0.5
        assert quantum_volume_pass(0.8) and not quantum_volume_pass(0.6)

    def test_ideal_asymptote(self):
        assert abs(ideal_heavy_output_probability() - (1 + np.log(2)) / 2) < 1e-9
        assert quantum_volume(5) == 32


class TestTomography:
    def test_state_tomography(self):
        rng = np.random.default_rng(0)
        A = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
        rho = A @ A.conj().T; rho /= np.trace(rho)
        assert np.allclose(state_tomography(pauli_expectations(rho), 2), rho, atol=1e-9)
        assert is_physical_density_matrix(rho)

    def test_dfe(self):
        rng = np.random.default_rng(1)
        A = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
        rho = A @ A.conj().T; rho /= np.trace(rho)
        psi = rng.normal(size=4) + 1j * rng.normal(size=4); psi /= np.linalg.norm(psi)
        target = np.outer(psi, psi.conj())
        assert abs(direct_fidelity_estimation(rho, target) - np.real(np.vdot(psi, rho @ psi))) < 1e-9


class TestChannelMetrics:
    def test_exact_unitary(self):
        U = unitary_group.rvs(2, random_state=1)
        assert abs(average_gate_fidelity([U], U) - 1) < 1e-9
        assert abs(entanglement_fidelity([U], U) - 1) < 1e-9
        assert abs(unitarity([U], 1) - 1) < 1e-9

    def test_depolarizing_unitarity(self):
        K = _depol_kraus(0.2)
        decay = pauli_transfer_matrix(K, 1)[1, 1]
        assert abs(unitarity(K, 1) - decay ** 2) < 1e-9

    def test_choi(self):
        U = unitary_group.rvs(2, random_state=2)
        choi = choi_matrix([U], 2)
        assert np.min(np.linalg.eigvalsh(choi)) > -1e-9 and abs(np.trace(choi) - 2) < 1e-9


class TestMirror:
    def test_noiseless(self):
        layers = [unitary_group.rvs(4, random_state=i) for i in range(3)]
        assert abs(mirror_survival(layers) - 1) < 1e-9

    def test_noisy_decays(self):
        layers = [unitary_group.rvs(4, random_state=i) for i in range(3)]
        assert mirror_survival(layers, noise_channel=depolarizing_layer(0.05)) < 1
        d = mirror_fidelity_decay([layers[:1], layers[:2], layers[:3]], 0.05)
        assert all(d[i] >= d[i + 1] for i in range(2))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
