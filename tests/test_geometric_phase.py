"""Tests for the Pancharatnam-Berry geometric phase."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    bloch_spinor,
    pancharatnam_phase,
    solid_angle,
    berry_phase_triangle,
)


class TestSpinor:
    @pytest.mark.parametrize(
        "n,expected",
        [
            ([0, 0, 1], [1, 0]),
            ([1, 0, 0], [1 / np.sqrt(2), 1 / np.sqrt(2)]),
        ],
    )
    def test_known_spinors(self, n, expected):
        assert np.allclose(np.abs(bloch_spinor(n)), np.abs(expected), atol=1e-12)

    def test_antipodal_orthogonal(self):
        assert abs(np.vdot(bloch_spinor([0, 0, 1]), bloch_spinor([0, 0, -1]))) < 1e-12


class TestBerryPhase:
    def test_octant_is_quarter_pi(self):
        r = berry_phase_triangle([1, 0, 0], [0, 1, 0], [0, 0, 1])
        assert abs(r["solid_angle"] - np.pi / 2) < 1e-9  # octant = 4pi/8
        assert abs(r["phase"] - np.pi / 4) < 1e-9
        assert r["matches"]

    def test_orientation_flips_sign(self):
        fwd = berry_phase_triangle([1, 0, 0], [0, 1, 0], [0, 0, 1])["phase"]
        rev = berry_phase_triangle([0, 0, 1], [0, 1, 0], [1, 0, 0])["phase"]
        assert abs(fwd + rev) < 1e-9

    @pytest.mark.parametrize("seed", range(8))
    def test_random_triangles_match_solid_angle(self, seed):
        # Quantum overlap phase vs classical spherical trigonometry: independent
        # computations, exact agreement.
        rng = np.random.default_rng(seed)
        r = berry_phase_triangle(*rng.normal(size=(3, 3)))
        assert r["matches"]

    def test_gauge_invariance(self):
        rng = np.random.default_rng(3)
        vs = rng.normal(size=(3, 3))
        states = [bloch_spinor(v / np.linalg.norm(v)) for v in vs]
        g1 = pancharatnam_phase(states)
        rephased = [np.exp(1j * rng.uniform(0, 2 * np.pi)) * s for s in states]
        g2 = pancharatnam_phase(rephased)
        assert abs(g1 - g2) < 1e-12

    def test_degenerate_triangle_zero_phase(self):
        # Two coincident vertices: no enclosed area, no geometric phase.
        r = berry_phase_triangle([0, 0, 1], [0, 0, 1], [1, 0, 0])
        assert abs(r["phase"]) < 1e-9
        assert abs(r["solid_angle"]) < 1e-9


class TestSolidAngle:
    def test_octant_families(self):
        # All eight octants have |solid angle| pi/2.
        for sx in (1, -1):
            for sy in (1, -1):
                for sz in (1, -1):
                    E = abs(solid_angle([sx, 0, 0], [0, sy, 0], [0, 0, sz]))
                    assert abs(E - np.pi / 2) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
