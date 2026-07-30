"""
Tests for the 1.1.0 QSVT applications: matrix functions, spectral estimation,
amplitude amplification, and the QSP completion identity. Every routine is checked
against the exact spectrum / a closed form.
"""

import numpy as np
import pytest
from numpy.polynomial.chebyshev import chebval
from scipy.linalg import expm, logm, sqrtm

from quantum_debugger.algorithms.qsvt_applications import (
    matrix_sign_qsvt, spectral_projector_qsvt, matrix_sqrt_qsvt,
    matrix_inverse_sqrt_qsvt, matrix_power_qsvt, pseudo_inverse_qsvt,
    bandpass_filter_qsvt, matrix_exp_qsvt, matrix_log_qsvt,
    gibbs_state_qsvt, ground_state_projector_qsvt)
from quantum_debugger.algorithms.chebyshev_spectral import (
    spectral_moments, trace_of_function, partition_function_qsvt,
    density_of_states_kpm, eigenvalue_count_in_interval)
from quantum_debugger.algorithms.qsvt_amplification import (
    amplitude_amplification_qsvt, grover_amplitude_simulated,
    chebyshev_approximation)
from quantum_debugger.algorithms.qsp import qsp_complementary_response


def _herm(w, seed=0):
    """Random Hermitian matrix with the given eigenvalues."""
    rng = np.random.default_rng(seed)
    n = len(w)
    Q, _ = np.linalg.qr(rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n)))
    return (Q * w) @ Q.conj().T, Q


# --- matrix functions -------------------------------------------------------

class TestMatrixFunctions:
    def test_sign_gapped(self):
        w = np.array([-0.9, -0.4, 0.4, 0.9])
        A, Q = _herm(w, 1)
        exact = (Q * np.sign(w)) @ Q.conj().T
        assert np.max(np.abs(matrix_sign_qsvt(A, gap=0.4, degree=61) - exact)) < 1e-4

    def test_spectral_projector(self):
        w = np.array([-0.9, -0.4, 0.4, 0.9])
        A, Q = _herm(w, 2)
        P = spectral_projector_qsvt(A, 0.0, gap=0.4, degree=61, above=True)
        assert np.max(np.abs(P - (Q * (w > 0)) @ Q.conj().T)) < 1e-4
        assert np.max(np.abs(P @ P - P)) < 1e-4  # idempotent

    def test_sqrt(self):
        A, _ = _herm(np.array([0.2, 0.45, 0.7, 1.0]), 3)
        S = matrix_sqrt_qsvt(A, 40)
        assert np.max(np.abs(S @ S - A)) < 1e-8
        assert np.max(np.abs(S - sqrtm(A))) < 1e-8

    def test_inverse_sqrt(self):
        A, _ = _herm(np.array([0.25, 0.5, 0.75, 1.0]), 4)
        IS = matrix_inverse_sqrt_qsvt(A, 40)
        assert np.max(np.abs(IS @ A @ IS - np.eye(4))) < 1e-7

    def test_power(self):
        A, Q = _herm(np.array([0.3, 0.5, 0.75, 1.0]), 5)
        w = np.array([0.3, 0.5, 0.75, 1.0])
        for p in (0.5, 1.5, -1.0, -0.5):
            exact = (Q * (w ** p)) @ Q.conj().T
            assert np.max(np.abs(matrix_power_qsvt(A, p, 45) - exact)) < 1e-7

    def test_exp(self):
        A, _ = _herm(np.array([-0.9, -0.3, 0.5, 0.95]), 6)
        assert np.max(np.abs(matrix_exp_qsvt(A, 30) - expm(A))) < 1e-8

    def test_log(self):
        A, _ = _herm(np.array([0.2, 0.45, 0.7, 1.0]), 7)
        assert np.max(np.abs(matrix_log_qsvt(A, 45) - logm(A))) < 1e-7

    def test_pseudo_inverse_converges_to_regularized(self):
        w = np.array([-0.9, -0.5, 0.0, 0.6, 0.95])
        A, Q = _herm(w, 8)
        reg = (Q * (w / (w**2 + 1e-2))) @ Q.conj().T
        prev = np.inf
        for deg in (80, 160, 240):
            err = np.max(np.abs(pseudo_inverse_qsvt(A, 1e-2, deg) - reg))
            assert err < prev
            prev = err
        assert prev < 1e-9  # QSVT reproduces the regularized filter

    def test_pseudo_inverse_converges_to_pinv(self):
        w = np.array([-0.9, -0.5, 0.0, 0.6, 0.95])
        A, _ = _herm(w, 8)
        pinv = np.linalg.pinv(A)
        e_coarse = np.max(np.abs(pseudo_inverse_qsvt(A, 1e-1, 60) - pinv))
        e_fine = np.max(np.abs(pseudo_inverse_qsvt(A, 1e-2, 160) - pinv))
        assert e_fine < e_coarse  # -> np.pinv as eps -> 0

    def test_bandpass(self):
        w = np.array([-0.9, -0.2, 0.3, 0.85])
        A, Q = _herm(w, 9)
        B = bandpass_filter_qsvt(A, 0.3, 0.15, 40)
        exact = (Q * np.exp(-((w - 0.3) / 0.15) ** 2)) @ Q.conj().T
        assert np.max(np.abs(B - exact)) < 1e-5


