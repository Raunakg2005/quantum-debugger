"""
Variational Ground-State Solver (VQE)

A self-contained hardware-efficient VQE for any Hamiltonian written as a sum of
weighted Pauli strings. A layered RY + CNOT ansatz is optimized to minimize the
energy expectation; the result is checked against the exact ground energy
(smallest eigenvalue of the assembled Hamiltonian). Useful for spin models such as
the transverse-field Ising and Heisenberg Hamiltonians.

Hamiltonians use the same ``(coefficient, pauli_string)`` format as
``hamiltonian_simulation`` (``pauli_string[q]`` in ``I/X/Y/Z`` acts on qubit q).
"""

import numpy as np
from scipy.optimize import minimize

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary
from .hamiltonian_simulation import hamiltonian_matrix

_CNOT = GateLibrary.CNOT


def _ansatz_state(params: np.ndarray, n: int, layers: int) -> np.ndarray:
    """Hardware-efficient ansatz: per layer, RY on each qubit + a CNOT ladder."""
    state = QuantumState(n)
    idx = 0
    for _ in range(layers):
        for q in range(n):
            state.apply_gate(GateLibrary.RY(params[idx]), [q])
            idx += 1
        for q in range(n - 1):
            state.apply_gate(_CNOT, [q, q + 1])
    # Final rotation layer.
    for q in range(n):
        state.apply_gate(GateLibrary.RY(params[idx]), [q])
        idx += 1
    return state.state_vector


def _n_params(n: int, layers: int) -> int:
    return n * (layers + 1)


def variational_ground_state(
    terms,
    layers: int = 4,
    restarts: int = 6,
    max_iterations: int = 500,
    seed: int = 0,
    method: str = "BFGS",
) -> dict:
    """
    Find the ground-state energy of a Pauli-sum Hamiltonian with VQE.

    Uses a gradient-based optimizer (BFGS by default) on the layered RY + CNOT
    ansatz, which converges to the exact ground energy far more reliably than a
    derivative-free method -- reaching machine precision on TFIM/Heisenberg chains
    up to several qubits.

    Args:
        terms: list of (coeff, pauli_string)
        layers: ansatz depth
        restarts: random restarts (best kept)
        max_iterations: optimizer iterations per restart
        seed: RNG seed
        method: scipy.optimize.minimize method (default 'BFGS')

    Returns:
        dict with 'energy' (VQE estimate), 'exact_energy' (exact ground state),
        'error', and 'optimal_params'.
    """
    n = len(terms[0][1])
    H = hamiltonian_matrix(terms, n)
    exact = float(np.min(np.linalg.eigvalsh(H)))

    def energy(params):
        psi = _ansatz_state(params, n, layers)
        return float(np.real(np.vdot(psi, H @ psi)))

    rng = np.random.default_rng(seed)
    n_params = _n_params(n, layers)
    best_energy, best_params = np.inf, None
    for _ in range(restarts):
        x0 = rng.uniform(0, 2 * np.pi, n_params)
        res = minimize(energy, x0, method=method, options={"maxiter": max_iterations})
        if res.fun < best_energy:
            best_energy, best_params = float(res.fun), res.x

    return {
        "energy": best_energy,
        "exact_energy": exact,
        "error": abs(best_energy - exact),
        "optimal_params": best_params,
    }


def tfim_hamiltonian(n: int, field: float = 1.0, coupling: float = 1.0) -> list:
    """Transverse-field Ising model: -J sum ZZ - h sum X (open chain)."""
    terms = []
    for i in range(n - 1):
        p = ["I"] * n
        p[i] = p[i + 1] = "Z"
        terms.append((-coupling, "".join(p)))
    for i in range(n):
        p = ["I"] * n
        p[i] = "X"
        terms.append((-field, "".join(p)))
    return terms


def heisenberg_hamiltonian(n: int, coupling: float = 1.0) -> list:
    """Isotropic Heisenberg model: J sum (XX + YY + ZZ) on an open chain."""
    terms = []
    for i in range(n - 1):
        for pauli in ("X", "Y", "Z"):
            p = ["I"] * n
            p[i] = p[i + 1] = pauli
            terms.append((coupling, "".join(p)))
    return terms
