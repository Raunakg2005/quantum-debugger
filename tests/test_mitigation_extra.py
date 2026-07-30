"""
Tests for the 1.2.0 mitigation backfill: ZNE extrapolation models, unitary folding,
advanced readout mitigation, PEC via PTM inversion, and multi-pulse dynamical
decoupling. Every routine is checked against an exact value or a closed form.
"""

import numpy as np
import pytest
from scipy.stats import unitary_group

from quantum_debugger.algorithms.zne_extrapolation import (
    richardson_extrapolate, polynomial_extrapolate, exponential_extrapolate,
    adaptive_extrapolate)
from quantum_debugger.algorithms.unitary_folding import (
    fold_global, noise_scale_factor, fold_gate_sequence, folded_channel_expectation)
from quantum_debugger.algorithms.readout_advanced import (
    tensored_assignment_matrix, tensored_mitigate, iterative_bayesian_unfolding,
    constrained_readout_mitigate, calibrate_assignment_matrix)
from quantum_debugger.algorithms.pec_ptm import (
    channel_ptm, invert_channel_ptm, pec_sampling_overhead, depolarizing_overhead,
    pauli_quasiprobabilities, pec_mitigate_ptm)
from quantum_debugger.algorithms.dynamical_decoupling import (
    cpmg_sequence, xy4_sequence, udd_sequence, switching_function_moments,
    suppression_order, dd_coherence)


def _depol_kraus(p):
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.diag([1, -1]).astype(complex)
    return [np.sqrt(1 - 3 * p / 4) * I, np.sqrt(p / 4) * X,
            np.sqrt(p / 4) * Y, np.sqrt(p / 4) * Z]


class TestZNEExtrapolation:
    def test_richardson_exact_polynomial(self):
        poly = np.poly1d([0.3, -0.5, 0.2, 0.7])  # cubic, E(0) = 0.7
        x = np.array([1., 2., 3., 4.])
        assert abs(richardson_extrapolate(x, poly(x)) - 0.7) < 1e-9

    def test_polynomial_exact(self):
        p = np.poly1d([0.1, -0.3, 0.9])
        x = np.array([1., 2., 3., 4.])
        assert abs(polynomial_extrapolate(x, p(x), 2) - 0.9) < 1e-9

    def test_exponential_exact(self):
        A, B, c = 0.8, -0.6, 0.7
        x = np.array([0.5, 1., 1.5, 2., 3.])
        r = exponential_extrapolate(x, A + B * np.exp(-c * x))
        assert abs(r["value"] - (A + B)) < 1e-3

    def test_adaptive_selects_model(self):
        x = np.array([0.5, 1., 1.5, 2., 3.])
        assert adaptive_extrapolate(x, 0.8 - 0.6 * np.exp(-0.7 * x))["model"] == "exponential"
        lin = adaptive_extrapolate(x, 1.2 - 0.4 * x)
        assert lin["model"] == "linear" and abs(lin["value"] - 1.2) < 1e-6


class TestUnitaryFolding:
    def test_global_fold_preserves_action(self):
        G = unitary_group.rvs(4, random_state=1)
        for k in (1, 2, 3):
            assert np.allclose(fold_global(G, k), G, atol=1e-12)
            assert noise_scale_factor(k) == 2 * k + 1

    def test_local_fold_preserves_product(self):
        gates = [unitary_group.rvs(2, random_state=i) for i in range(4)]
        folded = fold_gate_sequence(gates, [1, 3])

        def prod(gs):
            U = np.eye(2, dtype=complex)
            for g in gs:
                U = g @ U
            return U
        assert np.allclose(prod(folded), prod(gates), atol=1e-12)
        assert len(folded) == 8  # 4 gates, 2 folded (+2 each)

    def test_folded_noise_amplifies(self):
        Z = np.diag([1, -1]).astype(complex)
        rho0 = np.array([[1, 0], [0, 0]], dtype=complex)

        def depol(rho, p=0.1):
            return (1 - p) * rho + p * np.eye(2) * np.trace(rho) / 2
        vals = [folded_channel_expectation(lambda: rho0.copy(), depol, Z, k)
                for k in (0, 1, 2, 3)]
        assert all(vals[i] > vals[i + 1] for i in range(3))  # decays with folds
        assert abs(vals[1] - 0.9 ** 3) < 1e-9


