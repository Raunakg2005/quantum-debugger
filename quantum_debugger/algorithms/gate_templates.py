"""
Gate-template decompositions.

Hardware exposes only a small native gate set (say ``CNOT`` plus single-qubit gates), so
high-level gates are expanded via fixed *templates*. The classics:

* **SWAP = 3 CNOTs** -- the identity behind routing cost.
* **Toffoli (CCX)** -- the standard 6-CNOT + ``T``/``T^dagger`` + ``H`` decomposition into
  Clifford+T, the gate that makes reversible classical logic possible.
* **Controlled-Z = H . CNOT . H** on the target.

Each template returns an IR sub-circuit, and this module verifies that its composed unitary
equals the gate it replaces.
"""

import numpy as np

from .circuit_ir import op, circuit_unitary

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
_Td = np.diag([1, np.exp(-1j * np.pi / 4)]).astype(complex)
# Little-endian CNOT (control = qubits[0], target = qubits[1]): flips the target bit when
# the control bit is 1, i.e. swaps basis indices 1 <-> 3.
_CNOT = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)


def swap_decomposition(q0=0, q1=1):
    """SWAP as three alternating CNOTs -- ``CNOT(a,b) CNOT(b,a) CNOT(a,b)``. Verified equal to
    the SWAP gate."""
    return [op(_CNOT, [q0, q1]), op(_CNOT, [q1, q0]), op(_CNOT, [q0, q1])]


def controlled_z_decomposition(control=0, target=1):
    """Controlled-Z as ``H(target) . CNOT . H(target)``. Verified equal to CZ."""
    return [op(_H, [target]), op(_CNOT, [control, target]), op(_H, [target])]


def toffoli_decomposition(c0=0, c1=1, target=2):
    """
    Toffoli (CCX) in the standard 6-CNOT Clifford+T template. Returns the IR sub-circuit;
    verified to equal the Toffoli unitary. Uses controls ``c0, c1`` and ``target``.
    """
    return [
        op(_H, [target]),
        op(_CNOT, [c1, target]), op(_Td, [target]),
        op(_CNOT, [c0, target]), op(_T, [target]),
        op(_CNOT, [c1, target]), op(_Td, [target]),
        op(_CNOT, [c0, target]), op(_T, [c1]), op(_T, [target]),
        op(_H, [target]),
        op(_CNOT, [c0, c1]), op(_T, [c0]), op(_Td, [c1]),
        op(_CNOT, [c0, c1]),
    ]


def toffoli_matrix() -> np.ndarray:
    """The 8x8 Toffoli (CCX) unitary in little-endian convention (controls 0,1; target 2):
    flips the target when both controls are 1, i.e. swaps indices 3 (``q0q1=11,q2=0``) and 7
    (``q0q1=11,q2=1``)."""
    T = np.eye(8, dtype=complex)
    T[[3, 7]] = T[[7, 3]]
    return T


def verify_template(sub_circuit, target_matrix, n_qubits: int, atol: float = 1e-9) -> bool:
    """True iff a template sub-circuit's composed unitary equals ``target_matrix`` up to a
    global phase."""
    U = circuit_unitary(sub_circuit, n_qubits)
    V = np.asarray(target_matrix, dtype=complex)
    i = np.unravel_index(np.argmax(np.abs(V)), V.shape)
    if abs(U[i]) < atol:
        return False
    return bool(np.allclose(U * (V[i] / U[i]), V, atol=atol))
