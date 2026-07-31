"""
Tests for the 2.3.0 Hamiltonian-simulation suite: Trotter-Suzuki product formulas and
their error scaling, commutator bounds, qDRIFT, Taylor-series simulation, and gate-count
complexity. Verified against the exact e^{-iHt}.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.product_formulas import (
    exact_evolution, first_order_trotter, second_order_trotter, fourth_order_suzuki,
    trotter_error, simulate_state, error_scaling_slope)
from quantum_debugger.algorithms.trotter_bounds import (
    commutator, commutator_sum, first_order_error_bound, second_order_error_bound, terms_commute)
from quantum_debugger.algorithms.qdrift import (
    qdrift_probabilities, qdrift_error, qdrift_gate_count)
from quantum_debugger.algorithms.taylor_simulation import (
    taylor_series_unitary, taylor_error, taylor_truncation_order, hamiltonian_from_terms,
    series_convergence)
from quantum_debugger.algorithms.simulation_complexity import (
    trotter_first_order_gate_count, qdrift_beats_trotter, cheapest_method)

_TERMS = [(1.0, "ZZI"), (1.0, "IZZ"), (0.7, "XII"), (0.7, "IXI"), (0.7, "IIX")]


class TestProductFormulas:
    def test_exact_unitary(self):
        E = exact_evolution(_TERMS, 1.0)
        assert np.allclose(E.conj().T @ E, np.eye(8), atol=1e-9)

    def test_error_decreases(self):
        assert trotter_error(_TERMS, 1.0, 16, 1) < trotter_error(_TERMS, 1.0, 1, 1)
        assert trotter_error(_TERMS, 1.0, 16, 2) < trotter_error(_TERMS, 1.0, 16, 1)

    def test_order_slopes(self):
        s1 = error_scaling_slope(_TERMS, 1.0, 1)
        s2 = error_scaling_slope(_TERMS, 1.0, 2)
        s4 = error_scaling_slope(_TERMS, 1.0, 4, (1, 2, 4, 8))
        assert abs(s1 + 1) < 0.2 and abs(s2 + 2) < 0.2 and abs(s4 + 4) < 0.6

    def test_simulate_state(self):
        f = [simulate_state(_TERMS, 1.0, r, 2) for r in (1, 16)]
        assert f[1] > f[0] and f[1] > 0.999


class TestTrotterBounds:
    def test_bounds_hold(self):
        t = 0.5
        assert first_order_error_bound(_TERMS, t) >= trotter_error(_TERMS, t, 1, 1)
        assert second_order_error_bound(_TERMS, t) >= trotter_error(_TERMS, t, 1, 2)

    def test_commuting_exact(self):
        comm = [(1.0, "ZZI"), (0.5, "IZZ"), (0.3, "ZIZ")]
        assert terms_commute(comm)
        assert trotter_error(comm, 0.5, 1, 1) < 1e-9

    def test_commutator(self):
        X = np.array([[0, 1], [1, 0]]); Z = np.array([[1, 0], [0, -1]])
        assert np.allclose(commutator(X, Z), X @ Z - Z @ X)
        assert commutator_sum(_TERMS) > 0


class TestQDRIFT:
    def test_probabilities(self):
        probs, lam = qdrift_probabilities(_TERMS)
        assert abs(probs.sum() - 1) < 1e-9 and abs(lam - 4.1) < 1e-9

    def test_error_decreases(self):
        psi = np.zeros(8, dtype=complex); psi[0] = 1
        rho = np.outer(psi, psi.conj())
        errs = [qdrift_error(_TERMS, 0.5, N, rho, samples=400, seed=1) for N in (5, 80)]
        assert errs[1] < errs[0]

    def test_gate_count(self):
        assert qdrift_gate_count(4.1, 1.0, 0.01) > 0


class TestTaylor:
    def test_factorial_convergence(self):
        H = hamiltonian_from_terms(_TERMS)
        conv = series_convergence(H, 0.5)
        assert all(conv[i] > conv[i + 1] for i in range(len(conv) - 1))

    def test_truncation_order(self):
        H = hamiltonian_from_terms(_TERMS)
        normHt = np.linalg.norm(H, 2) * 0.5
        K = taylor_truncation_order(normHt, 1e-6)
        assert taylor_error(H, 0.5, K) < 1e-6


class TestComplexity:
    def test_qdrift_crossover(self):
        assert qdrift_beats_trotter(50, 50.0, 5.0, 1.0, 0.001)

    def test_cheapest_method(self):
        H = hamiltonian_from_terms(_TERMS)
        normHt = np.linalg.norm(H, 2)
        assert cheapest_method(5, commutator_sum(_TERMS), 4.1, normHt, 1.0, 1e-8) == "taylor"

    def test_trotter_gate_count(self):
        assert trotter_first_order_gate_count(5, commutator_sum(_TERMS), 1.0, 0.01) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
