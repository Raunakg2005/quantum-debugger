"""ZX-calculus (v3.4.0) -- verification tests.

Spiders, rewrite rules, gates, and phase gadgets are each checked against the exact matrix
semantics (rules hold up to the ZX scalar, accounted for where noted).
"""
import numpy as np
import pytest

from quantum_debugger.algorithms.zx_spiders import (
    z_spider_matrix, x_spider_matrix, spider_to_matrix, z_spider_tensor,
    is_hadamard_self_inverse, green_phase, red_phase, hadamard_matrix,
)
from quantum_debugger.algorithms.zx_rewrite import (
    spider_fusion_z, spider_fusion_multi, spider_fusion_x, identity_rule,
    color_change_rule, copy_rule, pi_copy_rule, hopf_rule,
)
from quantum_debugger.algorithms.zx_gates import (
    hadamard_gate, z_gate, x_gate, s_gate, t_gate, z_phase_gate, x_phase_gate,
    cnot_zx, cz_zx, gate_equals, cnot_zx_is_cnot, cz_zx_is_cz,
)
from quantum_debugger.algorithms.phase_gadgets import (
    rz, zz_phase_exact, zz_gadget, phase_gadget, phase_gadget_exact, gadget_matches_exact,
)


def test_z_spider_is_z_gate():
    assert np.allclose(z_spider_matrix(1, 1, np.pi), np.diag([1, -1]))
    assert np.allclose(green_phase(np.pi / 2), np.diag([1, 1j]))


def test_x_spider_is_x_gate():
    assert np.allclose(x_spider_matrix(1, 1, np.pi), [[0, 1], [1, 0]])
    assert gate_equals(red_phase(np.pi), np.array([[0, 1], [1, 0]], dtype=complex))


def test_hadamard_self_inverse():
    assert is_hadamard_self_inverse()
    assert np.allclose(hadamard_matrix() @ hadamard_matrix(), np.eye(2))


def test_z_copy_spider():
    C = z_spider_matrix(1, 2, 0.0)
    assert np.allclose(C[:, 0], [1, 0, 0, 0])   # |0> -> |00>
    assert np.allclose(C[:, 1], [0, 0, 0, 1])   # |1> -> |11>


def test_spider_fusion():
    assert spider_fusion_z(0.7, 1.1)
    assert spider_fusion_multi(0.7, 1.1)
    assert spider_fusion_x(0.5, 0.9)


def test_identity_and_copy_rules():
    assert identity_rule()
    assert copy_rule()


def test_color_change_rule():
    assert color_change_rule(2, 1, 0.6)
    assert color_change_rule(1, 3, 0.3)
    assert color_change_rule(1, 1, np.pi)


def test_pi_copy_rule():
    assert pi_copy_rule(1)
    assert pi_copy_rule(2)
    assert pi_copy_rule(3)


def test_hopf_rule():
    assert hopf_rule()


def test_zx_gates_match_unitaries():
    assert gate_equals(z_gate(), np.diag([1, -1]).astype(complex))
    assert gate_equals(x_gate(), np.array([[0, 1], [1, 0]], dtype=complex))
    assert gate_equals(s_gate(), np.diag([1, 1j]).astype(complex))
    assert gate_equals(t_gate(), np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex))
    assert gate_equals(z_phase_gate(0.5), np.diag([1, np.exp(0.5j)]).astype(complex))


def test_cnot_and_cz_from_zx():
    assert cnot_zx_is_cnot()
    assert cz_zx_is_cz()
    CNOT_le = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)
    assert gate_equals(cnot_zx(), CNOT_le)


def test_phase_gadget_matches_exponential():
    assert np.allclose(zz_gadget(0.8), zz_phase_exact(0.8))
    assert gadget_matches_exact(2, 0.8)
    assert gadget_matches_exact(3, 0.6)
    assert gadget_matches_exact(4, 1.1)


def test_rz_definition():
    assert np.allclose(rz(np.pi), np.diag([np.exp(-1j * np.pi / 2), np.exp(1j * np.pi / 2)]))