class TestReadoutAdvanced:
    def test_tensored(self):
        A0 = np.array([[0.95, 0.08], [0.05, 0.92]])
        A1 = np.array([[0.90, 0.10], [0.10, 0.90]])
        A = tensored_assignment_matrix([A0, A1])
        p_true = np.array([0.5, 0.2, 0.2, 0.1])
        rec = tensored_mitigate(A @ p_true, [A0, A1])
        assert np.max(np.abs(rec - p_true)) < 1e-12

    def test_ibu_valid_and_accurate(self):
        A0 = np.array([[0.95, 0.08], [0.05, 0.92]])
        A1 = np.array([[0.90, 0.10], [0.10, 0.90]])
        A = tensored_assignment_matrix([A0, A1])
        p_true = np.array([0.5, 0.2, 0.2, 0.1])
        ibu = iterative_bayesian_unfolding(A @ p_true, A, 300)
        assert np.max(np.abs(ibu - p_true)) < 1e-4
        assert abs(ibu.sum() - 1) < 1e-9 and np.all(ibu >= 0)

    def test_constrained_valid_and_accurate(self):
        A0 = np.array([[0.95, 0.08], [0.05, 0.92]])
        A1 = np.array([[0.90, 0.10], [0.10, 0.90]])
        A = tensored_assignment_matrix([A0, A1])
        p_true = np.array([0.5, 0.2, 0.2, 0.1])
        con = constrained_readout_mitigate(A @ p_true, A)
        assert np.max(np.abs(con - p_true)) < 1e-4
        assert abs(con.sum() - 1) < 1e-8 and np.all(con >= -1e-12)

    def test_calibration(self):
        A0 = np.array([[0.95, 0.08], [0.05, 0.92]])
        A1 = np.array([[0.90, 0.10], [0.10, 0.90]])
        A = tensored_assignment_matrix([A0, A1])
        cols = [A[:, j] for j in range(4)]
        assert np.allclose(calibrate_assignment_matrix(cols), A, atol=1e-12)


class TestPECPtm:
    def test_ptm_inverse(self):
        R = channel_ptm(_depol_kraus(0.2))
        assert np.allclose(invert_channel_ptm(R) @ R, np.eye(4), atol=1e-12)

    def test_overhead_matches_closed_form(self):
        assert abs(pec_sampling_overhead(np.eye(4)) - 1.0) < 1e-12
        for p in (0.1, 0.2, 0.3):
            R = channel_ptm(_depol_kraus(p))
            pd = 1 - R[1, 1]
            assert abs(pec_sampling_overhead(R) - depolarizing_overhead(pd)) < 1e-9
            assert abs(pauli_quasiprobabilities(R).sum() - 1.0) < 1e-12

    def test_pec_recovers_noiseless(self):
        Z = np.diag([1, -1]).astype(complex)
        rho_ideal = np.array([[0.8, 0.1], [0.1, 0.2]], dtype=complex)
        K = _depol_kraus(0.2)
        rho_noisy = sum(k @ rho_ideal @ k.conj().T for k in K)
        exact = np.real(np.trace(Z @ rho_ideal))
        assert abs(pec_mitigate_ptm(rho_noisy, K, Z) - exact) < 1e-9


class TestDynamicalDecoupling:
    def test_udd_cancels_n_moments(self):
        for n in (1, 2, 3, 4, 5, 6):
            seq = udd_sequence(n)
            assert suppression_order(seq) == n
            M = switching_function_moments(seq, n)
            assert np.max(np.abs(M[:n])) < 1e-9 and abs(M[n]) > 1e-6

    def test_cpmg_refocuses_static(self):
        for n in (1, 2, 4, 8):
            assert abs(switching_function_moments(cpmg_sequence(n), 0)[0]) < 1e-12

    def test_xy4_axes_and_moment(self):
        t, axes = xy4_sequence(1)
        assert axes == ["X", "Y", "X", "Y"]
        assert abs(switching_function_moments(t, 0)[0]) < 1e-12

    def test_dd_coherence(self):
        sigma = 1.5
        assert abs(dd_coherence([], sigma) - np.exp(-sigma**2 / 2)) < 1e-6  # free decay
        assert abs(dd_coherence(cpmg_sequence(4), sigma) - 1.0) < 1e-9
        assert abs(dd_coherence(udd_sequence(4), sigma) - 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
