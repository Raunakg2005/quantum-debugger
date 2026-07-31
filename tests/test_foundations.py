"""
Tests for the 2.5.0 foundations suite: CHSH Bell inequality and bounds, PR boxes and
no-signaling, multiparty Mermin inequalities, EPR steering, and device-independent
randomness. Classical bounds are checked by brute force, quantum values against closed
forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.bell_inequalities import (
    chsh_value, classical_chsh_bound, tsirelson_bound, algebraic_bound, chsh_violation,
    bell_state)
from quantum_debugger.algorithms.pr_box import (
    pr_box_correlations, chsh_from_box, is_no_signaling, local_deterministic_box,
    pr_box_is_superquantum)
from quantum_debugger.algorithms.mermin_multiparty import (
    mermin_optimal_value, mermin_quantum_bound, mermin_classical_bound, mermin_violation_ratio)
from quantum_debugger.algorithms.steering import (
    steering_value, is_steerable, werner_state, werner_steering_threshold)
from quantum_debugger.algorithms.device_independent import (
    guessing_probability, certified_randomness, is_randomness_certified, randomness_vs_violation)


class TestCHSH:
    def test_tsirelson(self):
        assert abs(chsh_value(bell_state("phi_plus")) - tsirelson_bound()) < 1e-9
        assert abs(tsirelson_bound() - 2 * np.sqrt(2)) < 1e-9

    def test_classical_bound(self):
        assert classical_chsh_bound() == 2 and algebraic_bound() == 4

    def test_violation(self):
        assert chsh_violation(bell_state("phi_plus")) > 0
        prod = np.array([1, 0, 0, 0], dtype=complex)
        assert abs(chsh_value(prod)) <= 2 + 1e-9


class TestPRBox:
    def test_pr_box(self):
        box = pr_box_correlations()
        assert abs(chsh_from_box(box) - 4) < 1e-9
        assert is_no_signaling(box) and pr_box_is_superquantum()

    def test_local_box(self):
        lb = local_deterministic_box(lambda x: 0, lambda y: 0)
        assert abs(chsh_from_box(lb)) <= 2 + 1e-9 and is_no_signaling(lb)


class TestMermin:
    def test_quantum_max(self):
        for n in (2, 3, 4, 5):
            assert abs(mermin_optimal_value(n) - 2 ** ((n - 1) / 2)) < 1e-6
            assert abs(mermin_optimal_value(n) - mermin_quantum_bound(n)) < 1e-6

    def test_classical_bound(self):
        for n in (2, 3, 4):
            assert abs(mermin_classical_bound(n) - 1) < 1e-6

    def test_exponential_violation(self):
        ratios = [mermin_violation_ratio(n) for n in (2, 3, 4, 5)]
        assert all(ratios[i] < ratios[i + 1] for i in range(3))


class TestSteering:
    def test_bell_steerable(self):
        bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rho = np.outer(bell, bell.conj())
        assert abs(steering_value(rho) - np.sqrt(3)) < 1e-9 and is_steerable(rho)

    def test_separable_not_steerable(self):
        assert not is_steerable(np.diag([1, 0, 0, 0]).astype(complex))

    def test_werner_threshold(self):
        pth = werner_steering_threshold()
        assert is_steerable(werner_state(pth + 0.02))
        assert not is_steerable(werner_state(pth - 0.02))


class TestDeviceIndependent:
    def test_endpoints(self):
        assert abs(guessing_probability(2.0) - 1) < 1e-9
        assert abs(guessing_probability(2 * np.sqrt(2)) - 0.5) < 1e-9
        assert abs(certified_randomness(2.0)) < 1e-9
        assert abs(certified_randomness(2 * np.sqrt(2)) - 1) < 1e-9

    def test_certification(self):
        assert is_randomness_certified(2.5) and not is_randomness_certified(2.0)

    def test_monotone(self):
        rv = randomness_vs_violation(np.linspace(2, 2 * np.sqrt(2), 5))
        assert all(rv[i] <= rv[i + 1] for i in range(4))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
