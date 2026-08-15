"""Tests for magic measures (stabilizer Renyi entropy)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import stabilizer_renyi_entropy, magic_of_t_states
from quantum_debugger.stabilizer import StabilizerSimulator

_T_STATE = np.array([1, np.exp(1j * np.pi / 4)], dtype=complex) / np.sqrt(2)


class TestStabilizerStatesHaveZeroMagic:
    @pytest.mark.parametrize(
        "sv",
        [
            [1, 0],
            [0, 1],
            np.array([1, 1]) / np.sqrt(2),
            np.array([1, -1]) / np.sqrt(2),
            np.array([1, 1j]) / np.sqrt(2),
            np.array([1, -1j]) / np.sqrt(2),
        ],
    )
    def test_all_six_single_qubit_stabilizer_states(self, sv):
        assert abs(stabilizer_renyi_entropy(np.array(sv, dtype=complex))) < 1e-9

    def test_bell_and_ghz(self):
        bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        assert abs(stabilizer_renyi_entropy(bell)) < 1e-9
        ghz = np.zeros(8, dtype=complex)
        ghz[0] = ghz[7] = 1 / np.sqrt(2)
        assert abs(stabilizer_renyi_entropy(ghz)) < 1e-9

    @pytest.mark.parametrize("seed", range(3))
    def test_random_clifford_orbit_states(self, seed):
        sim = StabilizerSimulator.random(3, depth=60, seed=seed)
        assert abs(stabilizer_renyi_entropy(sim.to_statevector())) < 1e-9


class TestMagicStates:
    def test_t_state_value(self):
        assert abs(stabilizer_renyi_entropy(_T_STATE) - np.log2(4 / 3)) < 1e-9

    def test_clifford_invariance(self):
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        S = np.array([[1, 0], [0, 1j]], dtype=complex)
        m0 = stabilizer_renyi_entropy(_T_STATE)
        assert abs(stabilizer_renyi_entropy(H @ _T_STATE) - m0) < 1e-9
        assert abs(stabilizer_renyi_entropy(S @ _T_STATE) - m0) < 1e-9

    @pytest.mark.parametrize("k", [1, 2, 3])
    def test_additivity_over_t_states(self, k):
        r = magic_of_t_states(k)
        assert abs(r["computed"] - r["analytic"]) < 1e-9
        assert abs(r["analytic"] - k * np.log2(4 / 3)) < 1e-12

    def test_nonstabilizer_has_positive_magic(self):
        psi = np.array([np.cos(0.3), np.sin(0.3) * np.exp(0.4j)], dtype=complex)
        assert stabilizer_renyi_entropy(psi) > 0.01

    def test_magic_survives_entangling_clifford(self):
        # CNOT (Clifford) on |T>|0> cannot create or destroy magic.
        CNOT = np.eye(4, dtype=complex)[[0, 1, 3, 2]]
        state = np.kron(np.array([1, 0], dtype=complex), _T_STATE)  # qubit0 = T
        m_before = stabilizer_renyi_entropy(state)
        m_after = stabilizer_renyi_entropy(CNOT @ state)
        assert abs(m_before - m_after) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
