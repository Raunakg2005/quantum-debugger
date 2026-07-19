"""Tests for the Clifford/stabilizer simulator."""

import numpy as np
import pytest

from quantum_debugger.stabilizer import (
    StabilizerSimulator,
    stabilizer_to_pauli_matrix,
)
from quantum_debugger.core.quantum_state import QuantumState
from quantum_debugger.core.gates import GateLibrary

_H = GateLibrary.H
_CNOT = GateLibrary.CNOT
_S = np.array([[1, 0], [0, 1j]], dtype=complex)


class TestGHZ:
    @pytest.mark.parametrize("seed", range(10))
    def test_measurements_perfectly_correlated(self, seed):
        sim = StabilizerSimulator(5, seed=seed)
        sim.h(0)
        for q in range(4):
            sim.cnot(0, q + 1)
        outs = sim.measure_all()
        assert len(set(outs)) == 1  # all 0 or all 1

    def test_bell_stabilizers(self):
        sim = StabilizerSimulator(2, seed=0)
        sim.h(0)
        sim.cnot(0, 1)
        signs_paulis = sim.stabilizers()
        paulis = {ps for _, ps in signs_paulis}
        # Bell state is stabilized by XX and ZZ.
        assert "XX" in paulis and "ZZ" in paulis


class TestAgainstStateVector:
    @pytest.mark.parametrize("seed", range(20))
    def test_stabilizers_are_plus_one_eigenstates(self, seed):
        n = 4
        rng = np.random.default_rng(seed)
        sim = StabilizerSimulator(n, seed=seed)
        st = QuantumState(n)
        for _ in range(25):
            g = rng.integers(3)
            if g == 0:
                q = int(rng.integers(n))
                sim.h(q)
                st.apply_gate(_H, [q])
            elif g == 1:
                q = int(rng.integers(n))
                sim.s(q)
                st.apply_gate(_S, [q])
            else:
                a, b = (int(x) for x in rng.choice(n, 2, replace=False))
                sim.cnot(a, b)
                st.apply_gate(_CNOT, [a, b])
        sv = st.state_vector
        for sign, ps in sim.stabilizers():
            M = stabilizer_to_pauli_matrix(sign, ps)
            assert np.isclose(np.real(np.vdot(sv, M @ sv)), 1.0, atol=1e-9)


class TestMeasurement:
    def test_deterministic_repeat(self):
        sim = StabilizerSimulator(3, seed=1)
        sim.h(0)
        sim.cnot(0, 1)
        sim.cnot(1, 2)
        first = sim.measure(0)
        assert sim.measure(0) == first  # repeated measurement is deterministic
        assert sim.measure(1) == first  # GHZ correlation

    def test_computational_basis_state(self):
        sim = StabilizerSimulator(3, seed=0)
        sim.x_gate(1)  # |010>
        assert sim.measure_all() == [0, 1, 0]

    def test_pauli_gates_phases(self):
        # Z on |+> flips it to |->, whose X-stabilizer sign is -1.
        sim = StabilizerSimulator(1, seed=0)
        sim.h(0)
        sim.z_gate(0)
        sign, ps = sim.stabilizers()[0]
        assert ps == "X" and sign == -1


class TestScaling:
    def test_large_ghz_is_fast(self):
        sim = StabilizerSimulator(200, seed=2)
        sim.h(0)
        for q in range(199):
            sim.cnot(0, q + 1)
        outs = sim.measure_all()
        assert len(set(outs)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
