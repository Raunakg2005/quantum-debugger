"""Tests for spin squeezing (one-axis twisting)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import one_axis_twisting, best_squeezing


class TestOneAxisTwisting:
    @pytest.mark.parametrize("n", [3, 4, 6])
    def test_coherent_state_is_at_sql(self, n):
        # No twisting -> coherent spin state -> xi^2 = 1 exactly (standard quantum limit).
        assert abs(one_axis_twisting(n, 0.0) - 1.0) < 1e-9

    @pytest.mark.parametrize("n", [4, 6])
    def test_twisting_squeezes_below_sql(self, n):
        r = best_squeezing(n)
        assert r["best_xi2"] < 1.0
        assert r["best_xi2"] < 0.9  # meaningfully squeezed

    def test_squeezing_improves_with_atom_number(self):
        xis = [best_squeezing(n)["best_xi2"] for n in (4, 6, 8)]
        assert all(b < a for a, b in zip(xis, xis[1:]))


class TestBestSqueezing:
    def test_reports_sql_and_gain(self):
        r = best_squeezing(6)
        assert abs(r["sql"] - 1.0) < 1e-9
        assert r["metrological_gain"] > 1.0  # beats the SQL
        assert r["squeezing_dB"] < 0  # negative dB = squeezed
        assert 0 < r["best_chi_t"]  # squeezing needs finite twisting

    def test_gain_matches_xi2(self):
        r = best_squeezing(6)
        assert abs(r["metrological_gain"] - 1 / r["best_xi2"]) < 1e-9

    def test_dB_consistent(self):
        r = best_squeezing(8)
        assert abs(r["squeezing_dB"] - 10 * np.log10(r["best_xi2"])) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
