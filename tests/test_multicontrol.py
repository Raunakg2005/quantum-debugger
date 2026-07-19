"""Tests for multi-controlled-X synthesis."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    toffoli_gates,
    fredkin_gates,
    mcx_gates,
    apply_gates,
)
from quantum_debugger.core.quantum_state import QuantumState


def _run(n, init_index, gates):
    state = QuantumState(n)
    sv = np.zeros(2**n, dtype=complex)
    sv[init_index] = 1.0
    state.state_vector = sv
    apply_gates(state, gates)
    probs = np.abs(state.state_vector) ** 2
    return int(np.argmax(probs)), float(np.max(probs))


class TestToffoli:
    @pytest.mark.parametrize("x", range(8))
    def test_matches_ccx(self, x):
        out, prob = _run(3, x, toffoli_gates(0, 1, 2))
        bits = [(x >> q) & 1 for q in range(3)]
        if bits[0] and bits[1]:
            bits[2] ^= 1
        expected = sum(b << q for q, b in enumerate(bits))
        assert out == expected
        assert prob > 0.999  # exact, no phase leakage


class TestFredkin:
    @pytest.mark.parametrize("x", range(8))
    def test_controlled_swap(self, x):
        out, prob = _run(3, x, fredkin_gates(0, 1, 2))
        bits = [(x >> q) & 1 for q in range(3)]
        if bits[0] == 1:  # swap qubits 1 and 2 when control is set
            bits[1], bits[2] = bits[2], bits[1]
        expected = sum(b << q for q, b in enumerate(bits))
        assert out == expected
        assert prob > 0.999


class TestMCX:
    @pytest.mark.parametrize("n_ctrl", [3, 4])
    def test_flips_only_when_all_controls_set(self, n_ctrl):
        target = n_ctrl
        ancillas = list(range(n_ctrl + 1, 2 * n_ctrl))
        n_qubits = 2 * n_ctrl
        controls = list(range(n_ctrl))
        gates = mcx_gates(controls, target, ancillas)
        for x in range(2**n_ctrl):
            idx = sum(((x >> q) & 1) << q for q in range(n_ctrl))
            out, prob = _run(n_qubits, idx, gates)
            all_set = all((x >> q) & 1 for q in range(n_ctrl))
            expected = idx | (1 << target) if all_set else idx
            assert out == expected
            # ancillas returned to |0>
            assert all(not ((out >> a) & 1) for a in ancillas)
            assert prob > 0.999

    def test_small_cases(self):
        # 0 controls -> plain X, 1 control -> CNOT.
        out, _ = _run(2, 0, mcx_gates([], 0, []))
        assert out == 1
        out, _ = _run(2, 0b01, mcx_gates([0], 1, []))
        assert out == 0b11


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
