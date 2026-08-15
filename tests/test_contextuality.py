"""Tests for the Peres-Mermin magic square (quantum contextuality)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    mermin_peres_square,
    classical_assignment_maximum,
    quantum_context_measurement,
)


class TestSquareStructure:
    def test_all_contexts_commute(self):
        assert mermin_peres_square()["all_contexts_commute"]

    def test_products_are_correct_signs(self):
        r = mermin_peres_square()
        assert r["products_verified"]
        assert r["row_signs"] == [1, 1, 1]
        assert r["col_signs"] == [1, 1, -1]


class TestClassicalObstruction:
    def test_no_assignment_satisfies_all_six(self):
        r = classical_assignment_maximum()
        assert r["max_satisfied"] == 5
        assert r["total_assignments"] == 512


class TestQuantumDeterminism:
    @pytest.mark.parametrize(
        "context,index",
        [
            ("row", 0),
            ("row", 1),
            ("row", 2),
            ("col", 0),
            ("col", 1),
            ("col", 2),
        ],
    )
    def test_product_deterministic_on_random_states(self, context, index):
        rng = np.random.default_rng(hash((context, index)) % 2**31)
        for trial in range(6):
            psi = rng.normal(size=4) + 1j * rng.normal(size=4)
            r = quantum_context_measurement(psi, context, index, seed=trial)
            assert r["product"] == r["expected_sign"]

    def test_all_six_contexts_on_one_state(self):
        # The same state satisfies ALL six constraints -- impossible classically.
        psi = np.array([1, 1j, -1, 0.5], dtype=complex)
        for ctx in ("row", "col"):
            for i in range(3):
                r = quantum_context_measurement(psi, ctx, i, seed=9)
                assert r["product"] == r["expected_sign"]

    def test_individual_outcomes_are_random(self):
        # Individual outcomes vary with the branch -- only the product is fixed.
        # (Use a state that is NOT an eigenstate of the row-0 observables.)
        psi = np.array([1, 0.5j, -0.3, 0.8], dtype=complex)
        seen = {
            tuple(quantum_context_measurement(psi, "row", 0, seed=s)["outcomes"])
            for s in range(25)
        }
        assert len(seen) > 1

    def test_invalid_context_rejected(self):
        with pytest.raises(ValueError):
            quantum_context_measurement(np.ones(4), "diagonal", 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
