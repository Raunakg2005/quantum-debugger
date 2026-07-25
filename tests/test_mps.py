"""Tests for the matrix product state simulator."""

import numpy as np
import pytest

from quantum_debugger.mps import MPS
from quantum_debugger.core.quantum_state import apply_gate_tensor
from quantum_debugger.core.gates import GateLibrary

_Z = np.diag([1, -1]).astype(complex)
_X = GateLibrary.X
_H = GateLibrary.H
_CNOT = GateLibrary.CNOT


class TestRoundtrip:
    @pytest.mark.parametrize("n", [2, 3, 4, 5])
    def test_statevector_roundtrip(self, n):
        rng = np.random.default_rng(n)
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        rec = MPS.from_statevector(psi).to_statevector()
        assert abs(np.vdot(psi, rec)) ** 2 > 1 - 1e-10

    def test_zero_state(self):
        m = MPS.zero_state(4)
        sv = m.to_statevector()
        expected = np.zeros(16, dtype=complex)
        expected[0] = 1
        assert np.allclose(sv, expected)


class TestBondDimensions:
    def test_product_state_bond_one(self):
        m = MPS.zero_state(5)
        assert m.max_bond_dimension() == 1

    def test_ghz_bond_two(self):
        n = 6
        m = MPS.zero_state(n)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        assert m.max_bond_dimension() == 2

    def test_bond_dim_list_length(self):
        m = MPS.zero_state(5)
        assert len(m.bond_dimensions()) == 4


class TestGatesMatchStateVector:
    @pytest.mark.parametrize("q", range(4))
    def test_single_qubit_gate(self, q):
        rng = np.random.default_rng(q)
        psi = rng.normal(size=16) + 1j * rng.normal(size=16)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi)
        m.apply_single(_H, q)
        ref = apply_gate_tensor(np, psi, _H, [q], 4)
        assert np.allclose(m.to_statevector(), ref, atol=1e-10)

    @pytest.mark.parametrize("q", range(3))
    def test_two_qubit_gate(self, q):
        from scipy.stats import unitary_group

        rng = np.random.default_rng(q)
        psi = rng.normal(size=16) + 1j * rng.normal(size=16)
        psi = psi / np.linalg.norm(psi)
        G = unitary_group.rvs(4, random_state=q + 1)  # asymmetric 2-qubit gate
        m = MPS.from_statevector(psi)
        m.apply_two(G, q)
        ref = apply_gate_tensor(np, psi, G, [q, q + 1], 4)
        assert np.allclose(m.to_statevector(), ref, atol=1e-10)


class TestExpectation:
    def test_matches_state_vector(self):
        rng = np.random.default_rng(0)
        psi = rng.normal(size=16) + 1j * rng.normal(size=16)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi)
        for q in range(4):
            full = np.array([[1]], dtype=complex)
            for k in range(4):
                full = np.kron(_Z if k == q else np.eye(2, dtype=complex), full)
            ref = np.real(psi.conj() @ full @ psi)
            assert abs(m.expectation(_Z, q) - ref) < 1e-9

    def test_correlation(self):
        # Bell pair: <Z0 Z1> = 1.
        m = MPS.zero_state(2)
        m.apply_single(_H, 0)
        m.apply_two(_CNOT, 0)
        assert abs(m.correlation(_Z, 0, _Z, 1) - 1.0) < 1e-9


class TestScale:
    def test_large_ghz_low_bond(self):
        # A 100-qubit GHZ has bond dimension 2 -- impossible for a state vector.
        n = 100
        m = MPS.zero_state(n, max_bond=4)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        assert m.max_bond_dimension() == 2
        assert abs(m.norm() - 1.0) < 1e-9
        assert abs(m.correlation(_Z, 0, _Z, n - 1) - 1.0) < 1e-9  # perfectly correlated
        assert abs(m.expectation(_X, 0)) < 1e-9                    # <X> = 0

    def test_product_circuit_stays_bond_one(self):
        n = 50
        m = MPS.zero_state(n)
        for q in range(n):
            m.apply_single(_X, q)  # all-ones product state
        assert m.max_bond_dimension() == 1
        assert abs(m.expectation(_Z, 25) - (-1.0)) < 1e-9  # |1> -> <Z> = -1


class TestTruncation:
    def test_bond_capped_at_max(self):
        # A random circuit generates entanglement; the bond stays capped.
        from scipy.stats import unitary_group

        n = 8
        m = MPS.zero_state(n, max_bond=4)
        for layer in range(3):
            for q in range(n - 1):
                G = unitary_group.rvs(4, random_state=layer * n + q)
                m.apply_two(G, q)
        assert m.max_bond_dimension() <= 4


