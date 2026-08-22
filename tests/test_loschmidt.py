"""Tests for the Loschmidt echo and quench dynamics."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    loschmidt_echo,
    rate_function,
    quench_dynamics,
    hamiltonian_matrix,
    tfim_hamiltonian,
)


class TestLoschmidtEcho:
    def test_starts_at_one(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        psi0 = np.zeros(8, dtype=complex)
        psi0[0] = 1
        L = loschmidt_echo(H, psi0, [0.0])
        assert abs(L[0] - 1.0) < 1e-12

    def test_eigenstate_never_dephases(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        _, vecs = np.linalg.eigh(H)
        L = loschmidt_echo(H, vecs[:, 2], np.linspace(0, 8, 30))
        assert np.allclose(L, 1.0, atol=1e-9)

    def test_two_level_analytic(self):
        delta, theta = 1.7, 0.6
        H = np.array([[delta / 2, 0], [0, -delta / 2]], dtype=complex)
        psi0 = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
        times = np.linspace(0, 10, 40)
        L = loschmidt_echo(H, psi0, times)
        analytic = 1 - np.sin(2 * theta) ** 2 * np.sin(delta * times / 2) ** 2
        assert np.allclose(L, analytic, atol=1e-9)

    def test_bounded_in_unit_interval(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 1.3), 3)
        rng = np.random.default_rng(0)
        psi0 = rng.normal(size=8) + 1j * rng.normal(size=8)
        L = loschmidt_echo(H, psi0, np.linspace(0, 12, 60))
        assert np.all(L >= -1e-12) and np.all(L <= 1 + 1e-9)


class TestRateFunction:
    def test_zero_at_t0(self):
        H = hamiltonian_matrix(tfim_hamiltonian(3, 1.0, 0.7), 3)
        psi0 = np.zeros(8, dtype=complex)
        psi0[0] = 1
        assert abs(rate_function(H, psi0, [0.0])[0]) < 1e-12

    def test_peaks_where_echo_dips(self):
        delta, theta = 2.0, np.pi / 4  # theta = pi/4 -> echo dips to 0 (DQPT)
        H = np.array([[delta / 2, 0], [0, -delta / 2]], dtype=complex)
        psi0 = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
        times = np.linspace(0.01, 2 * np.pi / delta - 0.01, 200)
        L = loschmidt_echo(H, psi0, times)
        rate = rate_function(H, psi0, times, n_qubits=1)
        assert rate[np.argmin(L)] == pytest.approx(rate.max(), rel=1e-6)


class TestQuenchDynamics:
    def test_revival_for_two_level(self):
        delta, theta = 1.5, 0.5
        H = np.array([[delta / 2, 0], [0, -delta / 2]], dtype=complex)
        psi0 = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
        r = quench_dynamics(H, psi0, t_max=4 * np.pi / delta, points=300)
        assert r["revival"]  # periodic, returns near 1

    def test_dqpt_reaches_zero_echo(self):
        # theta = pi/4: the echo hits exactly 0 -- a genuine DQPT.
        delta = 2.0
        H = np.array([[delta / 2, 0], [0, -delta / 2]], dtype=complex)
        psi0 = np.array([1, 1], dtype=complex) / np.sqrt(2)
        r = quench_dynamics(H, psi0, t_max=2 * np.pi / delta, points=400)
        assert r["min_echo"] < 1e-4

    def test_output_shapes(self):
        H = hamiltonian_matrix(tfim_hamiltonian(2, 1.0, 1.0), 2)
        psi0 = np.array([1, 0, 0, 0], dtype=complex)
        r = quench_dynamics(H, psi0, points=50)
        assert len(r["times"]) == len(r["echo"]) == len(r["rate_function"]) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
