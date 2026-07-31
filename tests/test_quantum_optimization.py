"""
Tests for the 2.1.0 optimization suite: QUBO/Ising encodings, QAOA theory, adiabatic
optimization, quantum annealing, and Dürr-Høyer minimization. Verified against brute
force and closed forms.
"""

import numpy as np
import pytest
from itertools import product
from scipy.linalg import expm

from quantum_debugger.algorithms.qubo import (
    qubo_energy, ising_energy, qubo_to_ising, ising_hamiltonian, brute_force_ising,
    brute_force_qubo, max_cut_qubo, number_partition_qubo, vertex_cover_qubo)
from quantum_debugger.algorithms.qaoa_theory import (
    cost_diagonal, mixer_layer, qaoa_state, qaoa_expectation, optimize_qaoa_p1, qaoa_landscape)
from quantum_debugger.algorithms.adiabatic_optimization import (
    transverse_field_driver, minimum_gap, adiabatic_success_probability,
    landau_zener_probability, adiabatic_runtime_bound)
from quantum_debugger.algorithms.quantum_annealing import (
    annealing_success_probability, annealed_solution)
from quantum_debugger.algorithms.grover_optimization import (
    durr_hoyer_minimize, grover_adaptive_search, quantum_minimum_queries, classical_minimum_queries)


class TestQUBO:
    def test_qubo_ising_equivalence(self):
        rng = np.random.default_rng(0)
        Q = rng.normal(size=(4, 4)); Q = (Q + Q.T) / 2
        h, J, off = qubo_to_ising(Q)
        for bits in product([0, 1], repeat=4):
            x = np.array(bits)
            assert abs(qubo_energy(Q, x) - (ising_energy(h, J, 1 - 2 * x) + off)) < 1e-9

    def test_ising_ground_state(self):
        rng = np.random.default_rng(1)
        Q = rng.normal(size=(4, 4)); Q = (Q + Q.T) / 2
        h, J, _ = qubo_to_ising(Q)
        _, bf_e = brute_force_ising(h, J)
        assert abs(np.diag(ising_hamiltonian(h, J)).real.min() - bf_e) < 1e-9

    def test_max_cut(self):
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
        Q = max_cut_qubo(edges, 4)
        x_opt, _ = brute_force_qubo(Q)
        cut = sum(1 for i, j in edges if x_opt[i] != x_opt[j])
        true_max = max(sum(1 for i, j in edges if b[i] != b[j]) for b in product([0, 1], repeat=4))
        assert cut == true_max

    def test_number_partition(self):
        nums = [3, 1, 1, 2, 2, 1]
        x, _ = brute_force_qubo(number_partition_qubo(nums))
        subset = sum(nums[i] for i in range(len(nums)) if x[i] == 1)
        assert subset == sum(nums) / 2

    def test_vertex_cover(self):
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        x, _ = brute_force_qubo(vertex_cover_qubo(edges, 4, penalty=3.0))
        assert all(x[i] == 1 or x[j] == 1 for i, j in edges)


class TestQAOA:
    def test_cost_diagonal(self):
        assert int(cost_diagonal([(0, 1), (1, 2), (2, 3), (3, 0)], 4).max()) == 4

    def test_state_and_mixer(self):
        diag = cost_diagonal([(0, 1), (1, 2)], 3)
        psi = qaoa_state(diag, [0.5], [0.3], 3)
        assert abs(np.vdot(psi, psi) - 1) < 1e-9
        r = np.random.default_rng(0).normal(size=8) + 1j * np.random.default_rng(1).normal(size=8)
        r /= np.linalg.norm(r)
        assert abs(np.linalg.norm(mixer_layer(r, 0.7, 3)) - 1) < 1e-9

    def test_optimize_beats_random(self):
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        opt = optimize_qaoa_p1(edges, 4)
        assert opt["expectation"] > len(edges) / 2
        assert opt["approximation_ratio"] > 0.7

    def test_landscape_shape(self):
        assert qaoa_landscape([(0, 1), (1, 2)], 3, grid=10).shape == (10, 10)


class TestAdiabatic:
    def _H(self):
        from quantum_debugger.algorithms.qubo import ising_hamiltonian
        h = np.array([0.5, -0.5, 0.2]); J = np.zeros((3, 3)); J[0, 1] = 1.0; J[1, 2] = -0.5
        return transverse_field_driver(3), ising_hamiltonian(h, J)

    def test_gap_and_runtime(self):
        H0, H1 = self._H()
        mg = minimum_gap(H0, H1)
        assert mg > 0 and adiabatic_runtime_bound(mg) == pytest.approx(1 / mg**2)

    def test_slow_anneal_succeeds(self):
        H0, H1 = self._H()
        p_fast = adiabatic_success_probability(H0, H1, 1.0, steps=200)
        p_slow = adiabatic_success_probability(H0, H1, 50.0, steps=300)
        assert p_slow > p_fast and p_slow > 0.95

    def test_landau_zener(self):
        def lz_sim(d, v, T=40, steps=8000):
            dt = 2 * T / steps
            psi = np.linalg.eigh(np.array([[-v * T, d / 2], [d / 2, v * T]], dtype=complex))[1][:, 0]
            for k in range(steps):
                t = -T + (k + 0.5) * dt
                psi = expm(-1j * np.array([[v * t, d / 2], [d / 2, -v * t]], dtype=complex) * dt) @ psi
            vec = np.linalg.eigh(np.array([[v * T, d / 2], [d / 2, -v * T]], dtype=complex))[1]
            return abs(np.vdot(vec[:, 1], psi)) ** 2
        for d, v in [(1.0, 2.0), (0.5, 1.0)]:
            assert abs(lz_sim(d, v) - landau_zener_probability(d, v)) < 0.02


class TestAnnealing:
    def test_anneal_finds_ground(self):
        h = np.array([0.5, -0.5, 0.2]); J = np.zeros((3, 3)); J[0, 1] = 1.0; J[1, 2] = -0.5
        assert annealing_success_probability(h, J, 50.0, steps=300) > 0.95
        assert np.array_equal(annealed_solution(h, J, 50.0, steps=300), brute_force_ising(h, J)[0])


class TestGroverOptimization:
    def test_durr_hoyer(self):
        vals = np.random.default_rng(3).uniform(0, 10, 16)
        assert durr_hoyer_minimize(vals, seed=1)["found_optimum"]
        rate = np.mean([durr_hoyer_minimize(vals, seed=s)["found_optimum"] for s in range(20)])
        assert rate > 0.9

    def test_adaptive_search(self):
        assert grover_adaptive_search(lambda x: (x - 5) ** 2, 3, seed=0)["argmin"] == 5

    def test_query_scaling(self):
        assert quantum_minimum_queries(256) < classical_minimum_queries(256)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