class TestSampling:
    def test_bell_only_correlated_outcomes(self):
        m = MPS.zero_state(2)
        m.apply_single(_H, 0)
        m.apply_two(_CNOT, 0)
        counts = m.sample(500, seed=1)
        assert set(counts) <= {"00", "11"}
        assert len(counts) == 2  # both appear

    def test_ghz_all_zero_or_all_one(self):
        n = 6
        m = MPS.zero_state(n)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        counts = m.sample(300, seed=2)
        assert set(counts) <= {"0" * n, "1" * n}

    def test_matches_born_distribution(self):
        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        shots = 40000
        counts = m.sample(shots, seed=1)
        max_err = 0.0
        for idx in range(2**n):
            bs = "".join(str((idx >> q) & 1) for q in range(n))
            emp = counts.get(bs, 0) / shots
            max_err = max(max_err, abs(emp - abs(psi[idx]) ** 2))
        assert max_err < 0.02  # within shot noise

    def test_product_state_deterministic(self):
        m = MPS.zero_state(3)
        m.apply_single(_X, 1)  # |010>
        assert m.sample(20, seed=0) == {"010": 20}

    def test_total_shots_conserved(self):
        m = MPS.zero_state(5)
        m.apply_single(_H, 0)
        assert sum(m.sample(137, seed=3).values()) == 137



class TestEntanglementEntropy:
    def test_matches_dense(self):
        from quantum_debugger.density_matrix import DensityMatrix

        rng = np.random.default_rng(0)
        n = 6
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=64)
        dm = DensityMatrix(state_vector=psi)
        ent = m.bond_entropies()
        for i in range(n - 1):
            assert abs(ent[i] - dm.entanglement_entropy(list(range(i + 1)))) < 1e-9

    def test_product_state_zero_entropy(self):
        m = MPS.zero_state(5)
        assert all(abs(s) < 1e-12 for s in m.bond_entropies())

    def test_ghz_one_bit_every_bond(self):
        n = 6
        m = MPS.zero_state(n)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        assert all(abs(s - 1.0) < 1e-9 for s in m.bond_entropies())

    def test_single_bond_accessor(self):
        m = MPS.zero_state(4)
        m.apply_single(_H, 0)
        m.apply_two(_CNOT, 0)
        m.apply_two(_CNOT, 1)
        m.apply_two(_CNOT, 2)  # GHZ
        assert abs(m.entanglement_entropy(1) - 1.0) < 1e-9

    def test_large_ghz_entropy_profile(self):
        # A 60-qubit GHZ has exactly 1 bit across every cut -- instant, no dense state.
        n = 60
        m = MPS.zero_state(n, max_bond=4)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        ent = m.bond_entropies()
        assert len(ent) == n - 1
        assert all(abs(s - 1.0) < 1e-9 for s in ent)

class TestOverlapFidelity:
    def test_overlap_matches_dense(self):
        rng = np.random.default_rng(0)
        n = 4
        a = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); a /= np.linalg.norm(a)
        b = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); b /= np.linalg.norm(b)
        ov = MPS.from_statevector(a).overlap(MPS.from_statevector(b))
        assert abs(ov - np.vdot(b, a)) < 1e-9

    def test_fidelity_matches_dense(self):
        rng = np.random.default_rng(1)
        n = 4
        a = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); a /= np.linalg.norm(a)
        b = rng.normal(size=2**n) + 1j * rng.normal(size=2**n); b /= np.linalg.norm(b)
        fid = MPS.from_statevector(a).fidelity(MPS.from_statevector(b))
        assert abs(fid - abs(np.vdot(b, a)) ** 2) < 1e-9

    def test_self_fidelity_is_one(self):
        m = MPS.zero_state(5)
        m.apply_single(_H, 0)
        m.apply_two(_CNOT, 0)
        assert abs(m.fidelity(m) - 1.0) < 1e-9

    def test_orthogonal_states_zero_overlap(self):
        a = MPS.zero_state(3)              # |000>
        b = MPS.zero_state(3); b.apply_single(_X, 0)  # |001>
        assert abs(a.overlap(b)) < 1e-12

    def test_large_ghz_self_fidelity(self):
        n = 40
        m = MPS.zero_state(n, max_bond=4)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        assert abs(m.fidelity(m) - 1.0) < 1e-9

    def test_mismatched_size_rejected(self):
        with pytest.raises(ValueError):
            MPS.zero_state(3).overlap(MPS.zero_state(4))

