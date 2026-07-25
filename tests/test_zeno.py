"""Tests for the quantum Zeno effect."""

import numpy as np
import pytest

from quantum_debugger.algorithms import quantum_zeno, zeno_postselected


class TestUnreadZeno:
    @pytest.mark.parametrize("n", [1, 2, 5, 10, 50])
    def test_matches_closed_form(self, n):
        r = quantum_zeno(np.pi / 2, n)
        assert abs(r["survival"] - r["analytic"]) < 1e-9

    def test_freezing_improves_with_n(self):
        omega_t = np.pi / 2
        survivals = [quantum_zeno(omega_t, n)["survival"] for n in (1, 2, 4, 16, 64)]
        assert all(b > a for a, b in zip(survivals, survivals[1:]))

    def test_limit_is_one(self):
        r = quantum_zeno(np.pi / 2, 2000)
        assert r["survival"] > 0.999

    def test_beats_free_evolution(self):
        # Free pi-pulse fully inverts (survival 0); frequent measurement stops it.
        r = quantum_zeno(np.pi, 50)
        assert abs(r["free_survival"]) < 1e-12
        assert r["survival"] > 0.95
        assert r["frozen"]

    def test_invalid_n_rejected(self):
        with pytest.raises(ValueError):
            quantum_zeno(np.pi, 0)


class TestPostselectedZeno:
    @pytest.mark.parametrize("n", [1, 3, 10, 100])
    def test_matches_closed_form(self, n):
        r = zeno_postselected(np.pi / 2, n)
        assert abs(r["survival_probability"] - r["analytic"]) < 1e-9

    def test_surviving_state_is_zero(self):
        r = zeno_postselected(np.pi / 2, 7)
        assert abs(r["state_fidelity"] - 1.0) < 1e-9

    def test_probability_tends_to_one(self):
        p_small = zeno_postselected(np.pi, 2)["survival_probability"]
        p_large = zeno_postselected(np.pi, 500)["survival_probability"]
        assert p_large > 0.995 > p_small

    def test_single_measurement_pi_pulse_never_survives(self):
        # One check after a full pi pulse: cos^2(pi/2) = 0... but with N=1 the
        # measurement happens after the whole rotation, so survival is ~0.
        r = zeno_postselected(np.pi, 1)
        assert r["survival_probability"] < 1e-12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
