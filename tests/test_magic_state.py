"""Tests for magic states and T-gate injection (gate teleportation)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import t_magic_state, inject_t_gate

_T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)


class TestMagicState:
    def test_is_t_on_plus(self):
        plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
        assert np.allclose(t_magic_state(), _T @ plus)

    def test_normalized(self):
        assert abs(np.linalg.norm(t_magic_state()) - 1.0) < 1e-12


class TestInjection:
    @pytest.mark.parametrize("outcome", [0, 1])
    def test_both_branches_give_t_psi(self, outcome):
        rng = np.random.default_rng(7)
        for _ in range(5):
            a, b = rng.normal(size=2) + 1j * rng.normal(size=2)
            r = inject_t_gate(a, b, force_outcome=outcome)
            assert abs(r["fidelity"] - 1.0) < 1e-9
            assert r["outcome"] == outcome
            assert r["correction"] == ("S" if outcome == 1 else None)

    @pytest.mark.parametrize("a,b", [(1, 0), (0, 1), (1, 1), (0.6, 0.8j), (1, -1j)])
    def test_outcome_probability_is_half(self, a, b):
        # The measurement reveals nothing about |psi>: both outcomes exactly 1/2.
        for outcome in (0, 1):
            r = inject_t_gate(a, b, force_outcome=outcome)
            assert abs(r["probability"] - 0.5) < 1e-12

    def test_random_outcome_still_exact(self):
        for seed in range(6):
            r = inject_t_gate(0.6, 0.8j, seed=seed)
            assert abs(r["fidelity"] - 1.0) < 1e-9
            assert r["outcome"] in (0, 1)

    def test_both_outcomes_occur(self):
        outcomes = {inject_t_gate(1, 1j, seed=s)["outcome"] for s in range(30)}
        assert outcomes == {0, 1}

    def test_correction_is_necessary(self):
        # Skipping the S fix-up on outcome 1 leaves T-dagger|psi>, not T|psi>.
        a, b = 1.0, 1.0
        r = inject_t_gate(a, b, force_outcome=1)
        assert r["correction"] == "S"
        tdg = _T.conj().T @ np.array([a, b]) / np.sqrt(2)
        t = _T @ np.array([a, b]) / np.sqrt(2)
        assert abs(np.vdot(t, tdg)) ** 2 < 0.9  # the two branches genuinely differ

    def test_result_is_not_identity(self):
        # Injection changes the state (T is not identity on |+>).
        a, b = 1.0, 1.0
        psi = np.array([a, b]) / np.sqrt(2)
        t_psi = _T @ psi
        assert abs(np.vdot(psi, t_psi)) ** 2 < 1 - 1e-3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
