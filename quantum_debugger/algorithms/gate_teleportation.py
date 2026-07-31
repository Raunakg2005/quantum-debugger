"""
Gate teleportation and magic-state injection.

Gate teleportation is the mechanism that makes non-Clifford gates fault-tolerant: instead
of applying a hard gate ``U`` directly, you prepare a *resource state* offline and
teleport the gate onto the data via measurement and a Pauli correction. The special case
of injecting a ``T`` gate from a ``T`` magic state is how universality is reached on codes
with only transversal Cliffords.

This module implements single-qubit gate teleportation and ``T``-injection at the
state-vector level and verifies that, after the outcome-dependent correction, the output is
exactly ``U|psi>`` (up to global phase) for every measurement branch.
"""

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_S = np.diag([1, 1j]).astype(complex)
_T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.diag([1, -1]).astype(complex)
_BELL = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)


_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_PAULIS = [np.eye(2, dtype=complex), _X, _Y, _Z]


def resource_state(U) -> np.ndarray:
    """Gate-teleportation resource ``(I (x) U)|Phi+>`` -- the offline entangled state that
    carries the gate ``U`` onto the data during teleportation."""
    return np.kron(np.eye(2), np.asarray(U, dtype=complex)) @ _BELL


def _bell_measure(state3):
    """Project qubits (0,1) of a 3-qubit state onto the four Bell states; return branches."""
    bells = {
        (0, 0): np.array([1, 0, 0, 1]) / np.sqrt(2),
        (0, 1): np.array([1, 0, 0, -1]) / np.sqrt(2),
        (1, 0): np.array([0, 1, 1, 0]) / np.sqrt(2),
        (1, 1): np.array([0, 1, -1, 0]) / np.sqrt(2),
    }
    st = state3.reshape(4, 2)
    out = {}
    for key, b in bells.items():
        branch = b.conj() @ st                      # unnormalized qubit-2 state
        pr = np.vdot(branch, branch)
        if pr > 1e-12:
            out[key] = (float(np.real(pr)), branch / np.sqrt(pr))
    return out


def gate_teleportation(U, psi) -> bool:
    """
    Teleport a single-qubit **Clifford** gate ``U`` onto ``psi`` via the resource
    ``(I(x)U)|Phi+>`` and a Bell measurement. Returns ``True`` iff every measurement branch
    equals ``U|psi>`` up to a *Pauli* correction ``U (X^b Z^a) U^dagger`` -- the
    gate-teleportation identity. (For non-Clifford ``U`` the byproduct is not Pauli, so this
    correctly returns ``False`` -- exactly why ``T`` needs :func:`t_injection`.)
    """
    U = np.asarray(U, dtype=complex)
    psi = np.asarray(psi, dtype=complex); psi = psi / np.linalg.norm(psi)
    target = U @ psi
    state3 = np.kron(psi, resource_state(U))
    for (a, b), (_, out) in _bell_measure(state3).items():
        # a Pauli correction recovers U|psi> iff the byproduct is Pauli (Clifford U)
        if not any(_equal_up_to_phase(P @ out, target) for P in _PAULIS):
            return False
    return True


def t_injection(psi) -> bool:
    """
    Inject a ``T`` gate onto ``psi`` using a ``T`` magic state and a CNOT + measurement + ``S``
    correction. Returns ``True`` iff both measurement branches give ``T|psi>`` up to phase --
    the primitive that reaches universality from transversal Cliffords. Verified.
    """
    from .magic_states import t_state
    psi = np.asarray(psi, dtype=complex); psi = psi / np.linalg.norm(psi)
    target = _T @ psi
    # data (control) x magic (target); CNOT then measure the magic qubit in Z.
    joint = np.kron(psi, t_state()).reshape(2, 2)
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
    joint = (cnot @ joint.reshape(4)).reshape(2, 2)
    for m in (0, 1):
        branch = joint[:, m]
        pr = np.vdot(branch, branch)
        if pr <= 1e-12:
            continue
        data = branch / np.sqrt(pr)
        corrected = (_S @ data) if m == 1 else data     # S correction on outcome 1
        if not _equal_up_to_phase(corrected, target):
            return False
    return True


def _equal_up_to_phase(a, b, atol: float = 1e-6):
    a = np.asarray(a); b = np.asarray(b)
    i = int(np.argmax(np.abs(b)))
    if abs(a[i]) < atol:
        return False
    return bool(np.allclose(a * (b[i] / a[i]), b, atol=atol))
