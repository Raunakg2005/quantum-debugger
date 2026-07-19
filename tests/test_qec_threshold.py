"""Tests for the repetition-code logical error rate."""

import pytest

from quantum_debugger.algorithms import repetition_code_error_rate


class TestRepetitionCode:
    @pytest.mark.parametrize("p", [0.02, 0.05, 0.1, 0.2])
    def test_matches_analytic(self, p):
        r = repetition_code_error_rate(p, trials=8000, seed=1)
        # Monte-Carlo estimate close to 3p^2(1-p)+p^3.
        assert abs(r["logical_error_rate"] - r["analytic_rate"]) < 0.02

    @pytest.mark.parametrize("p", [0.02, 0.05, 0.1, 0.2, 0.4])
    def test_below_physical_under_threshold(self, p):
        r = repetition_code_error_rate(p, trials=8000, seed=2)
        assert r["below_physical"]

    def test_no_noise_never_fails(self):
        r = repetition_code_error_rate(0.0, trials=1000, seed=0)
        assert r["logical_error_rate"] == 0.0

    def test_at_threshold_no_benefit(self):
        # At p = 1/2 the code no longer helps: logical rate ~ physical rate = 0.5.
        r = repetition_code_error_rate(0.5, trials=8000, seed=3)
        assert abs(r["logical_error_rate"] - 0.5) < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