class TestLongRangeGates:
    @pytest.mark.parametrize("a,b", [(0, 2), (0, 4), (1, 3), (0, 3)])
    def test_matches_state_vector(self, a, b):
        from scipy.stats import unitary_group

        rng = np.random.default_rng(a * 5 + b)
        n = 5
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        G = unitary_group.rvs(4, random_state=a * 5 + b)
        m = MPS.from_statevector(psi, max_bond=64)
        m.apply_two_long_range(G, a, b)
        ref = apply_gate_tensor(np, psi, G, [a, b], n)
        assert np.allclose(m.to_statevector(), ref, atol=1e-9)

    def test_adjacent_delegates(self):
        rng = np.random.default_rng(0)
        psi = rng.normal(size=16) + 1j * rng.normal(size=16); psi /= np.linalg.norm(psi)
        m = MPS.from_statevector(psi)
        m.apply_two_long_range(_CNOT, 1, 2)
        ref = apply_gate_tensor(np, psi, _CNOT, [1, 2], 4)
        assert np.allclose(m.to_statevector(), ref, atol=1e-9)

    def test_long_range_bell(self):
        n = 10
        m = MPS.zero_state(n)
        m.apply_single(_H, 0)
        m.apply_two_long_range(_CNOT, 0, n - 1)
        assert abs(m.correlation(_Z, 0, _Z, n - 1) - 1.0) < 1e-9

    def test_reversed_order_rejected(self):
        with pytest.raises(ValueError):
            MPS.zero_state(4).apply_two_long_range(_CNOT, 3, 1)

class TestFromCircuit:
    def test_matches_state_vector(self):
        from quantum_debugger.core.circuit import QuantumCircuit

        qc = QuantumCircuit(5)
        qc.h(0); qc.cnot(0, 1); qc.cnot(3, 1); qc.x(2)
        qc.cnot(4, 2); qc.h(3); qc.cnot(2, 0)
        m = MPS.from_circuit(qc, max_bond=32)
        assert np.allclose(m.to_statevector(), qc.get_statevector().state_vector, atol=1e-9)

    def test_reversed_cnot(self):
        from quantum_debugger.core.circuit import QuantumCircuit

        qc = QuantumCircuit(3)
        qc.x(2); qc.cnot(2, 0)  # control > target
        m = MPS.from_circuit(qc)
        assert np.allclose(m.to_statevector(), qc.get_statevector().state_vector, atol=1e-9)

    def test_ghz_circuit_bond_two(self):
        from quantum_debugger.core.circuit import QuantumCircuit

        n = 8
        qc = QuantumCircuit(n)
        qc.h(0)
        for q in range(n - 1):
            qc.cnot(q, q + 1)
        m = MPS.from_circuit(qc, max_bond=4)
        assert m.max_bond_dimension() == 2

    def test_three_qubit_gate_rejected(self):
        from quantum_debugger.core.circuit import QuantumCircuit

        qc = QuantumCircuit(3)
        qc.toffoli(0, 1, 2)  # 8x8 gate -- must be decomposed first
        with pytest.raises(NotImplementedError):
            MPS.from_circuit(qc)

class TestPauliExpectation:
    def test_matches_dense_all_strings(self):
        from quantum_debugger.algorithms import pauli_term_matrix
        import itertools

        rng = np.random.default_rng(0)
        n = 4
        psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
        psi = psi / np.linalg.norm(psi)
        m = MPS.from_statevector(psi, max_bond=16)
        for labels in itertools.product("IXYZ", repeat=n):
            ps = "".join(labels)
            dense = np.real(psi.conj() @ pauli_term_matrix(ps) @ psi)
            assert abs(m.expectation_pauli(ps) - dense) < 1e-9

    def test_ghz_stabilizers(self):
        n = 20
        m = MPS.zero_state(n)
        m.apply_single(_H, 0)
        for q in range(n - 1):
            m.apply_two(_CNOT, q)
        assert abs(m.expectation_pauli("X" * n) - 1.0) < 1e-9        # X^n stabilizes GHZ
        assert abs(m.expectation_pauli("Z" + "I" * (n - 2) + "Z") - 1.0) < 1e-9

    def test_identity_string_is_one(self):
        m = MPS.zero_state(4)
        m.apply_single(_H, 0)
        assert abs(m.expectation_pauli("IIII") - 1.0) < 1e-9



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
