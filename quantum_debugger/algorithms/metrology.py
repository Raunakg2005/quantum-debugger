"""
Quantum Metrology -- Heisenberg-Limited Phase Estimation

Demonstrates the quantum advantage in phase sensing. A GHZ probe state accumulates
phase N times faster than independent qubits, so its parity signal oscillates as
``cos(N * phi)`` and its quantum Fisher information scales as ``N**2`` (the
Heisenberg limit) versus ``N`` for a product state (the standard quantum limit).
The best phase uncertainty therefore scales as ``1/N`` instead of ``1/sqrt(N)``.

Phase encoding: ``U(phi) = exp(-i phi H)`` with ``H = sum_i Z_i / 2``.
"""

import numpy as np

from .state_preparation import ghz_state


def _generator_diagonal(n: int) -> np.ndarray:
    """Diagonal of H = sum_i Z_i / 2 over the 2**n computational basis."""
    diag = np.zeros(2**n)
    for index in range(2**n):
        # Z eigenvalue +1 for a 0 bit, -1 for a 1 bit.
        z_sum = sum(1 if not ((index >> q) & 1) else -1 for q in range(n))
        diag[index] = z_sum / 2
    return diag


def quantum_fisher_information(state: np.ndarray, n: int) -> float:
    """
    QFI for phase encoding U(phi) = exp(-i phi H), H = sum_i Z_i/2, on a pure state.

    For a pure state QFI = 4 * Var(H).
    """
    diag = _generator_diagonal(n)
    probs = np.abs(state) ** 2
    mean = float(np.sum(probs * diag))
    mean_sq = float(np.sum(probs * diag**2))
    return 4.0 * (mean_sq - mean**2)


def product_probe(n: int) -> np.ndarray:
    """The |+>^n product probe (standard quantum limit reference)."""
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = np.array([1.0], dtype=complex)
    for _ in range(n):
        state = np.kron(state, plus)
    return state


def parity_signal(n: int, phi: float) -> float:
    """
    Parity expectation <X^{⊗n}> of a GHZ probe after phase phi per qubit.

    Equals cos(n * phi): the GHZ interferometer oscillates n times faster than a
    single qubit, which is the source of the metrological gain.
    """
    state = ghz_state(n).astype(complex)
    # Apply the phase exp(-i phi Z/2) on each qubit (diagonal in computational basis).
    diag = _generator_diagonal(n)
    state = state * np.exp(-1j * phi * diag)
    # Parity X^{⊗n} maps |k> -> |~k>; <psi|X^n|psi> = sum_k conj(psi_k) psi_{~k}.
    n_states = 2**n
    full = n_states - 1
    parity = sum(np.conj(state[k]) * state[k ^ full] for k in range(n_states))
    return float(np.real(parity))


def phase_sensitivity(n: int) -> dict:
    """
    Compare GHZ (Heisenberg) vs product-state (standard-quantum-limit) phase sensing.

    Returns dict with the quantum Fisher information of each probe and the
    corresponding best phase uncertainty ``delta_phi = 1/sqrt(QFI)``.
    """
    ghz = ghz_state(n).astype(complex)
    prod = product_probe(n)
    qfi_ghz = quantum_fisher_information(ghz, n)
    qfi_prod = quantum_fisher_information(prod, n)
    return {
        "n": n,
        "qfi_ghz": qfi_ghz,
        "qfi_product": qfi_prod,
        "delta_phi_ghz": 1.0 / np.sqrt(qfi_ghz) if qfi_ghz > 0 else np.inf,
        "delta_phi_product": 1.0 / np.sqrt(qfi_prod) if qfi_prod > 0 else np.inf,
        "advantage": qfi_ghz / qfi_prod if qfi_prod > 0 else np.inf,
    }
