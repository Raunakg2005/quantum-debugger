"""
Tests for the 1.7.0 advanced-algorithms suite: quantum walks, amplitude estimation
(MLQAE / IQAE / canonical), Markov chains & quantum PageRank, phase-estimation variants,
and quantum mean estimation. Verified against exact evolution and closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.quantum_walks import (
    continuous_time_walk_operator, ctqw_distribution, position_variance, line_adjacency,
    discrete_time_walk_line, szegedy_walk_operator, spatial_search_ctqw)
from quantum_debugger.algorithms.amplitude_estimation_advanced import (
    grover_probability, maximum_likelihood_ae, iterative_ae, canonical_qae,
    classical_monte_carlo_error, heisenberg_scaling_error)
from quantum_debugger.algorithms.quantum_markov import (
    is_stochastic, stationary_distribution, google_matrix, classical_pagerank,
    detailed_balance, quantum_pagerank)
from quantum_debugger.algorithms.phase_estimation_variants import (
    kitaev_phase_estimation, robust_phase_estimation, phase_estimation_error)
from quantum_debugger.algorithms.quantum_mean_estimation import (
    mean_amplitude, quantum_mean_estimation, monte_carlo_speedup)


class TestQuantumWalks:
    def test_ctqw_unitary_conserving(self):
        A = line_adjacency(15)
        U = continuous_time_walk_operator(A, 2.0)
        assert np.allclose(U.conj().T @ U, np.eye(15), atol=1e-9)
        assert abs(ctqw_distribution(A, 3.0, 7).sum() - 1) < 1e-9

    def test_ballistic_spread(self):
        A = line_adjacency(21)
        v2 = position_variance(ctqw_distribution(A, 2.0, 10))
        v4 = position_variance(ctqw_distribution(A, 4.0, 10))
        assert abs(v4 / v2 - 4.0) < 0.2       # variance ~ t^2

    def test_dtqw(self):
        d = discrete_time_walk_line(20)
        assert abs(d.sum() - 1) < 1e-9
        assert position_variance(d) > 20      # ballistic, far above classical ~20

    def test_szegedy_unitary(self):
        P = np.array([[0.5, 0.5], [0.25, 0.75]])
        W = szegedy_walk_operator(P)
        assert np.allclose(W.conj().T @ W, np.eye(4), atol=1e-9)

    def test_spatial_search(self):
        n = 16
        K = np.ones((n, n)) - np.eye(n)
        p = spatial_search_ctqw(K, 3, 1.0 / n, np.pi / 2 * np.sqrt(n))
        assert p > 0.4                        # from uniform 1/16


class TestAmplitudeEstimation:
    def test_grover_probability(self):
        assert abs(grover_probability(0.3, 0) - 0.09) < 1e-12

    def test_mlqae(self):
        assert abs(maximum_likelihood_ae(0.3, [0, 1, 2, 4, 8], shots=4000, seed=1) - 0.3) < 0.02

    def test_mlqae_heisenberg(self):
        e_shallow = np.mean([abs(maximum_likelihood_ae(0.3, [0, 1], shots=1000, seed=s) - 0.3) for s in range(8)])
        e_deep = np.mean([abs(maximum_likelihood_ae(0.3, [0, 1, 2, 4, 8, 16], shots=1000, seed=s) - 0.3) for s in range(8)])
        assert e_deep < e_shallow             # more/higher powers -> smaller error

    def test_iqae(self):
        assert abs(iterative_ae(0.3, rounds=7, shots=4000, seed=2) - 0.3) < 0.02

    def test_canonical_precision(self):
        assert abs(canonical_qae(0.3, 8) - 0.3) < 0.02
        assert heisenberg_scaling_error(100) < classical_monte_carlo_error(100)


class TestMarkov:
    def test_stationary(self):
        P = np.array([[0.5, 0.5], [0.25, 0.75]])
        pi = stationary_distribution(P)
        assert np.allclose(pi @ P, pi, atol=1e-9) and abs(pi.sum() - 1) < 1e-9

    def test_google_matrix(self):
        A = np.array([[0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 0, 1, 0]], dtype=float)
        assert is_stochastic(google_matrix(A), axis=1)

    def test_pagerank_valid(self):
        A = np.array([[0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 0, 1, 0]], dtype=float)
        pr = classical_pagerank(A)
        qpr = quantum_pagerank(A, steps=300)
        assert abs(pr.sum() - 1) < 1e-9
        assert abs(qpr.sum() - 1) < 1e-9 and np.all(qpr >= -1e-9)
        assert np.argmax(qpr) == np.argmax(pr)     # same top node

    def test_detailed_balance(self):
        P = np.array([[0.5, 0.5], [0.25, 0.75]])
        assert detailed_balance(P, stationary_distribution(P))


class TestPhaseEstimation:
    def test_kitaev(self):
        assert abs(kitaev_phase_estimation(0.375, 4) - 0.375) < 1e-9
        assert abs(kitaev_phase_estimation(0.1, 8) - 0.1) <= phase_estimation_error(8) + 1e-9

    def test_robust(self):
        for phi in (0.3, 0.7):
            r = robust_phase_estimation(phi, max_k=8, shots=4000, seed=1)
            assert min(abs(r - phi), 1 - abs(r - phi)) < 0.02


class TestMeanEstimation:
    def test_mean(self):
        rng = np.random.default_rng(0)
        f = rng.uniform(0, 1, 16)
        assert abs(mean_amplitude(f) ** 2 - f.mean()) < 1e-9
        assert abs(quantum_mean_estimation(f, shots=4000, seed=1) - f.mean()) < 0.02

    def test_speedup(self):
        assert abs(monte_carlo_speedup(0.01) - 100) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
