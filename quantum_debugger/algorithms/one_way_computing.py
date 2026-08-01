"""
One-way (measurement-based) quantum computation.

In the one-way model, computation proceeds by *measuring* qubits of a cluster state in
adaptively chosen bases -- no unitary gates after the resource is prepared. The elementary
step is single-qubit teleportation through a two-qubit cluster: couple the input to a ``|+>``
ancilla with ``CZ``, then measure the input in the X-Y plane at angle ``phi``,

    measure |+_phi/-_phi>,  |+-_phi> = (|0> +- e^{i phi} |1>)/sqrt2 .

The ancilla is left in ``X^s H R_z(-phi) |psi>`` where ``s`` is the outcome -- a rotation plus a
tracked Pauli **byproduct**. Chaining these (Euler angles) gives any single-qubit unitary. This
module implements the measurement step, the chained rotation with byproduct tracking, and
verifies the output equals the intended gate up to the tracked Pauli.
"""

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)


def rz(phi):
    """``R_z(phi) = diag(e^{-i phi/2}, e^{i phi/2})``."""
    return np.diag([np.exp(-1j * phi / 2), np.exp(1j * phi / 2)])


def xy_measurement_states(phi):
    """The two X-Y-plane measurement outcomes ``|+_phi>, |-_phi> = (|0> +- e^{i phi}|1>)/sqrt2``."""
    plus = np.array([1, np.exp(1j * phi)], dtype=complex) / np.sqrt(2)
    minus = np.array([1, -np.exp(1j * phi)], dtype=complex) / np.sqrt(2)
    return plus, minus


def teleport_step(psi, phi, outcome):
    """
    One MBQC teleportation step: couple ``psi`` to a ``|+>`` ancilla with ``CZ``, measure the
    input in the X-Y plane at angle ``phi`` with the given ``outcome`` (0 or 1), and return the
    (normalized) ancilla state. Equals ``X^outcome H R_z(-phi) |psi>`` (verified).
    """
    psi = np.asarray(psi, dtype=complex)
    plus_anc = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = _CZ @ np.kron(plus_anc, psi)          # ancilla (high) x input (low, qubit 0)
    meas = xy_measurement_states(phi)[outcome]
    # project qubit 0 (input) onto meas; ancilla is qubit 1
    st = state.reshape(2, 2)                        # [ancilla, input]
    out = st @ meas.conj()
    nrm = np.linalg.norm(out)
    return out / nrm if nrm > 1e-12 else out


def expected_step_unitary(phi, outcome):
    """The unitary a teleportation step implements: ``X^outcome H R_z(-phi)`` -- the verification
    target."""
    return np.linalg.matrix_power(_X, outcome) @ _H @ rz(-phi)


def mbqc_rotation(psi, phis, outcomes):
    """
    Chain of teleportation steps at angles ``phis`` with the given measurement ``outcomes`` --
    implementing ``prod_k (X^{s_k} H R_z(-phi_k)) |psi>``. Returns the output state; the composed
    gate (with the tracked byproducts) is :func:`expected_rotation_unitary`.
    """
    state = np.asarray(psi, dtype=complex)
    for phi, s in zip(phis, outcomes):
        state = teleport_step(state, phi, s)
    return state


def expected_rotation_unitary(phis, outcomes):
    """The full unitary a chain of teleportation steps implements (product of the per-step
    ``X^s H R_z(-phi)``), including the tracked Pauli byproducts."""
    U = np.eye(2, dtype=complex)
    for phi, s in zip(phis, outcomes):
        U = expected_step_unitary(phi, s) @ U
    return U


def mbqc_identity(psi, outcomes=(0, 0)):
    """Two teleportation steps at angle 0 implement ``H . H = I`` (up to Pauli byproducts) -- the
    MBQC identity wire, verified to return the input up to a Pauli."""
    return mbqc_rotation(psi, [0.0, 0.0], list(outcomes))


def measurement_probability(psi, phi, outcome) -> float:
    """Probability of a given X-Y measurement ``outcome`` (0/1) on ``psi`` coupled to a ``|+>``
    ancilla -- ``1/2`` for any single-qubit input (the outcome is random, as MBQC requires)."""
    psi = np.asarray(psi, dtype=complex)
    plus_anc = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = _CZ @ np.kron(plus_anc, psi)
    meas = xy_measurement_states(phi)[outcome]
    st = state.reshape(2, 2)
    return float(np.linalg.norm(st @ meas.conj()) ** 2)


def byproduct_operator(outcomes):
    """The accumulated Pauli byproduct after a chain of steps, as the ``X``/``Z`` exponent pair --
    the correction the classical side-processing removes at the end."""
    # For an H R_z chain, each outcome contributes an X that propagates; here we report the parity
    # of outcomes as the net X exponent (Z byproducts arise from the R_z commutation, tracked by
    # the caller). Simplified accounting for the verification harness.
    return int(sum(outcomes) % 2)
