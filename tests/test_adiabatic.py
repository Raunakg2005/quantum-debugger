"""Tests for adiabatic quantum computation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import adiabatic_evolution, hamiltonian_matrix


def _driver(n):
    # H_initial = -sum X, ground state |+...+>.
    return hamiltonian_matrix(
        [(-1.0, "".join("X" if i == q else "I" for i in range(n))) for q in range(n)], n
    )


def _problem(n):
    # Ferromagnet + small longitudinal field -> unique ground state |0...0>.
    zz = [
        (-1.0, "".join("Z" if i in (q, q + 1) else "I" for i in range(n)))
        for q in range(n - 1)
    ]
    z = [(-0.3, "".join("Z" if i == q else "I" for i in range(n))) for q in range(n)]
    return hamiltonian_matrix(zz + z, n)


class TestAdiabaticTheorem:
    def test_slow_evolution_succeeds(self):
        r = adiabatic_evolution(_driver(3), _problem(3), total_time=50.0)
        assert r["fidelity"] > 0.99
        assert r["adiabatic"]
        assert abs(r["final_energy"] - r["target_energy"]) < 0.05

    def test_fast_evolution_fails(self):
        r = adiabatic_evolution(_driver(3), _problem(3), total_time=0.5)
        assert r["fidelity"] < 0.5
        assert not r["adiabatic"]

    def test_fidelity_monotone_in_time(self):
        fids = [
            adiabatic_evolution(_driver(3), _problem(3), total_time=T)["fidelity"]
            for T in (0.5, 2, 5, 20, 50)
        ]
        assert all(b > a - 1e-6 for a, b in zip(fids, fids[1:]))

    def test_reports_min_gap(self):
        r = adiabatic_evolution(_driver(3), _problem(3), total_time=10.0)
        assert r["min_gap"] > 0  # gapped path -> adiabatic possible

    def test_trivial_when_initial_equals_final(self):
        # If driver == problem, any speed stays in the ground state.
        H = _problem(2)
        r = adiabatic_evolution(H, H, total_time=0.3)
        assert r["fidelity"] > 1 - 1e-9

    def test_final_state_normalized(self):
        r = adiabatic_evolution(_driver(2), _problem(2), total_time=5.0)
        assert r["fidelity"] <= 1.0 + 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
