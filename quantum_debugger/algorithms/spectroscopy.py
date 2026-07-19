"""
Quantum Spectroscopy -- Eigenphase / Eigenvalue Estimation

Quantum phase estimation for an *arbitrary* unitary or Hermitian operator (not just
the demo phase gate). Given an eigenstate, QPE reads out the corresponding
eigenphase of a unitary ``U`` (``U|psi> = e^{2*pi*i*phi}|psi>``) or the eigenvalue
of a Hermitian ``H`` (via ``U = exp(i H t)``). Verified against classical
diagonalization.
"""

import numpy as np
from scipy.linalg import expm

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary
from .qft import apply_inverse_qft
from ..core.circuit import QuantumCircuit


def _controlled_power(U: np.ndarray, power: int) -> np.ndarray:
    """Controlled-U^power with the control as the low bit of the joint index."""
    Up = np.linalg.matrix_power(U, power)
    dim = U.shape[0]
    C = np.zeros((2 * dim, 2 * dim), dtype=complex)
    for s_in in range(dim):
        C[2 * s_in, 2 * s_in] = 1.0  # control = 0 -> identity
        for s_out in range(dim):
            C[2 * s_out + 1, 2 * s_in + 1] = Up[s_out, s_in]  # control = 1 -> U
    return C


def unitary_eigenphase(U, eigenstate, n_counting: int = 8) -> dict:
    """
    Estimate the eigenphase ``phi`` of ``U`` for the given eigenstate via QPE.

    Args:
        U: a 2**m x 2**m unitary
        eigenstate: a length-2**m eigenvector of U
        n_counting: counting qubits (precision)

    Returns:
        dict with 'phase' (phi in [0, 1)), 'eigenvalue' (e^{2*pi*i*phi}), 'measured'.
    """
    U = np.asarray(U, dtype=complex)
    psi = np.asarray(eigenstate, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    m = int(round(np.log2(U.shape[0])))
    total = m + n_counting

    state = QuantumState(total)
    # Work register (qubits 0..m-1) = eigenstate; counting register = qubits m..
    sv = np.zeros(2**total, dtype=complex)
    for i, amp in enumerate(psi):
        sv[i] = amp
    state.state_vector = sv

    H = GateLibrary.H
    work = list(range(m))
    for j in range(n_counting):
        state.apply_gate(H, [m + j])
    for j in range(n_counting):
        state.apply_gate(_controlled_power(U, 2**j), [m + j] + work)

    inv = QuantumCircuit(total)
    apply_inverse_qft(inv, qubits=list(reversed(range(m, m + n_counting))))
    for g in inv.gates:
        state.apply_gate(g.matrix, g.qubits)

    probs = np.abs(state.state_vector) ** 2
    counting_probs = np.zeros(2**n_counting)
    for index in range(len(probs)):
        counting_probs[index >> m] += probs[index]

    measured = int(np.argmax(counting_probs))
    phase = measured / (2**n_counting)
    return {
        "phase": phase,
        "eigenvalue": np.exp(2j * np.pi * phase),
        "measured": measured,
    }


def hermitian_eigenvalue(
    H, eigenvector, n_counting: int = 8, scale: float = None
) -> dict:
    """
    Estimate the eigenvalue of a Hermitian ``H`` for the given eigenvector.

    Runs QPE on ``U = exp(i H scale)``. ``scale`` maps the eigenvalue range into
    ``[0, 2*pi)`` so the phase is unambiguous; if omitted it is chosen from the
    spectrum of ``H``.

    Returns dict with 'eigenvalue' (estimate), 'exact_eigenvalue' (Rayleigh
    quotient), and 'error'.
    """
    H = np.asarray(H, dtype=complex)
    v = np.asarray(eigenvector, dtype=complex)
    v = v / np.linalg.norm(v)

    eigvals = np.linalg.eigvalsh(H)
    lo, hi = float(eigvals[0]), float(eigvals[-1])
    if scale is None:
        span = (hi - lo) if hi > lo else 1.0
        # Map [lo, hi] into [0, 0.9 * 2pi) to stay within one period.
        scale = 0.9 * 2 * np.pi / span
    U = expm(1j * (H - lo * np.eye(H.shape[0])) * scale)

    result = unitary_eigenphase(U, v, n_counting)
    estimate = lo + result["phase"] * 2 * np.pi / scale
    exact = float(np.real(np.vdot(v, H @ v)))  # Rayleigh quotient
    return {
        "eigenvalue": estimate,
        "exact_eigenvalue": exact,
        "error": abs(estimate - exact),
    }
