"""
Tests for the 2.0.0 compilation suite: the circuit IR & equivalence oracle, peephole
optimization, commutation, routing / SWAP networks, gate templates, two-qubit CNOT
counts, and scheduling. Every rewrite is checked to preserve the circuit's unitary.
"""

import numpy as np
import pytest
from scipy.stats import unitary_group

from quantum_debugger.algorithms.circuit_ir import (
    op, circuit_unitary, circuits_equivalent, gate_count, two_qubit_count)
from quantum_debugger.algorithms.gate_optimization import (
    cancel_inverses, remove_identities, merge_rotations, optimize_circuit)
from quantum_debugger.algorithms.commutation import (
    operations_commute, commute_forward, commutation_graph)
from quantum_debugger.algorithms.qubit_routing import (
    coupling_map, is_executable, permutation_matrix, swap_network, route_linear, SWAP)
from quantum_debugger.algorithms.gate_templates import (
    swap_decomposition, controlled_z_decomposition, toffoli_decomposition,
    toffoli_matrix, verify_template)
from quantum_debugger.algorithms.two_qubit_synthesis import (
    makhlin_invariants, is_local, locally_equivalent, cnot_count)
from quantum_debugger.algorithms.scheduling import (
    asap_layers, circuit_depth, circuit_parallelism, flatten_layers)
from quantum_debugger.algorithms.circuit_ir import _embed

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_CNOT = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)
_SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
_iSWAP = np.array([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, 1]], dtype=complex)


def _Rz(t):
    return np.diag([np.exp(-1j * t / 2), np.exp(1j * t / 2)])


class TestCircuitIR:
    def test_equivalence(self):
        c = [op(_H, [0]), op(_CNOT, [0, 1])]
        assert circuits_equivalent(c, c, 2)
        assert circuit_unitary(c, 2).shape == (4, 4)
        assert gate_count(c) == 2 and two_qubit_count(c) == 1


class TestOptimization:
    def test_cancel_inverses(self):
        c = [op(_H, [0]), op(_H, [0]), op(_X, [1])]
        o = cancel_inverses(c)
        assert gate_count(o) == 1 and circuits_equivalent(c, o, 2)

    def test_merge_rotations(self):
        c = [op(_Rz(0.3), [0]), op(_Rz(0.4), [0])]
        o = merge_rotations(c)
        assert gate_count(o) == 1 and circuits_equivalent(c, o, 1)

    def test_full_optimize(self):
        c = [op(_H, [0]), op(_H, [0]), op(_Rz(0.3), [1]), op(_Rz(-0.3), [1]),
             op(_CNOT, [0, 1]), op(np.eye(2), [0])]
        o = optimize_circuit(c)
        assert gate_count(o) < gate_count(c) and circuits_equivalent(c, o, 2)


class TestCommutation:
    def test_commute(self):
        assert operations_commute(op(_X, [0]), op(_H, [1]), 2)      # disjoint

    def test_commute_forward(self):
        c = [op(_H, [1]), op(_X, [0])]
        cf = commute_forward(c, 1, 2)
        assert circuits_equivalent(c, cf, 2) and cf[0][1] == [0]

    def test_commutation_graph(self):
        G = commutation_graph([op(_X, [0]), op(_H, [1])], 2)
        assert G[0, 1] and G[1, 0]


class TestRouting:
    def test_route_linear(self):
        circ = [op(_H, [0]), op(_CNOT, [0, 3]), op(_CNOT, [1, 2])]
        routed = route_linear(circ, 4)
        line = coupling_map([(0, 1), (1, 2), (2, 3)], 4)
        assert not is_executable(circ, line)
        assert is_executable(routed, line)
        assert circuits_equivalent(circ, routed, 4)

    def test_swap_network(self):
        for perm in ([2, 0, 3, 1], [3, 2, 1, 0]):
            swaps = swap_network(perm)
            U = np.eye(16, dtype=complex)
            for i, j in swaps:
                U = _embed(SWAP, [i, j], 4) @ U
            assert np.allclose(U, permutation_matrix(perm, 4), atol=1e-9)
            assert all(abs(i - j) == 1 for i, j in swaps)


class TestTemplates:
    def test_swap(self):
        assert verify_template(swap_decomposition(), _SWAP, 2)

    def test_cz(self):
        assert verify_template(controlled_z_decomposition(), _CZ, 2)

    def test_toffoli(self):
        assert verify_template(toffoli_decomposition(), toffoli_matrix(), 3)


class TestSynthesis:
    def test_cnot_counts(self):
        assert cnot_count(np.eye(4)) == 0
        assert cnot_count(np.kron(_H, _H)) == 0
        assert cnot_count(_CNOT) == 1
        assert cnot_count(_CZ) == 1
        assert cnot_count(_iSWAP) == 2
        assert cnot_count(_SWAP) == 3
        assert all(cnot_count(unitary_group.rvs(4, random_state=s)) == 3 for s in range(3))

    def test_local_and_equivalence(self):
        assert is_local(np.kron(_H, _H)) and not is_local(_CNOT)
        assert locally_equivalent(_CNOT, _CZ) and not locally_equivalent(_CNOT, _SWAP)


class TestScheduling:
    def test_depth_and_parallelism(self):
        c = [op(_H, [0]), op(_H, [1]), op(_CNOT, [0, 1]), op(_X, [0]), op(_X, [1])]
        assert circuit_depth(c, 2) == 3
        assert abs(circuit_parallelism(c, 2) - 5 / 3) < 1e-9

    def test_schedule_preserves_unitary(self):
        c = [op(_H, [0]), op(_H, [1]), op(_CNOT, [0, 1]), op(_X, [0])]
        assert circuits_equivalent(c, flatten_layers(asap_layers(c, 2)), 2)

    def test_serial_depth(self):
        assert circuit_depth([op(_H, [0]), op(_X, [0]), op(_H, [0])], 1) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
