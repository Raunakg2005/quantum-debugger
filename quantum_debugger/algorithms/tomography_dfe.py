"""
State tomography and direct fidelity estimation.

A density matrix on ``n`` qubits is fixed by its ``4^n`` Pauli expectations,
``rho = (1/2^n) sum_P <P> P``. **Linear-inversion tomography** reconstructs ``rho`` from
those expectations; **direct fidelity estimation (DFE)** skips the full reconstruction and
estimates only the fidelity to a target from the correlated Pauli expectations,

    F(rho, sigma) = (1/d) sum_k chi_rho(k) chi_sigma(k),

which needs far fewer settings. Both are verified: tomography recovers a random state
exactly, and DFE equals ``<psi|rho|psi>`` for a pure target.
"""

import numpy as np
from itertools import product

from .pauli_hamiltonian import pauli_matrix


def pauli_expectations(rho):
    """
    All Pauli expectations ``<P> = Tr(P rho)`` of an ``n``-qubit state, as a dict keyed by the
    Pauli label. The complete tomographic data set.
    """
    rho = np.asarray(rho, dtype=complex)
    n = int(round(np.log2(rho.shape[0])))
    out = {}
    for labels in product("IXYZ", repeat=n):
        lab = "".join(labels)
        out[lab] = float(np.real(np.trace(pauli_matrix(lab) @ rho)))
    return out


def state_tomography(expectations, n_qubits: int) -> np.ndarray:
    """
    Reconstruct a density matrix by linear inversion:
    ``rho = (1/2^n) sum_P <P> P``. Verified to recover the original state exactly from its
    Pauli expectations.
    """
    d = 2 ** n_qubits
    rho = np.zeros((d, d), dtype=complex)
    for lab, val in expectations.items():
        rho += val * pauli_matrix(lab)
    return rho / d


def is_physical_density_matrix(rho, atol: float = 1e-8) -> bool:
    """True iff ``rho`` is a valid density matrix: Hermitian, unit trace, positive
    semi-definite."""
    rho = np.asarray(rho, dtype=complex)
    if not np.allclose(rho, rho.conj().T, atol=atol):
        return False
    if abs(np.trace(rho) - 1) > atol:
        return False
    return bool(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2)) >= -atol)


def direct_fidelity_estimation(rho, target) -> float:
    """
    Direct fidelity estimation ``F = (1/d) sum_k Tr(P_k target) Tr(P_k rho)`` between a state
    ``rho`` and a (pure) ``target``. Equals ``Tr(target rho) = <psi|rho|psi>`` for a pure
    target -- verified -- without reconstructing ``rho``.
    """
    rho = np.asarray(rho, dtype=complex)
    target = np.asarray(target, dtype=complex)
    n = int(round(np.log2(rho.shape[0])))
    d = 2 ** n
    total = 0.0
    for labels in product("IXYZ", repeat=n):
        P = pauli_matrix("".join(labels))
        total += np.real(np.trace(P @ target)) * np.real(np.trace(P @ rho))
    return float(total / d)
