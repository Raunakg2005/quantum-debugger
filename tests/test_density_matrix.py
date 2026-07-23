"""Tests for the density-matrix (open quantum systems) simulator."""

import numpy as np
import pytest

from quantum_debugger.density_matrix import (
    DensityMatrix,
    bit_flip,
    phase_flip,
    depolarizing,
    amplitude_damping,
    phase_damping,
)
from quantum_debugger.core.gates import GateLibrary

_H = GateLibrary.H
_X = GateLibrary.X
_CNOT = GateLibrary.CNOT


class TestBasics:
    def test_pure_state_purity_one(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        assert np.isclose(dm.purity(), 1.0)

    def test_probabilities(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_X, [1])  # |10> (qubit1=1)
        probs = dm.probabilities()
        assert np.isclose(probs[0b10], 1.0)

    def test_apply_unitary_matches_state_vector(self):
        from quantum_debugger.core.quantum_state import QuantumState

        st = QuantumState(2)
        st.apply_gate(_H, [0])
        st.apply_gate(_CNOT, [0, 1])
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        sv = st.state_vector
        assert np.allclose(dm.rho, np.outer(sv, sv.conj()))


class TestPartialTrace:
    def test_bell_reduced_is_maximally_mixed(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        red = dm.partial_trace([0])
        assert np.isclose(red.purity(), 0.5)
        assert np.allclose(red.probabilities(), [0.5, 0.5])


class TestChannels:
    def test_depolarizing_full_gives_maximally_mixed(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        dm.apply_channel(depolarizing(1.0), [0])
        assert np.isclose(dm.purity(), 0.5)

    def test_depolarizing_purity_decreases(self):
        purities = []
        for p in (0.0, 0.25, 0.5, 1.0):
            dm = DensityMatrix(1, state_vector=np.array([1, 1]) / np.sqrt(2))
            dm.apply_channel(depolarizing(p), [0])
            purities.append(dm.purity())
        assert purities[0] > purities[1] > purities[2] > purities[3]
        assert np.isclose(purities[0], 1.0) and np.isclose(purities[3], 0.5)

    def test_amplitude_damping_decays_excited_state(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_X, [0])  # |1>
        dm.apply_channel(amplitude_damping(1.0), [0])
        assert np.allclose(dm.probabilities(), [1.0, 0.0])  # fully decayed to |0>

    def test_bit_flip_and_phase_flip_are_valid_channels(self):
        for ch in (bit_flip(0.3), phase_flip(0.3), phase_damping(0.4)):
            total = sum(K.conj().T @ K for K in ch)
            assert np.allclose(total, np.eye(2))  # trace-preserving


class TestFidelity:
    def test_fidelity_identical_and_orthogonal(self):
        dm = DensityMatrix(1, state_vector=np.array([1, 1]) / np.sqrt(2))
        assert np.isclose(dm.fidelity(np.array([1, 1]) / np.sqrt(2)), 1.0)
        assert np.isclose(dm.fidelity(np.array([1, 0])), 0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
