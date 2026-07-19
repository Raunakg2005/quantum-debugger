"""Tests for the QAOA MaxCut solver."""

import pytest

from quantum_debugger.algorithms import solve_maxcut, brute_force_maxcut

SQUARE = [(0, 1), (1, 2), (2, 3), (3, 0)]
TRIANGLE = [(0, 1), (1, 2), (2, 0)]
K4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


class TestBruteForce:
    def test_square(self):
        assert brute_force_maxcut(SQUARE, 4)["cut_value"] == 4

    def test_triangle(self):
        assert brute_force_maxcut(TRIANGLE, 3)["cut_value"] == 2

    def test_k4(self):
        assert brute_force_maxcut(K4, 4)["cut_value"] == 4


class TestSolveMaxcut:
    @pytest.mark.parametrize(
        "graph,n,optimal", [(SQUARE, 4, 4), (TRIANGLE, 3, 2), (K4, 4, 4)]
    )
    def test_finds_near_optimal(self, graph, n, optimal):
        r = solve_maxcut(graph, p=3, restarts=6, seed=1)
        assert r["optimal_cut"] == optimal
        assert r["cut_value"] <= optimal  # cut can't exceed the optimum
        assert r["approximation_ratio"] >= 0.75
        assert len(r["partition"]) == n

    def test_partition_matches_cut_value(self):
        r = solve_maxcut(SQUARE, p=3, restarts=6, seed=2)
        bits = r["partition"]
        crossing = sum(1 for i, j in SQUARE if bits[i] != bits[j])
        assert crossing == r["cut_value"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
