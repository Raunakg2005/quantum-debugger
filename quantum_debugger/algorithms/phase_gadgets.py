"""
Phase gadgets: ZX diagrams for multi-qubit phase rotations.

A *phase gadget* is the ZX diagram that applies a phase depending on the parity of a set of qubits --
it realizes ``exp(-i (alpha/2) Z⊗Z⊗...⊗Z)``, the exponential of a Pauli-Z string. Phase gadgets are
the workhorse of ZX-based circuit optimization: strings of them commute and combine, exposing
cancellations a gate-level view hides. This module builds gadgets from a CNOT ladder plus a central
Z-rotation and verifies each against the exact matrix exponential.
"""

import numpy as np
from scipy.linalg import expm

from .zx_gates import cnot_zx
from .zx_spiders import z_spider_matrix

_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def _pauli_string_z(n):
    """The operator ``Z⊗Z⊗...⊗Z`` on ``n`` qubits."""
    out = np.eye(1, dtype=complex)
    for _ in range(n):
        out = np.kron(out, _Z)
    return out


def rz(alpha):
    """The single-qubit ``Rz(alpha) = exp(-i alpha Z / 2) = diag(e^{-i alpha/2}, e^{i alpha/2})``."""
    return np.diag([np.exp(-1j * alpha / 2), np.exp(1j * alpha / 2)]).astype(complex)


def zz_phase_exact(alpha):
    """The exact two-qubit ZZ-phase rotation ``exp(-i (alpha/2) Z⊗Z)`` -- the target of the two-qubit
    gadget."""
    return expm(-1j * (alpha / 2) * _pauli_string_z(2))


def zz_gadget(alpha):
    """
    The two-qubit phase gadget as a CNOT-ladder circuit: ``CNOT · (I ⊗ Rz(alpha)) · CNOT`` (little-
    endian, control qubit 0). Equals ``exp(-i (alpha/2) Z⊗Z)``.
    """
    CNOT = cnot_zx()
    mid = np.kron(rz(alpha), np.eye(2))     # Rz on qubit 1 (little-endian: kron(q1, q0))
    return CNOT @ mid @ CNOT


def phase_gadget_exact(n, alpha):
    """The exact ``n``-qubit phase gadget ``exp(-i (alpha/2) Z^{⊗n})``."""
    return expm(-1j * (alpha / 2) * _pauli_string_z(n))


def phase_gadget(n, alpha):
    """
    The ``n``-qubit phase gadget built from a CNOT ladder onto a single ancilla-free target: entangle
    all qubits onto qubit ``n-1`` with CNOTs, apply ``Rz(alpha)`` there, then uncompute. Equals
    ``exp(-i (alpha/2) Z^{⊗n})``.
    """
    dim = 2 ** n
    # build the CNOT ladder q0->q1->...->q(n-1) using full-space operators
    ladder = np.eye(dim, dtype=complex)
    for c in range(n - 1):
        ladder = _cnot_full(n, c, c + 1) @ ladder
    mid = _single_qubit_full(n, n - 1, rz(alpha))
    return _dagger(ladder) @ mid @ ladder


def gadget_matches_exact(n, alpha, atol=1e-9):
    """Verify the CNOT-ladder phase gadget equals the exact ``exp(-i (alpha/2) Z^{⊗n})``."""
    return bool(np.allclose(phase_gadget(n, alpha), phase_gadget_exact(n, alpha), atol=atol))


def _dagger(U):
    return np.asarray(U, dtype=complex).conj().T


def _single_qubit_full(n, q, U):
    """Embed a single-qubit gate ``U`` on qubit ``q`` of ``n`` (little-endian)."""
    ops = [np.eye(2, dtype=complex)] * n
    ops[q] = U
    out = np.eye(1, dtype=complex)
    for k in range(n - 1, -1, -1):          # little-endian: qubit 0 is the last kron factor
        out = np.kron(out, ops[k])
    return out


def _cnot_full(n, control, target):
    """CNOT between two qubits of ``n`` (little-endian), built from projectors."""
    dim = 2 ** n
    P0 = np.array([[1, 0], [0, 0]], dtype=complex)
    P1 = np.array([[0, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    term0 = [np.eye(2, dtype=complex)] * n
    term0[control] = P0
    term1 = [np.eye(2, dtype=complex)] * n
    term1[control] = P1
    term1[target] = X

    def build(ops):
        out = np.eye(1, dtype=complex)
        for k in range(n - 1, -1, -1):
            out = np.kron(out, ops[k])
        return out

    return build(term0) + build(term1)
