"""Tests for the Grover-based constraint/SAT solver."""

import pytest

from quantum_debugger.algorithms import grover_solve


class TestGroverSolve:
    def test_single_solution(self):
        # Only x = 5 satisfies the predicate.
        r = grover_solve(lambda x: x == 5, n_qubits=3)
        assert r["solution"] == 5
        assert r["satisfies"]
        assert r["bits"] == [1, 0, 1]  # 5 = 0b101, qubit 0 = LSB
        assert r["success_probability"] > 0.9

    def test_multiple_solutions(self):
        # Even numbers on 4 bits: qubit 0 == 0.
        r = grover_solve(lambda x: x % 2 == 0, n_qubits=4)
        assert r["satisfies"]
        assert r["solution"] % 2 == 0
        assert r["num_solutions"] == 8

    def test_constraint_predicate(self):
        # x with exactly two bits set among 4.
        r = grover_solve(lambda x: bin(x).count("1") == 2, n_qubits=4)
        assert r["satisfies"]
        assert bin(r["solution"]).count("1") == 2

    def test_no_solution(self):
        r = grover_solve(lambda x: False, n_qubits=3)
        assert r["solution"] is None
        assert not r["satisfies"]
        assert r["num_solutions"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
