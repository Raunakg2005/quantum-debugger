"""Tests for the Bell / CHSH inequality test."""

import numpy as np
import pytest

from quantum_debugger.algorithms import chsh_value, correlator, bell_state, chsh_game


class TestBellState:
    def test_bell_state_amplitudes(self):
        sv = bell_state()
        expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        assert np.allclose(sv, expected)


class TestCorrelator:
    def test_equals_cos_difference(self):
        psi = bell_state()
        for a in np.linspace(0, np.pi, 5):
            for b in np.linspace(0, np.pi, 5):
                assert np.isclose(correlator(psi, a, b), np.cos(a - b), atol=1e-9)


class TestCHSH:
    def test_reaches_tsirelson_bound(self):
        r = chsh_value()  # default optimal angles
        assert np.isclose(abs(r["S"]), 2 * np.sqrt(2), atol=1e-9)
        assert r["violates_classical"]

    def test_classical_bound_reported(self):
        r = chsh_value()
        assert r["classical_bound"] == 2.0
        assert np.isclose(r["tsirelson_bound"], 2 * np.sqrt(2))

    def test_aligned_angles_do_not_violate(self):
        # All-equal angles give S = 2 (no violation).
        r = chsh_value(a=0.0, a_prime=0.0, b=0.0, b_prime=0.0)
        assert abs(r["S"]) <= 2.0 + 1e-9
        assert not r["violates_classical"]


class TestCHSHGame:
    def test_quantum_beats_classical(self):
        r = chsh_game()
        assert np.isclose(r["quantum_win_probability"], np.cos(np.pi / 8) ** 2)
        assert r["quantum_win_probability"] > 0.75
        assert r["beats_classical"]
        assert r["classical_win_probability"] == 0.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
