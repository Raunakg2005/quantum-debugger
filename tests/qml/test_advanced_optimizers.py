"""
Tests for advanced optimizers
"""

import pytest
import numpy as np
from quantum_debugger.qml.optimizers.advanced import (
    QuantumNaturalGradient,
    NelderMeadOptimizer,
    LBFGSBOptimizer,
    COBYLAOptimizer,
    get_optimizer,
    compare_optimizers,
)


class TestQuantumNaturalGradient:
    """Test Quantum Natural Gradient optimizer"""

    def test_initialization(self):
        """Test QNG initialization"""
        qng = QuantumNaturalGradient(learning_rate=0.1)

        assert qng.learning_rate == 0.1
        assert qng.epsilon > 0

    def test_step_without_circuit(self):
        """Test QNG step without circuit (falls back to gradient descent)"""
        qng = QuantumNaturalGradient(learning_rate=0.1)
        params = np.array([1.0, 2.0, 3.0])
        gradient = np.array([0.1, -0.2, 0.3])

        new_params = qng.step(params, gradient)

        # Should move in negative gradient direction
        assert len(new_params) == 3
        assert new_params[0] < params[0]  # Gradient positive, so decrease
        assert new_params[1] > params[1]  # Gradient negative, so increase

    def test_metric_tensor_shape(self):
        """Test metric tensor has correct shape"""
        qng = QuantumNaturalGradient()
        params = np.array([0.5, 1.0, 1.5])

        def dummy_circuit(p):
            return None

        metric = qng.compute_metric_tensor(dummy_circuit, params)

        assert metric.shape == (3, 3)
        assert np.all(np.isfinite(metric))


class TestNelderMeadOptimizer:
    """Test Nelder-Mead optimizer"""

    def test_initialization(self):
        """Test NM initialization"""
        nm = NelderMeadOptimizer(max_iterations=500)

        assert nm.max_iterations == 500

    def test_simple_quadratic(self):
        """Test on simple quadratic function"""

        def quadratic(x):
            return (x[0] - 3) ** 2 + (x[1] + 2) ** 2

        nm = NelderMeadOptimizer(max_iterations=1000, tolerance=1e-6)
        result = nm.minimize(quadratic, np.array([0.0, 0.0]))

        # Should find minimum at (3, -2)
        assert result["success"]
        np.testing.assert_array_almost_equal(result["params"], [3, -2], decimal=3)
        assert result["cost"] < 1e-5

    def test_rosenbrock(self):
        """Test on Rosenbrock function"""

        def rosenbrock(x):
            return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2

        nm = NelderMeadOptimizer(max_iterations=5000)
        result = nm.minimize(rosenbrock, np.array([0.0, 0.0]))

        # Rosenbrock minimum is at (1, 1)
        assert result["cost"] < 0.1  # May not converge perfectly

    def test_returns_dict(self):
        """Test that result is a dictionary with expected keys"""

        def simple_fn(x):
            return np.sum(x**2)

        nm = NelderMeadOptimizer()
        result = nm.minimize(simple_fn, np.array([1.0, 2.0]))

        assert "params" in result
        assert "cost" in result
        assert "success" in result


class TestLBFGSBOptimizer:
    """Test L-BFGS-B optimizer"""

    def test_initialization(self):
        """Test L-BFGS-B initialization"""
        lbfgs = LBFGSBOptimizer(max_iterations=100)

        assert lbfgs.max_iterations == 100

    def test_simple_optimization(self):
        """Test on simple function"""

        def quadratic(x):
            return x[0] ** 2 + 2 * x[1] ** 2 + x[0] * x[1]

        lbfgs = LBFGSBOptimizer(max_iterations=1000)
        result = lbfgs.minimize(quadratic, np.array([5.0, 5.0]))

        assert result["success"]
        # Minimum at origin
        np.testing.assert_array_almost_equal(result["params"], [0, 0], decimal=5)

    def test_with_bounds(self):
        """Test with parameter bounds"""

        def fn(x):
            return (x[0] - 5) ** 2  # Minimum at x=5

        # But constrain to [0, 3]
        lbfgs = LBFGSBOptimizer(bounds=[(0, 3)])
        result = lbfgs.minimize(fn, np.array([0.0]))

        # Should find boundary minimum at x=3
        assert result["success"]
        assert 2.9 <= result["params"][0] <= 3.1

    def test_gradient_function(self):
        """Test with explicit gradient"""

        def fn(x):
            return x[0] ** 2 + x[1] ** 2

        def grad(x):
            return np.array([2 * x[0], 2 * x[1]])

        lbfgs = LBFGSBOptimizer()
        result = lbfgs.minimize(fn, np.array([10.0, -5.0]), gradient_function=grad)

        assert result["success"]
        np.testing.assert_array_almost_equal(result["params"], [0, 0], decimal=5)


