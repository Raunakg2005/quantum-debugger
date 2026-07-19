"""Tests for quantum spectroscopy (eigenphase / eigenvalue estimation)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import unitary_eigenphase, hermitian_eigenvalue

try:
    from scipy.stats import unitary_group

    _HAVE_SCIPY_STATS = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY_STATS = False


class TestUnitaryEigenphase:
    @pytest.mark.parametrize("phi", [0.0, 0.125, 0.375, 0.5, 0.625])
    def test_phase_gate(self, phi):
        P = np.array([[1, 0], [0, np.exp(2j * np.pi * phi)]], dtype=complex)
        # |1> is the eigenstate with eigenphase phi.
        r = unitary_eigenphase(P, [0, 1], n_counting=8)
        assert abs(r["phase"] - phi) < 1e-2

    def test_zero_phase_eigenstate(self):
        # |0> of P has eigenphase 0.
        P = np.array([[1, 0], [0, np.exp(2j * np.pi * 0.3)]], dtype=complex)
        assert abs(unitary_eigenphase(P, [1, 0], n_counting=8)["phase"]) < 1e-2

    @pytest.mark.skipif(not _HAVE_SCIPY_STATS, reason="scipy.stats needed")
    @pytest.mark.parametrize("k", [0, 1, 2, 3])
    def test_random_two_qubit_unitary(self, k):
        U = unitary_group.rvs(4, random_state=5)
        w, V = np.linalg.eig(U)
        true_phase = (np.angle(w[k]) / (2 * np.pi)) % 1
        r = unitary_eigenphase(U, V[:, k], n_counting=10)
        assert (
            min(abs(r["phase"] - true_phase), 1 - abs(r["phase"] - true_phase)) < 0.02
        )


class TestHermitianEigenvalue:
    def test_recovers_eigenvalues(self):
        H = np.array([[2.0, 0.5], [0.5, 1.0]], dtype=complex)
        evals, evecs = np.linalg.eigh(H)
        for i in range(2):
            r = hermitian_eigenvalue(H, evecs[:, i], n_counting=10)
            assert abs(r["eigenvalue"] - evals[i]) < 0.02

    def test_diagonal_hamiltonian(self):
        H = np.diag([0.5, 1.5]).astype(complex)
        r = hermitian_eigenvalue(H, [1, 0], n_counting=10)
        assert abs(r["eigenvalue"] - 0.5) < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
