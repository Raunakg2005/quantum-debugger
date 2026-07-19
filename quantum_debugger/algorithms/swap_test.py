"""
Swap Test

Estimates the squared overlap |<psi|phi>|^2 between two states using one ancilla
and controlled-SWAP (Fredkin) gates. With the ancilla in |+>, a controlled swap
of the two registers, and a final Hadamard, the ancilla measures |0> with
probability (1 + |<psi|phi>|^2) / 2 -- so |<psi|phi>|^2 = 2 * P(0) - 1.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary


def _fredkin() -> np.ndarray:
    """Controlled-SWAP on gate-qubits (control=0, a=1, b=2), little-endian."""
    F = np.zeros((8, 8), dtype=complex)
    for idx in range(8):
        ctrl = idx & 1
        a = (idx >> 1) & 1
        b = (idx >> 2) & 1
        new = idx if ctrl == 0 else (ctrl | (b << 1) | (a << 2))
        F[new, idx] = 1.0
    return F


def swap_test(psi, phi) -> dict:
    """
    Estimate the squared overlap between two n-qubit states via the swap test.

    Args:
        psi, phi: state vectors of equal length 2**n

    Returns:
        dict with 'overlap' (|<psi|phi>|^2, from P(ancilla=0)) and
        'exact_overlap' (computed directly, for reference).
    """
    psi = np.asarray(psi, dtype=complex)
    phi = np.asarray(phi, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    phi = phi / np.linalg.norm(phi)
    n = int(round(np.log2(psi.shape[0])))

    # Layout: qubits 0..n-1 = register A (psi), n..2n-1 = register B (phi),
    # qubit 2n = ancilla. Initial state = |0>_anc (x) phi (x) psi.
    total = 2 * n + 1
    combined = np.kron([1.0, 0.0], np.kron(phi, psi))
    state = QuantumState(total, state_vector=combined)

    ancilla = 2 * n
    F = _fredkin()

    state.apply_gate(GateLibrary.H, [ancilla])
    for i in range(n):
        state.apply_gate(F, [ancilla, i, n + i])
    state.apply_gate(GateLibrary.H, [ancilla])

    probs = np.abs(state.state_vector) ** 2
    indices = np.arange(probs.shape[0])
    p0 = float(np.sum(probs[((indices >> ancilla) & 1) == 0]))
    overlap = max(0.0, 2.0 * p0 - 1.0)

    exact = float(np.abs(np.vdot(psi, phi)) ** 2)
    return {"overlap": overlap, "exact_overlap": exact, "p_ancilla_zero": p0}
