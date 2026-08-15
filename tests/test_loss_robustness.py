"""Tests for GHZ vs W robustness under particle loss."""

import numpy as np
import pytest

from quantum_debugger.algorithms import loss_robustness


class TestLossRobustness:
    @pytest.mark.parametrize("n", [3, 4, 5, 6])
    def test_ghz_loses_all_entanglement(self, n):
        assert loss_robustness(n)["ghz_pair_negativity"] < 1e-12

    @pytest.mark.parametrize("n", [3, 4, 5, 6])
    def test_w_matches_closed_form(self, n):
        r = loss_robustness(n)
        expected = (np.sqrt((n - 2) ** 2 + 4) - (n - 2)) / (2 * n)
        assert abs(r["w_pair_negativity"] - expected) < 1e-9
        assert r["w_pair_negativity"] > 0  # still entangled after the loss

    def test_w3_is_golden_value(self):
        # n = 3: negativity (sqrt(5) - 1) / 6.
        r = loss_robustness(3)
        assert abs(r["w_pair_negativity"] - (np.sqrt(5) - 1) / 6) < 1e-9

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_intact_ghz_is_maximally_entangled(self, n):
        assert abs(loss_robustness(n)["ghz_before_loss"] - 0.5) < 1e-9

    def test_w_entanglement_dilutes_with_n(self):
        vals = [loss_robustness(n)["w_pair_negativity"] for n in (3, 4, 5, 6)]
        assert all(b < a for a, b in zip(vals, vals[1:]))

    def test_small_n_rejected(self):
        with pytest.raises(ValueError):
            loss_robustness(2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
