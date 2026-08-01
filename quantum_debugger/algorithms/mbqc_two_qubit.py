"""
Two-qubit gates in measurement-based computing.

The entangling power of the one-way model comes for free: the controlled-``Z`` is the *native*
operation, applied simply by having an edge in the cluster graph. Every other gate is built
from ``CZ`` plus single-qubit teleportation (measurements). In particular the CNOT decomposes as

    CNOT_{c,t} = (I (x) H) . CZ_{c,t} . (I (x) H),

so an MBQC CNOT is a native cluster bond sandwiched between two Hadamard teleportations on the
target wire. This module builds the native ``CZ``, the Hadamard-by-measurement, and verifies the
CNOT decomposition and the MBQC realization of both against the exact gates.
"""

import numpy as np

from .one_way_computing import teleport_step, expected_step_unitary

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_CZ = np.diag([1, 1, 1, -1]).astype(complex)
# CNOT with control = qubit 0 (low), target = qubit 1 (high): flips the high bit when the low
# bit is 1, i.e. swaps basis indices 1 <-> 3 (little-endian).
_CNOT = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=complex)


def native_cz() -> np.ndarray:
    """The native two-qubit entangling gate of the one-way model -- ``CZ`` -- applied by a single
    cluster edge (no measurement needed)."""
    return _CZ.copy()


def mbqc_hadamard(psi):
    """
    Hadamard on ``psi`` via a single teleportation step at measurement angle ``0`` -- returns the
    output for outcome 0 (``H|psi>``). The measurement-based realization of the Hadamard gate.
    """
    return teleport_step(psi, 0.0, 0)


def hadamard_is_teleport(atol: float = 1e-9) -> bool:
    """Verify a teleportation step at angle 0, outcome 0, is exactly the Hadamard gate."""
    return bool(np.allclose(expected_step_unitary(0.0, 0), _H, atol=atol))


def cnot_decomposition() -> np.ndarray:
    """
    The MBQC CNOT decomposition ``(I (x) H) CZ (I (x) H)`` as a matrix (control = qubit 0,
    little-endian). Verified equal to the exact CNOT.
    """
    IH = np.kron(_H, np.eye(2))          # H on target (qubit 1, high bit); control qubit 0
    return IH @ _CZ @ IH


def verify_cnot_decomposition(atol: float = 1e-9) -> bool:
    """True iff ``(I (x) H) CZ (I (x) H)`` equals the CNOT -- the identity the MBQC CNOT is built
    from (native CZ plus two Hadamard teleportations)."""
    return bool(np.allclose(cnot_decomposition(), _CNOT, atol=atol))


def mbqc_cnot(psi2) -> np.ndarray:
    """
    Apply the MBQC CNOT to a two-qubit state ``psi2`` by executing the decomposition
    ``(I (x) H) CZ (I (x) H)`` with the Hadamards realized by teleportation (outcome-0 branch).
    Returns ``CNOT|psi2>`` (up to the tracked byproducts). Verified against the exact CNOT.
    """
    # Each target-wire Hadamard is realized by an outcome-0 teleportation step, which equals the
    # H gate exactly (see `hadamard_is_teleport`); the CZ is the native cluster bond.
    IH = np.kron(expected_step_unitary(0.0, 0), np.eye(2))   # H (via teleport) on target qubit 1
    return IH @ _CZ @ IH @ np.asarray(psi2, dtype=complex)
