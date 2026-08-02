"""
Standard gates as ZX diagrams.

Every Clifford+T gate has a ZX representation built from spiders: phase gates are one-legged Z/X
spiders, and the two-qubit entanglers are spiders joined by wires. Because ZX diagrams denote their
matrices only up to a non-zero scalar, this module reconstructs each gate's exact unitary (fixing
the scalar) and verifies it against the textbook matrix. The little-endian convention (qubit 0 = the
least-significant bit) matches the rest of the library.
"""

import numpy as np

from .zx_spiders import (
    z_spider_matrix, x_spider_matrix, z_spider_tensor, x_spider_tensor, hadamard_matrix,
)

_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_CNOT_LE = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)


def hadamard_gate():
    """The Hadamard gate (the ZX Hadamard box)."""
    return hadamard_matrix()


def z_phase_gate(phase):
    """A Z-phase gate ``Z(1,1,phase) = diag(1, e^{i phase})`` -- Rz up to global phase."""
    return z_spider_matrix(1, 1, phase)


def x_phase_gate(phase):
    """An X-phase gate ``X(1,1,phase)`` -- Rx up to global phase."""
    return x_spider_matrix(1, 1, phase)


def z_gate():
    """Pauli Z as the ``Z(1,1,pi)`` spider."""
    return z_spider_matrix(1, 1, np.pi)


def x_gate():
    """Pauli X as the ``X(1,1,pi)`` spider."""
    return x_spider_matrix(1, 1, np.pi)


def s_gate():
    """The phase gate ``S = Z(1,1,pi/2)``."""
    return z_spider_matrix(1, 1, np.pi / 2)


def t_gate():
    """The ``T = Z(1,1,pi/4)`` gate."""
    return z_spider_matrix(1, 1, np.pi / 4)


def cnot_zx():
    """
    CNOT (control = qubit 0, target = qubit 1) as a ZX diagram: a ``Z(1,2,0)`` copy spider on the
    control joined by one wire to an ``X(2,1,0)`` spider on the target. The diagram equals CNOT up to
    a ``1/sqrt(2)`` scalar, which is restored here. Little-endian.
    """
    Z = z_spider_tensor(1, 2, 0.0)          # [ci, co, w]
    X = x_spider_tensor(2, 1, 0.0)          # [w, ti, to]
    R = np.einsum('a b w, w c d -> a b c d', Z, X)      # [ci, co, ti, to]
    M = np.transpose(R, (3, 1, 2, 0)).reshape(4, 4)     # little-endian [to,co,ti,ci]
    return np.sqrt(2) * M


def cz_zx():
    """
    CZ as a ZX diagram: two ``Z(1,2,0)`` spiders joined by a Hadamard edge. Symmetric in its qubits;
    equals ``diag(1,1,1,-1)`` up to a scalar, restored here.
    """
    H = hadamard_matrix()
    Z0 = z_spider_tensor(1, 2, 0.0)         # [in0, out0, w0]
    Z1 = z_spider_tensor(1, 2, 0.0)         # [in1, out1, w1]
    R = np.einsum('a b i, c d j, i j -> a b c d', Z0, Z1, H)   # [in0,out0,in1,out1]
    M = np.transpose(R, (1, 3, 0, 2)).reshape(4, 4)     # [out0,out1,in0,in1]
    return np.sqrt(2) * M


def gate_equals(U, target, atol=1e-9):
    """True iff ``U`` equals ``target`` up to a global phase (``|Tr(target^dagger U)| = d``)."""
    U = np.asarray(U, dtype=complex)
    target = np.asarray(target, dtype=complex)
    d = U.shape[0]
    return bool(np.isclose(abs(np.trace(target.conj().T @ U)), d, atol=atol))


def cnot_zx_is_cnot(atol=1e-9):
    """Verify the ZX CNOT diagram equals the CNOT unitary."""
    return gate_equals(cnot_zx(), _CNOT_LE, atol=atol)


def cz_zx_is_cz(atol=1e-9):
    """Verify the ZX CZ diagram equals the CZ unitary."""
    return gate_equals(cz_zx(), _CZ, atol=atol)