class TestThermalAndGround:
    def test_gibbs(self):
        w = np.array([-0.8, -0.1, 0.4, 0.9])
        H, Q = _herm(w, 10)
        beta = 1.5
        Z = np.sum(np.exp(-beta * w))
        rho_exact = (Q * (np.exp(-beta * w) / Z)) @ Q.conj().T
        assert np.max(np.abs(gibbs_state_qsvt(H, beta, 30) - rho_exact)) < 1e-8
        assert abs(np.real(np.trace(gibbs_state_qsvt(H, beta, 30))) - 1) < 1e-9

    def test_gibbs_infinite_temperature(self):
        H, _ = _herm(np.array([-0.8, -0.1, 0.4, 0.9]), 11)
        assert np.allclose(gibbs_state_qsvt(H, 0.0, 30), np.eye(4) / 4, atol=1e-6)

    def test_ground_state_projector(self):
        w = np.array([-0.8, -0.2, 0.3, 0.9])
        H, Q = _herm(w, 12)
        Pg = ground_state_projector_qsvt(H, cutoff=-0.5, gap=0.3, degree=71)
        assert np.max(np.abs(Pg - np.outer(Q[:, 0], Q[:, 0].conj()))) < 1e-4
        assert abs(np.real(np.trace(Pg)) - 1) < 1e-3


# --- spectral estimation ----------------------------------------------------

class TestSpectralEstimation:
    def _A(self):
        return _herm(np.array([-0.9, -0.3, 0.1, 0.5, 0.85, -0.6]), 13)

    def test_moments(self):
        A, _ = self._A()
        w = np.array([-0.9, -0.3, 0.1, 0.5, 0.85, -0.6])
        mu = spectral_moments(A, 8)
        for k in range(8):
            c = np.zeros(k + 1); c[k] = 1
            assert abs(mu[k] - np.sum(chebval(w, c))) < 1e-9

    def test_trace_of_function(self):
        A, _ = self._A()
        w = np.array([-0.9, -0.3, 0.1, 0.5, 0.85, -0.6])
        for f in (np.exp, lambda x: np.cos(2 * x), lambda x: x**3):
            assert abs(trace_of_function(A, f, 30) - np.sum(f(w))) < 1e-9

    def test_partition_function(self):
        A, _ = self._A()
        w = np.array([-0.9, -0.3, 0.1, 0.5, 0.85, -0.6])
        assert abs(partition_function_qsvt(A, 1.2, 30) - np.sum(np.exp(-1.2 * w))) < 1e-9

    def test_dos_integrates_to_dim(self):
        A, _ = self._A()
        x, rho = density_of_states_kpm(A, 60, 600)
        assert abs(np.trapezoid(rho, x) - 6.0) < 1e-2

    def test_eigenvalue_count(self):
        A, _ = self._A()
        w = np.array([-0.9, -0.3, 0.1, 0.5, 0.85, -0.6])
        for a, b in [(-0.5, 0.4), (-1.0, 0.0), (0.0, 1.0)]:
            true = int(np.sum((w > a) & (w < b)))
            assert round(eigenvalue_count_in_interval(A, a, b, 0.15, 70)) == true


# --- amplitude amplification & approximation --------------------------------

class TestAmplitudeAmplification:
    def test_matches_simulation(self):
        for a in (0.1, 0.25, 0.4):
            for k in (1, 2, 3, 5):
                res = amplitude_amplification_qsvt(a, k)
                assert abs(res["amplitude"] - grover_amplitude_simulated(a, k)) < 1e-12

    def test_optimal_amplifies(self):
        a = 0.1
        k = amplitude_amplification_qsvt(a, 0)["optimal_iterations"]
        assert amplitude_amplification_qsvt(a, k)["probability"] > 0.99


class TestChebyshevApproximation:
    def test_geometric_decay(self):
        errs = [chebyshev_approximation(np.exp, d)["max_error"] for d in (4, 8, 12)]
        assert errs[0] > errs[1] > errs[2]
        assert errs[-1] < 1e-10

    def test_poly_matches_func(self):
        approx = chebyshev_approximation(lambda x: np.cos(3 * x), 20, domain=(-1, 1))
        xs = np.linspace(-1, 1, 100)
        assert np.max(np.abs(approx["poly"](xs) - np.cos(3 * xs))) < 1e-9


class TestQSPCompletion:
    def test_completion_identity(self):
        rng = np.random.default_rng(14)
        phases = rng.uniform(0, 2 * np.pi, 6)
        xs = np.linspace(-0.95, 0.95, 50)
        P, Q = qsp_complementary_response(phases, xs)
        identity = np.abs(P) ** 2 + (1 - xs**2) * np.abs(Q) ** 2
        assert np.max(np.abs(identity - 1)) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
