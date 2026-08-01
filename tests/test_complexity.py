"""
Tests for the 3.0.0 quantum-complexity milestone: Boolean-function complexity measures and
their hierarchy, Fourier analysis on the cube, query separations, communication complexity,
and the complexity-class containment order. Verified by brute force and closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.boolean_complexity import (
    truth_table, max_sensitivity, block_sensitivity, certificate_complexity,
    decision_tree_complexity, polynomial_degree, sensitivity_hierarchy_holds)
from quantum_debugger.algorithms.fourier_analysis import (
    fourier_coefficients, parseval, influence, total_influence, noise_stability, degree_from_fourier)
from quantum_debugger.algorithms.query_complexity import (
    deutsch_jozsa_queries, simon_queries, grover_queries, parity_queries, quantum_speedup,
    polynomial_method_bound, is_exponential_separation, grover_is_optimal)
from quantum_debugger.algorithms.communication_complexity import (
    equality_deterministic, quantum_fingerprint_length, inner_product_complexity,
    disjointness_complexity, equality_exponential_saving, has_quantum_advantage)
from quantum_debugger.algorithms.complexity_classes import (
    contains, problem_class, in_bqp, is_open_separation, hierarchy_is_consistent)

_OR = lambda b: int(any(b))
_PARITY = lambda b: sum(b) % 2
_MAJ = lambda b: int(sum(b) > len(b) / 2)


class TestBooleanComplexity:
    def test_or_measures(self):
        tt = truth_table(_OR, 3)
        assert max_sensitivity(tt, 3) == 3 and polynomial_degree(tt, 3) == 3

    def test_majority(self):
        tt = truth_table(_MAJ, 3)
        assert max_sensitivity(tt, 3) == 2 and block_sensitivity(tt, 3) == 2
        assert certificate_complexity(tt, 3) == 2 and decision_tree_complexity(tt, 3) == 3

    def test_hierarchy(self):
        for f in (_OR, _PARITY, _MAJ):
            assert sensitivity_hierarchy_holds(truth_table(f, 3), 3)


class TestFourier:
    def test_parseval(self):
        for f in (_OR, _PARITY, _MAJ):
            assert abs(parseval(truth_table(f, 3), 3) - 1) < 1e-9

    def test_influences(self):
        assert abs(total_influence(truth_table(_PARITY, 3), 3) - 3) < 1e-9
        assert abs(total_influence(truth_table(lambda b: b[0], 3), 3) - 1) < 1e-9

    def test_noise_and_degree(self):
        tt = truth_table(_MAJ, 3)
        assert abs(noise_stability(tt, 3, 1.0) - 1) < 1e-9
        assert degree_from_fourier(tt, 3) == polynomial_degree(tt, 3)


class TestQuery:
    def test_separations(self):
        assert is_exponential_separation(deutsch_jozsa_queries)
        assert is_exponential_separation(simon_queries)
        assert not is_exponential_separation(parity_queries)

    def test_grover(self):
        assert grover_is_optimal(1024, grover_queries(1024)["quantum"])
        assert quantum_speedup(parity_queries(8)) == 2

    def test_polynomial_method(self):
        assert polynomial_method_bound(6) == 3.0


class TestCommunication:
    def test_equality(self):
        assert quantum_fingerprint_length(64) < equality_deterministic(64)
        assert equality_exponential_saving(64)

    def test_advantages(self):
        assert not has_quantum_advantage(inner_product_complexity(64))
        assert has_quantum_advantage(disjointness_complexity(64))


class TestClasses:
    def test_containments(self):
        assert contains("PSPACE", "BQP") and contains("BQP", "BPP")
        assert not contains("BQP", "NP")           # open

    def test_problems(self):
        assert in_bqp("factoring") and in_bqp("sorting")
        assert problem_class("sat") == "NP"

    def test_open_and_consistent(self):
        assert is_open_separation("BQP", "NP")
        assert not is_open_separation("BPP", "BQP")   # BPP ⊆ BQP proven
        assert hierarchy_is_consistent()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
