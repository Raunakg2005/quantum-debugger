"""Tests for quantum metrology (GHZ Heisenberg-limited phase sensing)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    phase_sensitivity,
    parity_signal,
    quantum_fisher_information,
)
from quantum_debugger.algorithms.metrology import product_probe
from quantum_debugger.algorithms import ghz_state


class TestQFI:
    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
    def test_ghz_is_heisenberg(self, n):
        qfi = quantum_fisher_information(ghz_state(n).astype(complex), n)
        assert np.isclose(qfi, n**2)

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
    def test_product_is_sql(self, n):
        qfi = quantum_fisher_information(product_probe(n), n)
        assert np.isclose(qfi, n)


class TestPhaseSensitivity:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_advantage_is_n(self, n):
        r = phase_sensitivity(n)
        assert np.isclose(r["advantage"], n)
        assert np.isclose(r["delta_phi_ghz"], 1 / n)
        assert np.isclose(r["delta_phi_product"], 1 / np.sqrt(n))


class TestParitySignal:
    def test_oscillates_as_cos_n_phi(self):
        n = 4
        for phi in np.linspace(0, np.pi, 7):
            assert np.isclose(parity_signal(n, phi), np.cos(n * phi), atol=1e-9)

    def test_faster_than_single_qubit(self):
        # GHZ parity completes a full period in phi = 2pi/n.
        n = 3
        assert np.isclose(parity_signal(n, 2 * np.pi / n), 1.0, atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
