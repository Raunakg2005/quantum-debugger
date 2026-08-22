"""Tests for the Jordan-Wigner transformation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    jw_annihilation,
    jw_creation,
    jw_number,
    jw_total_number,
    hopping_hamiltonian,
    anticommutation_error,
)


class TestAnticommutation:
    @pytest.mark.parametrize("n", [1, 2, 3, 4])
    def test_fermionic_algebra_exact(self, n):
        assert anticommutation_error(n) < 1e-12

    def test_annihilation_kills_vacuum(self):
        # a_j |0...0> = 0.
        n = 3
        vac = np.zeros(2**n, dtype=complex)
        vac[0] = 1
        for j in range(n):
            assert np.allclose(jw_annihilation(j, n) @ vac, 0, atol=1e-12)

    def test_double_occupation_forbidden(self):
        # (a_j-dagger)^2 = 0 (Pauli exclusion).
        n = 3
        for j in range(n):
            ad = jw_creation(j, n)
            assert np.allclose(ad @ ad, 0, atol=1e-12)


class TestNumberOperator:
    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_eigenvalues_zero_one(self, n):
        for j in range(n):
            ev = np.linalg.eigvalsh(jw_number(j, n)).real
            assert np.allclose(np.unique(np.round(ev, 9)), [0, 1])

    def test_total_number_counts_occupation(self):
        n = 4
        N = jw_total_number(n)
        for state in (0b0000, 0b0110, 0b1111, 0b1010):
            assert abs(np.real(N[state, state]) - bin(state).count("1")) < 1e-12

    def test_number_is_projector(self):
        n = 3
        for j in range(n):
            nj = jw_number(j, n)
            assert np.allclose(nj @ nj, nj, atol=1e-12)


class TestHoppingHamiltonian:
    def test_hermitian(self):
        H = hopping_hamiltonian(4, t=1.3)
        assert np.allclose(H, H.conj().T)

    def test_open_chain_band(self):
        n, t = 4, 1.0
        H = hopping_hamiltonian(n, t, periodic=False)
        N = jw_total_number(n)
        occ1 = [i for i in range(2**n) if abs(np.real(N[i, i]) - 1) < 1e-9]
        ev = np.sort(np.linalg.eigvalsh(H[np.ix_(occ1, occ1)]).real)
        band = np.sort([-2 * t * np.cos(k * np.pi / (n + 1)) for k in range(1, n + 1)])
        assert np.allclose(ev, band, atol=1e-9)

    def test_ring_band(self):
        n, t = 4, 1.0
        H = hopping_hamiltonian(n, t, periodic=True)
        N = jw_total_number(n)
        occ1 = [i for i in range(2**n) if abs(np.real(N[i, i]) - 1) < 1e-9]
        ev = np.sort(np.linalg.eigvalsh(H[np.ix_(occ1, occ1)]).real)
        band = np.sort([-2 * t * np.cos(2 * np.pi * k / n) for k in range(n)])
        assert np.allclose(ev, band, atol=1e-9)

    def test_conserves_particle_number(self):
        # [H, N] = 0 -- hopping preserves total occupation.
        n = 4
        H = hopping_hamiltonian(n, 1.0, periodic=True)
        N = jw_total_number(n)
        assert np.allclose(H @ N - N @ H, 0, atol=1e-12)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
