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


class TestExpectation:
    def test_bell_expectations(self):
        sim = StabilizerSimulator(2)
        sim.h(0)
        sim.cnot(0, 1)
        assert sim.expectation_value("XX") == 1
        assert sim.expectation_value("ZZ") == 1
        assert sim.expectation_value("YY") == -1
        assert sim.expectation_value("XZ") == 0  # anticommutes with a stabilizer

    @pytest.mark.parametrize("seed", range(10))
    def test_matches_state_vector(self, seed):
        n = 3
        rng = np.random.default_rng(seed)
        sim = StabilizerSimulator(n, seed=seed)
        st = QuantumState(n)
        for _ in range(20):
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
        for _ in range(4):
            ps = "".join(rng.choice(["I", "X", "Y", "Z"]) for _ in range(n))
            exp_sv = float(np.real(np.vdot(sv, stabilizer_to_pauli_matrix(1, ps) @ sv)))
            assert abs(sim.expectation_value(ps) - exp_sv) < 1e-9

    def test_s_dagger_inverts_s(self):
        # S then S-dagger leaves |+> stabilized by +X.
        sim = StabilizerSimulator(1)
        sim.h(0)
        sim.s(0)
        sim.s_dagger(0)
        assert sim.stabilizers() == [(1, "X")]


class TestToStatevector:
    def test_bell(self):
        sim = StabilizerSimulator(2)
        sim.h(0)
        sim.cnot(0, 1)
        expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        sv = sim.to_statevector()
        assert abs(np.vdot(expected, sv)) ** 2 > 1 - 1e-9

    @pytest.mark.parametrize("seed", range(8))
    def test_matches_state_vector(self, seed):
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
        assert abs(np.vdot(sim.to_statevector(), st.state_vector)) ** 2 > 1 - 1e-9


class TestRandomClifford:
    @pytest.mark.parametrize("seed", range(5))
    def test_produces_valid_stabilizer_state(self, seed):
        sim = StabilizerSimulator.random(4, depth=40, seed=seed)
        assert len(sim.stabilizers()) == 4
        assert np.isclose(np.linalg.norm(sim.to_statevector()), 1.0)

    def test_scales(self):
        sim = StabilizerSimulator.random(120, depth=400, seed=1)
        assert sim.n == 120  # instant, far beyond state-vector reach


class TestGraphState:
    def test_line_graph_stabilizers(self):
        sim = StabilizerSimulator.graph(3, [(0, 1), (1, 2)])
        paulis = {ps for _, ps in sim.stabilizers()}
        assert paulis == {"XZI", "ZXZ", "IZX"}

    def test_matches_state_vector_graph_state(self):
        from quantum_debugger.algorithms import graph_state as sv_graph_state

        edges = [(0, 1), (1, 2), (2, 0)]
        sim = StabilizerSimulator.graph(3, edges)
        fid = abs(np.vdot(sim.to_statevector(), sv_graph_state(edges, 3))) ** 2
        assert fid > 1 - 1e-9

    def test_large_ring_is_instant(self):
        n = 300
        sim = StabilizerSimulator.graph(n, [(i, (i + 1) % n) for i in range(n)])
        # Node 0's graph stabilizer X_0 Z_1 Z_{n-1} has eigenvalue +1.
        ps = "".join(
            "X" if q == 0 else ("Z" if q in (1, n - 1) else "I") for q in range(n)
        )
        assert sim.expectation_value(ps) == 1


class TestSampling:
    def test_ghz_sample_only_all_zero_or_all_one(self):
        sim = StabilizerSimulator(3, seed=0)
        sim.h(0)
        sim.cnot(0, 1)
        sim.cnot(1, 2)
        counts = sim.sample(500, seed=1)
        assert set(counts) <= {"000", "111"}
        assert len(counts) == 2  # both outcomes appear

    def test_sampling_does_not_disturb_state(self):
        sim = StabilizerSimulator(2, seed=0)
        sim.h(0)
        sim.cnot(0, 1)
        sim.sample(50, seed=1)
        # Original still Bell (its stabilizers are intact).
        assert set(ps for _, ps in sim.stabilizers()) == {"XX", "ZZ"}

    def test_computational_basis_deterministic(self):
        sim = StabilizerSimulator(2, seed=0)
        sim.x_gate(0)  # |10> (qubit 0 = 1)
        assert sim.sample(20, seed=3) == {"10": 20}


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


class TestStabilizerEntanglementEntropy:
    def test_bell_is_one_bit(self):
        sim = StabilizerSimulator(2, seed=0)
        sim.h(0)
        sim.cnot(0, 1)
        assert abs(sim.entanglement_entropy([0]) - 1.0) < 1e-12

    def test_product_state_zero(self):
        sim = StabilizerSimulator(3, seed=0)
        sim.h(0)
        sim.h(1)  # all product
        assert abs(sim.entanglement_entropy([0, 1])) < 1e-12

    def test_ghz_cut_is_one_bit(self):
        sim = StabilizerSimulator(5, seed=0)
        sim.h(0)
        for q in range(4):
            sim.cnot(0, q + 1)
        # Any nontrivial cut of a GHZ state has exactly 1 bit of entanglement.
        assert abs(sim.entanglement_entropy([0, 1]) - 1.0) < 1e-12
        assert abs(sim.entanglement_entropy([0]) - 1.0) < 1e-12

    @pytest.mark.parametrize("seed", range(8))
    def test_matches_dense_entanglement_entropy(self, seed):
        from quantum_debugger.density_matrix import DensityMatrix

        n = 5
        sim = StabilizerSimulator.random(n, depth=60, seed=seed)
        dm = DensityMatrix(state_vector=sim.to_statevector())
        for region in ([0], [0, 1], [0, 1, 2], [2, 4]):
            tab = sim.entanglement_entropy(region)
            dense = dm.entanglement_entropy(region)
            assert abs(tab - dense) < 1e-9

    def test_entropy_is_integer_bits(self):
        sim = StabilizerSimulator.random(6, depth=80, seed=3)
        for region in ([0], [0, 1, 2], [1, 3, 5]):
            s = sim.entanglement_entropy(region)
            assert abs(s - round(s)) < 1e-12

    def test_scales_to_large_systems(self):
        # 200-qubit GHZ: dense entanglement entropy is impossible; the tableau is instant.
        n = 200
        sim = StabilizerSimulator(n, seed=1)
        sim.h(0)
        for q in range(n - 1):
            sim.cnot(0, q + 1)
        assert abs(sim.entanglement_entropy(list(range(100))) - 1.0) < 1e-12

    def test_full_and_empty_region(self):
        sim = StabilizerSimulator.random(4, depth=40, seed=2)
        assert abs(sim.entanglement_entropy([])) < 1e-12
        assert abs(sim.entanglement_entropy([0, 1, 2, 3])) < 1e-12  # whole = pure
