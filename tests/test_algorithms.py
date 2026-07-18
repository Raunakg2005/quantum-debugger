"""Tests for the quantum algorithms library (QFT, Grover, QPE, BV, DJ)."""

import numpy as np
import pytest

from quantum_debugger.core.quantum_state import QuantumState
from quantum_debugger.algorithms import (
    qft,
    qft_matrix,
    grover,
    grover_search,
    optimal_iterations,
    estimate_phase,
    bernstein_vazirani,
    deutsch_jozsa,
    constant_oracle,
    balanced_oracle,
    quantum_walk,
    quantum_counting,
)


def _circuit_unitary(circuit, n):
    N = 2**n
    U = np.zeros((N, N), dtype=complex)
    for x in range(N):
        e = np.zeros(N, dtype=complex)
        e[x] = 1.0
        state = QuantumState(n, state_vector=e)
        for g in circuit.gates:
            state.apply_gate(g.matrix, g.qubits)
        U[:, x] = state.state_vector
    return U


class TestQFT:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_matches_dft(self, n):
        U = _circuit_unitary(qft(n), n)
        assert np.allclose(U, qft_matrix(n), atol=1e-10)

    def test_inverse_undoes_forward(self):
        n = 3
        Uf = _circuit_unitary(qft(n), n)
        Ui = _circuit_unitary(qft(n, inverse=True), n)
        assert np.allclose(Ui @ Uf, np.eye(2**n), atol=1e-10)

    def test_qft_zero_is_uniform(self):
        n = 3
        U = _circuit_unitary(qft(n), n)
        assert np.allclose(np.abs(U[:, 0]), 1 / np.sqrt(2**n))


class TestGrover:
    def test_finds_single_marked_state(self):
        result = grover_search(3, marked_states=5)
        assert result["best_state"] == 5
        assert result["success_probability"] > 0.9

    def test_finds_multiple_marked_states(self):
        result = grover_search(4, marked_states=[3, 10])
        assert result["best_state"] in (3, 10)
        assert result["success_probability"] > 0.9

    def test_optimal_iterations(self):
        assert optimal_iterations(3, 1) >= 1
        assert optimal_iterations(10, 1) > optimal_iterations(4, 1)

    def test_returns_valid_probabilities(self):
        circuit = grover(3, 2)
        probs = circuit.get_statevector().get_probabilities()
        assert np.isclose(probs.sum(), 1.0)


class TestPhaseEstimation:
    @pytest.mark.parametrize("frac", [0.25, 0.125, 0.75, 0.5])
    def test_estimates_exact_phase(self, frac):
        result = estimate_phase(2 * np.pi * frac, n_counting=4)
        assert np.isclose(result["phase"], frac, atol=1e-6)
        assert result["probability"] > 0.99


class TestBernsteinVazirani:
    @pytest.mark.parametrize("secret", ["101", "1101", "0110", "111"])
    def test_recovers_secret_in_one_query(self, secret):
        recovered = "".join(map(str, bernstein_vazirani(secret)))
        assert recovered == secret


class TestDeutschJozsa:
    def test_constant(self):
        assert deutsch_jozsa(constant_oracle(0), n=3) == "constant"
        assert deutsch_jozsa(constant_oracle(1), n=3) == "constant"

    def test_balanced(self):
        assert deutsch_jozsa(balanced_oracle(3), n=3) == "balanced"


class TestQuantumWalk:
    def test_distribution_is_valid(self):
        r = quantum_walk(n_position_qubits=4, steps=5)
        assert np.isclose(r["distribution"].sum(), 1.0)
        assert r["distribution"].shape == (16,)

    def test_ballistic_spread(self):
        # Ballistic: std ~ steps, so doubling steps ~doubles std (ratio near 2,
        # vs a classical diffusive walk where the ratio is ~sqrt(2)=1.41).
        s8 = quantum_walk(5, 8)["std"]
        s16 = quantum_walk(5, 16)["std"]
        assert s16 / s8 > 1.7
        assert s16 > np.sqrt(16)  # far broader than a classical random walk


class TestQuantumCounting:
    @pytest.mark.parametrize("marked", [[3], [1, 5, 9], [0, 2, 4, 6, 8, 10]])
    def test_estimates_count(self, marked):
        result = quantum_counting(n_qubits=4, marked=marked, n_counting=5)
        assert result["true_count"] == len(marked)
        assert abs(result["estimated_count"] - len(marked)) < 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
