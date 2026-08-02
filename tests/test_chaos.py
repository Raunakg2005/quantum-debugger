"""Quantum chaos & scrambling (v3.5.0) -- verification tests.

Random-matrix spacing statistics, the spectral form factor's D^2/D normalization and plateau,
Krylov-complexity Lanczos reconstruction of the autocorrelation, and ETH thermalization -- each
checked against a closed form or the exact spectrum.
"""
import numpy as np
import pytest

from quantum_debugger.algorithms.random_matrix import (
    goe_matrix, gue_matrix, wigner_surmise, poisson_spacing_pdf, semicircle_density,
    unfolded_spacings, mean_ratio, surmise_normalization, surmise_mean,
)
from quantum_debugger.algorithms.spectral_form_factor import (
    spectral_form_factor, sff_at_zero, plateau_value, long_time_average,
    reaches_plateau, normalized_sff, sff_curve,
)
from quantum_debugger.algorithms.krylov_complexity import (
    lanczos_coefficients, autocorrelation, reconstruct_autocorrelation,
    krylov_complexity, krylov_dimension, moment, operator_inner_product,
)
from quantum_debugger.algorithms.eth import (
    eigenbasis, diagonal_elements, eth_diagonal_fluctuation, thermalizes,
    eigenstate_matches_microcanonical,
)

Z = np.array([[1, 0], [0, -1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)


def _projector(D):
    O = np.zeros((D, D), dtype=complex)
    for i in range(D // 2):
        O[i, i] = 1.0
    return O


def test_wigner_surmise_normalized():
    for beta in (1, 2):
        assert surmise_normalization(beta) == pytest.approx(1.0, abs=1e-2)
        assert surmise_mean(beta) == pytest.approx(1.0, abs=1e-2)
    assert wigner_surmise(0.0, 1) == 0.0            # level repulsion
    assert poisson_spacing_pdf(0.0) == pytest.approx(1.0)


def test_goe_gue_ratios():
    wg = np.linalg.eigvalsh(goe_matrix(400, seed=1))
    assert mean_ratio(wg) == pytest.approx(0.53, abs=0.03)
    wp = np.sort(np.random.default_rng(2).random(3000))
    assert mean_ratio(wp) == pytest.approx(0.386, abs=0.03)


def test_semicircle_and_unfolding():
    assert semicircle_density(0.0, 2.0) == pytest.approx(1.0 / np.pi, abs=1e-9)
    assert semicircle_density(3.0, 2.0) == 0.0
    sp = unfolded_spacings(np.linalg.eigvalsh(goe_matrix(200, seed=3)))
    assert sp.mean() == pytest.approx(1.0, abs=1e-9)


def test_sff_zero_and_plateau():
    e = np.linalg.eigvalsh(goe_matrix(64, seed=3))
    assert sff_at_zero(e) == pytest.approx(64 ** 2)
    assert plateau_value(e) == 64
    assert long_time_average(e, 400) == pytest.approx(64, rel=0.1)
    assert reaches_plateau(e, 400)
    assert normalized_sff(e, 0.0) == pytest.approx(64)


def test_sff_curve_shape():
    e = np.linalg.eigvalsh(goe_matrix(32, seed=4))
    ts, s = sff_curve(e, 50, points=200)
    assert s[0] == pytest.approx(32 ** 2)      # SFF(0) = D^2


def test_krylov_single_spin():
    w = 1.6
    H = (w / 2) * Z
    bs = lanczos_coefficients(H, X)
    assert bs[0] == pytest.approx(w, abs=1e-6)     # b_1 = omega
    assert krylov_dimension(bs) == 2


def test_krylov_reconstructs_autocorrelation():
    w = 1.6
    H = (w / 2) * Z
    bs = lanczos_coefficients(H, X)
    for t in (0.3, 0.7, 1.5):
        exact = autocorrelation(H, X, t)
        assert reconstruct_autocorrelation(bs, t) == pytest.approx(exact, abs=1e-6)
        assert exact == pytest.approx(np.cos(w * t), abs=1e-6)


def test_krylov_complexity_oscillates():
    w = 1.6
    H = (w / 2) * Z
    bs = lanczos_coefficients(H, X)
    assert krylov_complexity(bs, 0.0) == pytest.approx(0.0, abs=1e-9)
    assert krylov_complexity(bs, np.pi / (2 * w)) == pytest.approx(1.0, abs=1e-6)


def test_moments_even_nonnegative():
    H = goe_matrix(16, seed=5)
    O = goe_matrix(16, seed=6)
    assert moment(H, O, 0).real == pytest.approx(1.0, abs=1e-9)   # normalized
    assert moment(H, O, 2).real >= -1e-9


def test_eth_thermalization_with_bounded_observable():
    H = goe_matrix(200, seed=5)
    O = _projector(200)
    assert thermalizes(H, O, tol=0.1)
    assert eigenstate_matches_microcanonical(H, O) < 0.1


def test_eth_diagonal_fluctuation_shrinks_with_dimension():
    O50 = _projector(50)
    O400 = _projector(400)
    f50 = eth_diagonal_fluctuation(eigenbasis(goe_matrix(50, seed=7))[1], O50)
    f400 = eth_diagonal_fluctuation(eigenbasis(goe_matrix(400, seed=7))[1], O400)
    assert f400 < f50                              # diagonal smooths as D grows
