"""Tests for entanglement growth after a quench."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    entanglement_growth,
    hamiltonian_matrix,
    tfim_hamiltonian,
    heisenberg_hamiltonian,
)


def _hbin(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


class TestAnalyticTwoQubit:
    def test_xx_coupling_matches_binary_entropy(self):
        g = 1.0
        H = g * hamiltonian_matrix([(1.0, "XX")], 2)
        psi0 = np.array([1, 0, 0, 0], dtype=complex)  # |00>
        times = np.linspace(0, 3, 25)
        r = entanglement_growth(H, psi0, [0], times)
        analytic = np.array([_hbin(np.sin(g * t) ** 2) for t in times])
        assert np.allclose(r["entropy"], analytic, atol=1e-9)

    def test_reaches_one_bit_at_quarter_period(self):
        # At g t = pi/4, sin^2 = 1/2 -> maximal entanglement (1 bit).
        H = hamiltonian_matrix([(1.0, "XX")], 2)
        r = entanglement_growth(
            H, np.array([1, 0, 0, 0], dtype=complex), [0], [np.pi / 4]
        )
        assert abs(r["entropy"][0] - 1.0) < 1e-9


class TestQuenchGrowth:
    def test_product_state_starts_at_zero(self):
        n = 6
        H = hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 1.0), n)
        psi0 = np.zeros(2**n, dtype=complex)
        psi0[0] = 1
        r = entanglement_growth(H, psi0, [0, 1, 2], np.linspace(0, 8, 40))
        assert abs(r["initial"]) < 1e-9

    def test_entropy_grows_then_saturates(self):
        n = 6
        H = hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 1.0), n)
        psi0 = np.zeros(2**n, dtype=complex)
        psi0[0] = 1
        r = entanglement_growth(H, psi0, [0, 1, 2], np.linspace(0, 10, 60))
        assert r["saturation"] > 0.5  # grew substantially
        assert r["saturation"] <= r["max_entropy"] + 1e-9  # bounded by volume law

    def test_never_exceeds_bound(self):
        n = 6
        H = hamiltonian_matrix(heisenberg_hamiltonian(n), n)
        psi0 = np.zeros(2**n, dtype=complex)
        psi0[0b010101] = 1  # Neel-like product state
        r = entanglement_growth(H, psi0, [0, 1, 2], np.linspace(0, 6, 40))
        assert np.all(r["entropy"] <= r["max_entropy"] + 1e-9)

    def test_eigenstate_has_static_entropy(self):
        # An energy eigenstate does not change its entanglement over time.
        n = 4
        H = hamiltonian_matrix(tfim_hamiltonian(n, 1.0, 0.7), n)
        _, vecs = np.linalg.eigh(H)
        r = entanglement_growth(H, vecs[:, 0], [0, 1], np.linspace(0, 5, 20))
        assert np.allclose(r["entropy"], r["entropy"][0], atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
