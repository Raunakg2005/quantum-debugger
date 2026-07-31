"""
Tests for the 1.8.0 continuous-variable suite: Gaussian states, symplectic transforms,
Fock-space operators, Wigner functions, boson sampling, and bosonic cat codes. Verified
against harmonic-oscillator closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.gaussian_states import (
    vacuum_covariance, squeezed_covariance, thermal_covariance, symplectic_eigenvalues,
    is_physical_covariance, purity_gaussian, gaussian_entropy)
from quantum_debugger.algorithms.symplectic import (
    is_symplectic, phase_rotation_symplectic, squeezing_symplectic, beamsplitter_symplectic,
    apply_symplectic, two_mode_squeezing_symplectic)
from quantum_debugger.algorithms.fock_space import (
    annihilation_operator, creation_operator, number_operator_fock, coherent_state_fock,
    displacement_operator, squeeze_operator, mean_photon_number)
from quantum_debugger.algorithms.wigner import (
    wigner_point, wigner_negativity, wigner_integral, husimi_q)
from quantum_debugger.algorithms.boson_sampling import (
    permanent, boson_sampling_probability, beamsplitter_unitary, hong_ou_mandel)
from quantum_debugger.algorithms.bosonic_codes import (
    cat_state, parity_expectation, cat_code_words, loss_flips_parity)


class TestGaussianStates:
    def test_vacuum(self):
        assert is_physical_covariance(vacuum_covariance(1))
        assert abs(purity_gaussian(vacuum_covariance(1)) - 1) < 1e-9

    def test_squeezed_pure(self):
        sq = squeezed_covariance(0.5)
        assert abs(symplectic_eigenvalues(sq)[0] - 1) < 1e-9
        assert is_physical_covariance(sq)

    def test_thermal(self):
        th = thermal_covariance(2.0)
        assert abs(symplectic_eigenvalues(th)[0] - 5) < 1e-9
        assert abs(purity_gaussian(th) - 0.2) < 1e-9
        assert gaussian_entropy(th) > 0

    def test_unphysical_rejected(self):
        assert not is_physical_covariance(np.diag([0.3, 0.3]))


class TestSymplectic:
    def test_all_symplectic(self):
        for S in (phase_rotation_symplectic(0.7), squeezing_symplectic(0.5),
                  beamsplitter_symplectic(0.6), two_mode_squeezing_symplectic(0.4)):
            assert is_symplectic(S)

    def test_squeeze_vacuum(self):
        out = apply_symplectic(vacuum_covariance(1), squeezing_symplectic(0.5))
        assert np.allclose(out, squeezed_covariance(0.5), atol=1e-9)

    def test_tms_entangles(self):
        tms = apply_symplectic(vacuum_covariance(2), two_mode_squeezing_symplectic(0.4))
        assert abs(tms[0, 2]) > 0.1 and is_physical_covariance(tms)


class TestFockSpace:
    def test_commutator(self):
        c = 30; a = annihilation_operator(c); ad = creation_operator(c)
        assert np.allclose(np.diag(a @ ad - ad @ a)[:c - 1], 1, atol=1e-9)
        assert np.allclose(number_operator_fock(c), ad @ a, atol=1e-9)

    def test_coherent_state(self):
        c = 30; alpha = 1.2 + 0.5j
        ca = coherent_state_fock(alpha, c)
        a = annihilation_operator(c)
        assert np.allclose((a @ ca)[:c - 2], (alpha * ca)[:c - 2], atol=1e-4)
        assert abs(mean_photon_number(ca) - abs(alpha) ** 2) < 1e-3

    def test_displacement_and_squeeze(self):
        c = 30; vac = np.zeros(c, dtype=complex); vac[0] = 1
        D = displacement_operator(1.0 + 0.3j, c)
        assert np.allclose(np.abs(D @ vac), np.abs(coherent_state_fock(1.0 + 0.3j, c)), atol=1e-3)
        sq = squeeze_operator(0.6, c) @ vac
        assert np.allclose(np.abs(sq[1::2]), 0, atol=1e-6)     # even photons only


class TestWigner:
    def test_vacuum_wigner(self):
        c = 40; vac = np.zeros(c, dtype=complex); vac[0] = 1
        rho = np.outer(vac, vac.conj())
        for al in (0, 0.5 + 0.3j, 1j):
            assert abs(wigner_point(rho, al, c) - (2 / np.pi) * np.exp(-2 * abs(al) ** 2)) < 1e-4
        assert abs(wigner_integral(rho, c) - 1) < 1e-2
        assert wigner_negativity(rho, c) < 1e-3

    def test_cat_negativity(self):
        c = 40; b = 2.0
        cat = coherent_state_fock(b, c) + coherent_state_fock(-b, c); cat /= np.linalg.norm(cat)
        assert wigner_negativity(np.outer(cat, cat.conj()), c, span=4, points=61) > 0.1

    def test_husimi_nonneg(self):
        c = 40; vac = np.zeros(c, dtype=complex); vac[0] = 1
        rho = np.outer(vac, vac.conj())
        assert husimi_q(rho, 0, c) >= 0
        assert abs(husimi_q(rho, 0, c) - 1 / np.pi) < 1e-3


class TestBosonSampling:
    def test_permanent(self):
        assert abs(permanent(np.ones((3, 3))) - 6) < 1e-9
        assert abs(permanent(np.eye(4)) - 1) < 1e-9

    def test_hom_dip(self):
        h = hong_ou_mandel(np.pi / 4)
        assert h["coincidence"] < 1e-9 and abs(h["bunching"] - 1) < 1e-9
        assert abs(hong_ou_mandel(0.0)["coincidence"] - 1) < 1e-9

    def test_normalization(self):
        from scipy.stats import unitary_group
        U = unitary_group.rvs(3, random_state=1)
        outs = [[2, 0, 0], [0, 2, 0], [0, 0, 2], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
        assert abs(sum(boson_sampling_probability(U, [1, 1, 0], o) for o in outs) - 1) < 1e-6


class TestBosonicCodes:
    def test_parity(self):
        assert abs(parity_expectation(cat_state(2.0, "even")) - 1) < 1e-6
        assert abs(parity_expectation(cat_state(2.0, "odd")) + 1) < 1e-6

    def test_code_words_orthogonal(self):
        c0, c1 = cat_code_words(2.0)
        assert abs(np.vdot(c0, c1)) < 1e-6

    def test_loss_detectable(self):
        assert loss_flips_parity(2.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
