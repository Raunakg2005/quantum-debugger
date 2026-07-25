"""Tests for the Hahn spin echo (dynamical decoupling)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import spin_echo, echo_state_fidelity


class TestStaticNoise:
    @pytest.mark.parametrize("sigma", [0.3, 0.8, 1.5, 3.0])
    def test_no_echo_decays_as_closed_form(self, sigma):
        r = spin_echo(sigma, static=True)
        assert abs(r["no_echo"] - np.exp(-(sigma**2) / 2)) < 1e-9

    @pytest.mark.parametrize("sigma", [0.3, 0.8, 1.5, 3.0])
    def test_echo_restores_coherence_exactly(self, sigma):
        r = spin_echo(sigma, static=True)
        assert abs(r["echo"] - 1.0) < 1e-9

    def test_echo_beats_free_evolution(self):
        r = spin_echo(1.0, static=True)
        assert r["echo"] > r["no_echo"]

    def test_zero_noise_trivial(self):
        r = spin_echo(0.0, static=True)
        assert abs(r["no_echo"] - 1.0) < 1e-12
        assert abs(r["echo"] - 1.0) < 1e-12


class TestFastNoise:
    @pytest.mark.parametrize("sigma", [0.5, 1.0, 2.0])
    def test_echo_gives_no_advantage(self, sigma):
        # Uncorrelated noise: the echo decays exactly like free evolution.
        r = spin_echo(sigma, static=False)
        expected = np.exp(-(sigma**2) / 2)
        assert abs(r["no_echo"] - expected) < 1e-9
        assert abs(r["echo"] - expected) < 1e-9

    def test_correlation_is_the_resource(self):
        # Same sigma: echo works iff the noise is correlated across the shot.
        sigma = 1.2
        assert abs(spin_echo(sigma, static=True)["echo"] - 1.0) < 1e-9
        assert spin_echo(sigma, static=False)["echo"] < 0.5


class TestEchoStateFidelity:
    @pytest.mark.parametrize("a,b", [(1, 0), (1, 1), (0.6, 0.8j), (1, -1j)])
    def test_arbitrary_states_protected(self, a, b):
        assert abs(echo_state_fidelity(1.5, a, b) - 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
