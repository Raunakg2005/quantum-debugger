"""
Excited-state solvers for VQE-style algorithms.

Ground-state VQE finds the lowest eigenvalue; chemistry also needs excited states
(spectroscopy, reaction barriers). Three standard strategies are provided, each reduced
to a verifiable linear-algebra core:

* **Folded spectrum** -- minimizing ``(H - omega)^2`` targets the eigenstate *nearest*
  a chosen energy ``omega``, reaching interior states the ground-state method cannot.
* **Rayleigh-Ritz subspace** -- diagonalizing ``H`` inside a trial subspace gives
  variational (upper-bound) estimates of several eigenvalues at once, exact when the
  subspace is invariant (the subspace-search / quantum-subspace-expansion idea).
* **Variational deflation (VQD)** -- adding penalties ``beta |psi_i><psi_i|`` for the
  states already found lifts them out of the way, so the next ground state is the next
  excited state.

Each is verified against exact diagonalization.
"""

import numpy as np


def folded_spectrum_operator(H, omega: float) -> np.ndarray:
    """
    Folded-spectrum operator ``(H - omega I)^2``. Its ground state is the eigenstate of
    ``H`` whose energy is closest to ``omega`` -- the trick that lets a ground-state
    solver reach interior eigenvalues. Verified against the nearest exact eigenpair.
    """
    H = np.asarray(H, dtype=complex)
    shifted = H - omega * np.eye(H.shape[0])
    return shifted @ shifted


def nearest_eigenstate(H, omega: float):
    """
    The eigenvalue/eigenvector of ``H`` closest to ``omega``, obtained as the ground state
    of the folded operator ``(H - omega)^2``. Returns ``(energy, state)``.
    """
    H = np.asarray(H, dtype=complex)
    _, v = np.linalg.eigh(folded_spectrum_operator(H, omega))
    state = v[:, 0]
    energy = float(np.real(np.vdot(state, H @ state)))
    return energy, state


def subspace_energies(H, subspace_basis) -> np.ndarray:
    """
    Rayleigh-Ritz eigenvalue estimates: diagonalize ``H`` restricted to the span of
    ``subspace_basis`` (columns). The returned Ritz values are variational upper bounds on
    the true eigenvalues, and are exact when the subspace is ``H``-invariant -- the core
    of subspace-search VQE and the quantum subspace expansion.
    """
    B = np.asarray(subspace_basis, dtype=complex)
    B, _ = np.linalg.qr(B)                     # orthonormalize
    Hs = B.conj().T @ np.asarray(H, dtype=complex) @ B
    return np.linalg.eigvalsh(Hs)


def ssvqe_cost(H, states, weights) -> float:
    """
    Subspace-search VQE cost ``sum_i w_i <psi_i|H|psi_i>`` for orthonormal trial
    ``states`` and decreasing ``weights``. Minimized (over all orthonormal sets) exactly
    when the states are the lowest eigenvectors, giving cost ``sum_i w_i lambda_i`` --
    verified against that optimum.
    """
    H = np.asarray(H, dtype=complex)
    return float(sum(w * np.real(np.vdot(s, H @ s)) for w, s in zip(weights, states)))


def deflation_hamiltonian(H, known_states, beta: float) -> np.ndarray:
    """
    Variational-deflation Hamiltonian ``H + beta sum_i |psi_i><psi_i|`` that penalizes the
    already-found eigenstates ``known_states``. For ``beta`` above the spectral range, its
    ground state is the lowest eigenstate *orthogonal* to those given -- i.e. the next
    excited state. Verified: successive deflation recovers the exact spectrum in order.
    """
    H = np.asarray(H, dtype=complex).copy()
    for psi in known_states:
        psi = np.asarray(psi, dtype=complex)
        H = H + beta * np.outer(psi, psi.conj())
    return H


def excited_spectrum_by_deflation(H, k: int, beta: float = 100.0):
    """
    The ``k`` lowest eigenvalues found one at a time by variational deflation (each new
    ground state penalizes the previous ones). Returns the list of energies -- verified
    equal to the exact ``k`` lowest eigenvalues.
    """
    H = np.asarray(H, dtype=complex)
    found_states, energies = [], []
    for _ in range(k):
        Hd = deflation_hamiltonian(H, found_states, beta)
        w, v = np.linalg.eigh(Hd)
        state = v[:, 0]
        found_states.append(state)
        energies.append(float(np.real(np.vdot(state, H @ state))))
    return energies
