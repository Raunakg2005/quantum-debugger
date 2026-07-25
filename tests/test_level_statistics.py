"""Tests for level-spacing statistics (quantum chaos diagnostic)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    level_spacing_ratio,
    goe_reference,
    poisson_reference,
    classify_spectrum,
)


class TestReferenceEnsembles:
    def test_goe_matches_wigner_dyson(self):
        r = goe_reference(size=200, samples=30, seed=1)
        assert abs(r - 0.5307) < 0.02

    def test_poisson_matches_integrable(self):
        r = poisson_reference(size=5000, samples=30, seed=2)
        assert abs(r - 0.3863) < 0.02

    def test_goe_shows_level_repulsion(self):
        # GOE > Poisson: chaotic spectra repel, integrable ones don't.
        assert goe_reference(size=150, samples=20, seed=3) > poisson_reference(
            size=3000, samples=20, seed=3
        )


class TestStatistic:
    def test_equal_spacing_gives_one(self):
        # A perfectly rigid (equally spaced) spectrum has all gap ratios = 1.
        assert abs(level_spacing_ratio(np.arange(100.0)) - 1.0) < 1e-12

    def test_sorting_invariant(self):
        rng = np.random.default_rng(0)
        evals = rng.normal(size=500)
        assert abs(
            level_spacing_ratio(evals) - level_spacing_ratio(np.sort(evals))
        ) < 1e-12

    def test_ratio_in_unit_interval(self):
        rng = np.random.default_rng(1)
        r = level_spacing_ratio(rng.normal(size=1000))
        assert 0 <= r <= 1

    def test_degeneracies_dropped(self):
        # Repeated eigenvalues (zero gaps) must not produce division by zero.
        evals = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 3.0])
        r = level_spacing_ratio(evals)
        assert np.isfinite(r)


class TestClassification:
    def test_goe_spectrum_labeled_chaotic(self):
        rng = np.random.default_rng(5)
        A = rng.normal(size=(300, 300))
        evals = np.linalg.eigvalsh((A + A.T) / 2)
        assert classify_spectrum(evals)["classification"] == "chaotic"

    def test_poisson_spectrum_labeled_integrable(self):
        rng = np.random.default_rng(6)
        evals = np.sort(rng.uniform(size=8000))
        assert classify_spectrum(evals)["classification"] == "integrable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
