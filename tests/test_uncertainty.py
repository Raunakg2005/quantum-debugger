"""Tests for the Robertson and Maassen-Uffink uncertainty relations."""

import numpy as np
import pytest

from quantum_debugger.algorithms import robertson_bound, entropic_uncertainty

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class TestRobertson:
    def test_tight_on_z_eigenstate(self):
        # X, Y on |0>: dX = dY = 1 and |<[X,Y]>|/2 = |<Z>| = 1 -- equality.
        r = robertson_bound(_X, _Y, [1, 0])
        assert abs(r["product"] - 1.0) < 1e-12
        assert abs(r["bound"] - 1.0) < 1e-12
        assert r["satisfied"]

    @pytest.mark.parametrize("seed", range(10))
    def test_holds_on_random_states_and_observables(self, seed):
        rng = np.random.default_rng(seed)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        M1 = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        M2 = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        A, B = M1 + M1.conj().T, M2 + M2.conj().T
        assert robertson_bound(A, B, psi)["satisfied"]

    def test_commuting_observables_no_bound(self):
        r = robertson_bound(_Z, _Z, [0.6, 0.8])
        assert r["bound"] < 1e-12

    def test_x_eigenstate_trivial_bound(self):
        # On |+>, <Z> = 0: Robertson's bound degenerates to 0 (its weakness).
        r = robertson_bound(_X, _Y, np.array([1, 1]) / np.sqrt(2))
        assert r["bound"] < 1e-12


class TestMaassenUffink:
    def test_mub_bound_is_one_bit(self):
        r = entropic_uncertainty(_X, _Z, [1, 0])
        assert abs(r["bound"] - 1.0) < 1e-9

    def test_equality_on_z_eigenstate(self):
        # H(Z) = 0, H(X) = 1: sum hits the bound exactly.
        r = entropic_uncertainty(_X, _Z, [1, 0])
        assert abs(r["sum"] - 1.0) < 1e-9
        assert r["satisfied"]

    def test_equality_on_x_eigenstate(self):
        r = entropic_uncertainty(_X, _Z, np.array([1, 1]) / np.sqrt(2))
        assert abs(r["sum"] - 1.0) < 1e-9

    @pytest.mark.parametrize("seed", range(10))
    def test_never_violated_where_robertson_degenerates(self, seed):
        # The entropic bound stays 1 bit even where Robertson's collapses to 0.
        rng = np.random.default_rng(seed)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        r = entropic_uncertainty(_X, _Z, psi)
        assert abs(r["bound"] - 1.0) < 1e-9
        assert r["satisfied"]

    def test_intermediate_state_strictly_above(self):
        theta = np.pi / 8
        psi = [np.cos(theta), np.sin(theta)]
        r = entropic_uncertainty(_X, _Z, psi)
        assert r["sum"] > 1.0 + 1e-6  # strictly above the bound

    def test_same_basis_no_bound(self):
        r = entropic_uncertainty(_Z, _Z, [0.6, 0.8])
        assert r["bound"] < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
