"""
Tests for the 2.8.0 measurement-based computing suite: graph states & stabilizers, local
complementation, one-way teleportation/rotations, causal flow, and the MBQC CNOT. Verified
to reproduce the intended circuit unitaries and stabilizer structure.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.graph_states import (
    graph_state, verify_stabilizers, linear_cluster_edges, cluster_2d_edges,
    complete_graph_edges, star_graph_edges, graph_state_entanglement,
    local_complementation, local_clifford_equivalent)
from quantum_debugger.algorithms.one_way_computing import (
    teleport_step, expected_step_unitary, mbqc_rotation, expected_rotation_unitary,
    xy_measurement_states, mbqc_identity, measurement_probability)
from quantum_debugger.algorithms.measurement_calculus import (
    causal_flow, verify_flow, has_flow, pattern_depth)
from quantum_debugger.algorithms.mbqc_two_qubit import (
    native_cz, hadamard_is_teleport, verify_cnot_decomposition, mbqc_cnot)

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.diag([1, -1]).astype(complex)


def _eq_phase(a, b, atol=1e-6):
    i = int(np.argmax(np.abs(b)))
    return abs(a[i]) > 1e-9 and np.allclose(a * (b[i] / a[i]), b, atol=atol)


class TestGraphStates:
    def test_stabilizers(self):
        for n, edges in [(3, [(0, 1), (1, 2)]), (4, linear_cluster_edges(4)),
                         (4, cluster_2d_edges(2, 2))]:
            assert verify_stabilizers(edges, n)

    def test_entanglement(self):
        assert graph_state_entanglement([], 3) < 1e-9
        assert graph_state_entanglement(complete_graph_edges(3), 3) > 0.9
        assert graph_state_entanglement(star_graph_edges(4), 4) > 0.9

    def test_local_complementation(self):
        edges = [(0, 1), (0, 2), (0, 3)]
        lc = local_complementation(edges, 0, 4)
        assert local_clifford_equivalent(edges, lc, 0, 4)


class TestOneWay:
    def test_teleport_step(self):
        rng = np.random.default_rng(0)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2); psi /= np.linalg.norm(psi)
        for phi in (0.0, 0.5, 1.3):
            for s in (0, 1):
                assert _eq_phase(teleport_step(psi, phi, s), expected_step_unitary(phi, s) @ psi)

    def test_chained_rotation(self):
        rng = np.random.default_rng(1)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2); psi /= np.linalg.norm(psi)
        phis, outs = [0.3, -0.7, 1.1], [0, 1, 0]
        assert _eq_phase(mbqc_rotation(psi, phis, outs), expected_rotation_unitary(phis, outs) @ psi)

    def test_measurement_states_and_prob(self):
        p, m = xy_measurement_states(0.7)
        assert abs(np.vdot(p, m)) < 1e-9
        psi = np.array([0.6, 0.8], dtype=complex)
        assert abs(measurement_probability(psi, 0.5, 0) - 0.5) < 1e-9

    def test_identity(self):
        rng = np.random.default_rng(2)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2); psi /= np.linalg.norm(psi)
        out = mbqc_identity(psi, (0, 0))
        assert any(_eq_phase(out, P @ psi) for P in (np.eye(2), _X, _Z, _X @ _Z))


class TestMeasurementCalculus:
    def test_linear_cluster_flow(self):
        edges = linear_cluster_edges(4)
        res = causal_flow(edges, [0], [3], 4)
        assert res is not None and res[0] == {0: 1, 1: 2, 2: 3}
        assert has_flow(edges, [0], [3], 4)
        assert pattern_depth(edges, [0], [3], 4) == 4

    def test_verify_flow(self):
        edges = linear_cluster_edges(3)
        f, order = causal_flow(edges, [0], [2], 3)
        assert verify_flow(edges, f, order, [2], 3)


class TestMBQCTwoQubit:
    def test_cnot_decomposition(self):
        assert hadamard_is_teleport()
        assert verify_cnot_decomposition()
        assert np.allclose(native_cz(), np.diag([1, 1, 1, -1]))

    def test_mbqc_cnot(self):
        CNOT = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)
        rng = np.random.default_rng(0)
        psi = rng.normal(size=4) + 1j * rng.normal(size=4); psi /= np.linalg.norm(psi)
        assert np.allclose(mbqc_cnot(psi), CNOT @ psi, atol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