class TestCOBYLAOptimizer:
    """Test COBYLA optimizer"""

    def test_initialization(self):
        """Test COBYLA initialization"""
        cobyla = COBYLAOptimizer(max_iterations=100)

        assert cobyla.max_iterations == 100

    def test_simple_optimization(self):
        """Test basic optimization"""

        def fn(x):
            return x[0] ** 2 + x[1] ** 2

        cobyla = COBYLAOptimizer()
        result = cobyla.minimize(fn, np.array([5.0, -3.0]))

        # Should find minimum near origin
        assert result["cost"] < 0.1


class TestFactoryFunction:
    """Test optimizer factory function"""

    def test_get_qng(self):
        """Test getting QNG optimizer"""
        opt = get_optimizer("qng", learning_rate=0.05)

        assert isinstance(opt, QuantumNaturalGradient)
        assert opt.learning_rate == 0.05

    def test_get_nelder_mead(self):
        """Test getting Nelder-Mead"""
        opt = get_optimizer("nelder-mead", max_iterations=500)

        assert isinstance(opt, NelderMeadOptimizer)
        assert opt.max_iterations == 500

    def test_get_lbfgs(self):
        """Test getting L-BFGS-B"""
        opt = get_optimizer("lbfgs", tolerance=1e-8)

        assert isinstance(opt, LBFGSBOptimizer)
        assert opt.tolerance == 1e-8

    def test_case_insensitive(self):
        """Test case insensitivity"""
        opt1 = get_optimizer("LBFGS")
        opt2 = get_optimizer("lbfgs")
        opt3 = get_optimizer("L-BFGS-B")

        assert isinstance(opt1, LBFGSBOptimizer)
        assert isinstance(opt2, LBFGSBOptimizer)
        assert isinstance(opt3, LBFGSBOptimizer)

    def test_invalid_optimizer(self):
        """Test error for invalid optimizer"""
        with pytest.raises(ValueError, match="Unknown optimizer"):
            get_optimizer("invalid_optimizer")


class TestCompareOptimizers:
    """Test optimizer comparison utility"""

    def test_compare_multiple(self):
        """Test comparing multiple optimizers"""

        def quadratic(x):
            return x[0] ** 2 + x[1] ** 2

        results = compare_optimizers(
            quadratic, np.array([5.0, 5.0]), ["nelder-mead", "lbfgs"]
        )

        assert "nelder-mead" in results
        assert "lbfgs" in results
        assert all("params" in r or "error" in r for r in results.values())

    def test_handles_errors(self):
        """Test that errors are caught and reported"""

        def bad_function(x):
            raise ValueError("Intentional error")

        results = compare_optimizers(bad_function, np.array([1.0]), ["nelder-mead"])

        assert "error" in results["nelder-mead"]


class TestOptimizationBehavior:
    """Test optimization behavior and convergence"""

    def test_nm_vs_lbfgs_convergence(self):
        """Compare Nelder-Mead vs L-BFGS-B convergence"""

        def fn(x):
            return (x[0] - 2) ** 2 + (x[1] + 3) ** 2

        nm = NelderMeadOptimizer(max_iterations=1000)
        lbfgs = LBFGSBOptimizer(max_iterations=100)

        nm_result = nm.minimize(fn, np.array([0.0, 0.0]))
        lbfgs_result = lbfgs.minimize(fn, np.array([0.0, 0.0]))

        # Both should find minimum
        assert nm_result["cost"] < 0.01
        assert lbfgs_result["cost"] < 0.01

        # L-BFGS-B usually faster
        assert lbfgs_result["iterations"] < nm_result["iterations"]

    def test_all_optimizers_on_same_problem(self):
        """Test all optimizers on same problem"""

        def sphere(x):
            return np.sum(x**2)

        initial = np.array([10.0, -5.0, 3.0])

        optimizers = {
            "nelder-mead": NelderMeadOptimizer(),
            "lbfgs": LBFGSBOptimizer(),
            "cobyla": COBYLAOptimizer(),
        }

        for name, opt in optimizers.items():
            result = opt.minimize(sphere, initial.copy())
            assert result["cost"] < 1.0, f"{name} failed to converge"
