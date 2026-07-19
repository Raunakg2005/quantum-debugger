"""Tests for the SPSA optimizer."""

import numpy as np
import pytest

from quantum_debugger.qml.optimizers import SPSA


class TestSPSA:
    def test_minimizes_quadratic(self):
        opt = SPSA(a=0.3, c=0.1, maxiter=300, seed=0)
        result = opt.minimize(lambda x: (x[0] - 3) ** 2 + (x[1] + 1) ** 2, [0.0, 0.0])
        assert np.allclose(result["x"], [3.0, -1.0], atol=0.2)
        assert result["fun"] < 0.05

    def test_step_is_two_evaluations(self):
        calls = {"n": 0}

        def obj(x):
            calls["n"] += 1
            return float(np.sum(x**2))

        opt = SPSA(seed=1)
        opt.step(obj, np.array([1.0, 2.0, 3.0, 4.0]), k=0)
        assert calls["n"] == 2  # SPSA uses exactly two evaluations per step

    def test_history_recorded(self):
        opt = SPSA(maxiter=20, seed=2)
        result = opt.minimize(lambda x: float(np.sum((x - 1) ** 2)), np.zeros(3))
        assert len(result["history"]) == 21  # initial + one per iteration
        assert result["fun"] <= result["history"][0]

    def test_higher_dimensions(self):
        # SPSA cost is independent of dimension: still 2 evals/step.
        opt = SPSA(a=0.2, c=0.1, maxiter=200, seed=3)
        d = 10
        target = np.arange(d) * 0.1
        result = opt.minimize(lambda x: float(np.sum((x - target) ** 2)), np.zeros(d))
        assert result["fun"] < 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
