"""Tests for entangled state preparation."""

import numpy as np
import pytest

from quantum_debugger.algorithms import ghz_state, w_state, graph_state


def _fidelity(a, b):
    return abs(np.vdot(a, b)) ** 2


class TestGHZ:
    @pytest.mark.parametrize("n", [2, 3, 4, 5])
    def test_ghz(self, n):
        sv = ghz_state(n)
        expected = np.zeros(2**n, dtype=complex)
        expected[0] = expected[-1] = 1 / np.sqrt(2)
        assert _fidelity(sv, expected) > 1 - 1e-9


class TestW:
    @pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
    def test_w(self, n):
        sv = w_state(n)
        expected = np.zeros(2**n, dtype=complex)
        for k in range(n):
            expected[1 << k] = 1 / np.sqrt(n)
        assert _fidelity(sv, expected) > 1 - 1e-9

    def test_w_amplitudes_equal_and_positive(self):
        sv = w_state(4)
        amps = [sv[1 << k] for k in range(4)]
        assert np.allclose(amps, 0.5)


class TestGraphState:
    def test_line_graph_stabilizers(self):
        # Line 0-1-2: stabilizers X0Z1, Z0X1Z2, Z1X2 all have eigenvalue +1.
        sv = graph_state([(0, 1), (1, 2)], 3)
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        Ii = np.eye(2, dtype=complex)

        def op(ps):
            m = np.array([[1]], dtype=complex)
            for p in reversed(ps):
                m = np.kron(m, {"X": X, "Z": Z, "I": Ii}[p])
            return m

        for s in ("XZI", "ZXZ", "IZX"):
            assert np.isclose(np.real(np.vdot(sv, op(s) @ sv)), 1.0, atol=1e-9)

    def test_two_qubit_edge_is_bell(self):
        # A single-edge graph state equals a Bell state up to local H.
        sv = graph_state([(0, 1)], 2)
        assert np.isclose(np.linalg.norm(sv), 1.0)
        # |++> with a CZ -> (|00>+|01>+|10>-|11>)/2
        expected = np.array([1, 1, 1, -1], dtype=complex) / 2
        assert _fidelity(sv, expected) > 1 - 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
