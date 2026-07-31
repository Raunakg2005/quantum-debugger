"""
Tests for the 2.2.0 variational-algorithms suite: parameter-shift gradients, barren
plateaus, expressibility, entangling capability, and the quantum geometric tensor /
natural gradient. Verified against finite differences and closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.variational_ansatz import (
    hardware_efficient_ansatz, ansatz_num_params, z_observable, ansatz_expectation,
    random_parameters)
from quantum_debugger.algorithms.parameter_shift import (
    parameter_shift_gradient_all, finite_difference_gradient,
    parameter_shift_hessian_diagonal, gradient_norm)
from quantum_debugger.algorithms.barren_plateaus import (
    barren_plateau_scaling, cost_concentration)
from quantum_debugger.algorithms.expressibility import (
    haar_fidelity_pdf, haar_mean_fidelity, frame_potential, expressibility_kl)
from quantum_debugger.algorithms.entangling_capability import (
    meyer_wallach, entangling_capability, is_product_state)
from quantum_debugger.algorithms.quantum_natural_gradient import (
    quantum_geometric_tensor, quantum_fisher_matrix, is_positive_semidefinite,
    natural_gradient, fubini_study_distance, effective_quantum_dimension)


def _cost(n=3, layers=2):
    obs = z_observable(n)
    return lambda p: ansatz_expectation(p, n, layers, obs)


class TestParameterShift:
    def test_gradient_matches_fd(self):
        n, layers = 3, 2
        params = random_parameters(n, layers, 0)
        cost = _cost(n, layers)
        assert np.allclose(parameter_shift_gradient_all(cost, params),
                           finite_difference_gradient(cost, params), atol=1e-5)

    def test_hessian_matches_fd(self):
        n, layers = 3, 2
        params = random_parameters(n, layers, 1)
        cost = _cost(n, layers)
        h = parameter_shift_hessian_diagonal(cost, params)

        def fd(i, eps=1e-4):
            p = params.copy(); p[i] += eps; pp = cost(p)
            p = params.copy(); p[i] -= eps; pm = cost(p)
            return (pp - 2 * cost(params) + pm) / eps**2
        assert np.allclose(h, [fd(i) for i in range(len(params))], atol=1e-3)

    def test_gradient_norm(self):
        assert gradient_norm(_cost(), random_parameters(3, 2, 2)) >= 0


class TestBarrenPlateaus:
    def test_onset(self):
        sc = barren_plateau_scaling([2, 3, 4, 5], layers=8, samples=400)
        assert sc[2] > sc[5]                      # gradient variance shrinks with n

    def test_cost_concentration(self):
        cc = {n: cost_concentration(n, 8, samples=400) for n in (2, 5)}
        assert cc[2] > cc[5]


class TestExpressibility:
    def test_haar_pdf(self):
        xs = np.linspace(0, 1, 10000)
        assert abs(np.trapezoid(haar_fidelity_pdf(xs, 8), xs) - 1) < 1e-2

    def test_frame_potential(self):
        assert abs(frame_potential(3, 6) - haar_mean_fidelity(8)) < 0.05

    def test_deeper_more_expressive(self):
        assert expressibility_kl(3, 5, samples=3000) < expressibility_kl(3, 1, samples=3000)


class TestEntangling:
    def test_meyer_wallach(self):
        prod = np.zeros(8, dtype=complex); prod[0] = 1
        ghz = np.zeros(8, dtype=complex); ghz[0] = ghz[7] = 1 / np.sqrt(2)
        assert meyer_wallach(prod) < 1e-9 and abs(meyer_wallach(ghz) - 1) < 1e-9
        assert is_product_state(prod) and not is_product_state(ghz)

    def test_capability_grows(self):
        assert entangling_capability(3, 3) > entangling_capability(3, 1)


class TestNaturalGradient:
    def test_metric_psd(self):
        g = quantum_geometric_tensor(random_parameters(3, 2, 0), 3, 2)
        assert is_positive_semidefinite(g)

    def test_fisher_is_four_g(self):
        p = random_parameters(3, 2, 1)
        assert np.allclose(quantum_fisher_matrix(p, 3, 2), 4 * quantum_geometric_tensor(p, 3, 2))

    def test_natural_gradient_identity(self):
        grad = np.random.default_rng(2).normal(size=6)
        assert np.allclose(natural_gradient(grad, np.eye(6)), grad, atol=1e-5)

    def test_fubini_study_and_dimension(self):
        prod = np.zeros(8, dtype=complex); prod[0] = 1
        ghz = np.zeros(8, dtype=complex); ghz[0] = ghz[7] = 1 / np.sqrt(2)
        assert abs(fubini_study_distance(prod, ghz) - np.pi / 4) < 1e-9
        g = quantum_geometric_tensor(random_parameters(3, 2, 3), 3, 2)
        assert 0 <= effective_quantum_dimension(g) <= 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
