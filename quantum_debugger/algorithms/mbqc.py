"""
Measurement-based quantum computation (one-bit teleportation)

The opposite of the circuit model: instead of applying gates, you prepare a fixed
entangled resource and *measure*. The elementary step teleports a rotation onto a
fresh qubit.

Take a two-qubit cluster ``CZ (|+> x |psi>)`` (input on qubit 0, ancilla ``|+>`` on
qubit 1) and measure qubit 0 in the tilted basis

    |+_alpha> = (|0> + e^{i alpha} |1>) / sqrt(2)   (outcome 0),
    |-_alpha> = (|0> - e^{i alpha} |1>) / sqrt(2)   (outcome 1).

The ancilla is left in

    |out> = X^s H Rz(-alpha) |psi>,

where ``s`` is the measurement outcome and ``Rz(theta) = diag(e^{-i theta/2},
e^{i theta/2})``. The random ``X^s`` byproduct is the price of measurement; applying
it as a classically-conditioned correction makes the step a *deterministic* gate
``H Rz(-alpha)``. Chaining such steps (with feed-forward on the byproducts) realizes
any single-qubit rotation, and adding a second measured row realizes entangling
gates -- this primitive is universal.
"""

import numpy as np

from ..density_matrix import _embed
from ..core.gates import GateLibrary

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)


def _rz(theta):
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
    )


def cluster_pair(psi_in) -> np.ndarray:
    """
    The two-qubit cluster state ``CZ (|+>_ancilla x |psi>_input)`` with the input on
    qubit 0 and the ``|+>`` ancilla on qubit 1 (little-endian). Returns the 4-dim
    state vector.
    """
    psi = np.asarray(psi_in, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    return _CZ @ np.kron(plus, psi)


def mbqc_rotation(psi_in, alpha: float, seed: int = 0, correct: bool = True) -> dict:
    """
    One measurement-based step: measure qubit 0 of the cluster in the ``alpha``-tilted
    basis and read the rotated state off the ancilla.

    With ``correct=True`` the ``X^s`` byproduct is undone (classically-conditioned on
    the outcome), so the ancilla holds exactly ``H Rz(-alpha) |psi>`` *deterministically*
    -- a genuine gate enacted purely by measurement. With ``correct=False`` the raw
    ``X^s H Rz(-alpha) |psi>`` is returned.

    Returns dict with:
      * ``output``   -- the ancilla state vector (2-dim)
      * ``outcome``  -- the measurement result ``s`` (0 or 1)
      * ``ideal``    -- ``H Rz(-alpha)|psi>`` (or ``X^s`` times it if uncorrected)
      * ``fidelity`` -- overlap of ``output`` with ``ideal`` (1.0)
    """
    psi = np.asarray(psi_in, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    state = cluster_pair(psi)

    rng = np.random.default_rng(seed)
    basis0 = np.array([1, np.exp(1j * alpha)], dtype=complex) / np.sqrt(2)
    P0 = _embed(np.outer(basis0, basis0.conj()), [0], 2)
    p0 = float(np.real(state.conj() @ P0 @ state))
    outcome = 0 if rng.random() < p0 else 1

    tilt = 1 if outcome == 0 else -1
    proj_vec = np.array([1, tilt * np.exp(1j * alpha)], dtype=complex) / np.sqrt(2)
    P = _embed(np.outer(proj_vec, proj_vec.conj()), [0], 2)
    collapsed = P @ state
    collapsed = collapsed / np.linalg.norm(collapsed)

    # Ancilla (qubit 1) reduced pure state.
    rho1 = np.tensordot(
        collapsed.reshape(2, 2), collapsed.reshape(2, 2).conj(), axes=([1], [1])
    )
    vals, vecs = np.linalg.eigh(rho1)
    output = vecs[:, -1] * np.sqrt(vals[-1])

    gate = _H @ _rz(-alpha)
    if correct and outcome == 1:
        output = _X @ output
        ideal = gate @ psi
    elif not correct:
        ideal = np.linalg.matrix_power(_X, outcome) @ gate @ psi
    else:
        ideal = gate @ psi

    # Fix the global phase for a clean state comparison.
    phase = np.vdot(ideal, output)
    if abs(phase) > 1e-12:
        output = output * np.conj(phase) / abs(phase)

    fidelity = float(abs(np.vdot(ideal / np.linalg.norm(ideal),
                                 output / np.linalg.norm(output))) ** 2)
    return {
        "output": output,
        "outcome": outcome,
        "ideal": ideal,
        "fidelity": fidelity,
    }
