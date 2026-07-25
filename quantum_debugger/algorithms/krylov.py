"""
Krylov subspace diagonalization (the Lanczos method)

Instead of variationally searching or cooling, build a small subspace from repeated
applications of the Hamiltonian,

    K_m = span{ |psi>, H|psi>, H^2|psi>, ..., H^{m-1}|psi> },

and diagonalize ``H`` inside it. The extreme eigenvalues of the projected problem --
the Ritz values -- converge to the true extreme eigenvalues of ``H`` exponentially in
``m``, giving the ground energy *and* low-lying excited states (which plain
imaginary-time evolution cannot reach). This is classical Lanczos, and the model
behind quantum Krylov / quantum subspace-expansion algorithms.

Because the Krylov vectors become nearly parallel, the overlap matrix ``S`` grows
ill-conditioned; the projected generalized eigenproblem ``H c = E S c`` is solved in a
thresholded, well-conditioned subspace of ``S`` for stability.
"""

import numpy as np


def _thresholded_gevp(Hk, S, tol=1e-10):
    """Solve H c = E S c robustly by projecting onto the well-conditioned part of S."""
    s_vals, s_vecs = np.linalg.eigh(S)
    keep = s_vals > tol * s_vals.max()
    U = s_vecs[:, keep] / np.sqrt(s_vals[keep])
    projected = U.conj().T @ Hk @ U
    projected = (projected + projected.conj().T) / 2
    return np.sort(np.linalg.eigvalsh(projected).real)


def krylov_spectrum(hamiltonian, dim: int, initial_state=None, seed: int = 0) -> np.ndarray:
    """
    Ritz values from a ``dim``-dimensional Krylov subspace built from ``initial_state``
    (default random). Returns the sorted real eigenvalues of the projected problem --
    approximations to the extreme eigenvalues of ``hamiltonian``.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    if initial_state is None:
        rng = np.random.default_rng(seed)
        v = rng.normal(size=H.shape[0]) + 1j * rng.normal(size=H.shape[0])
    else:
        v = np.asarray(initial_state, dtype=complex)
    v = v / np.linalg.norm(v)

    basis = [v]
    for _ in range(dim - 1):
        w = H @ basis[-1]
        w = w / np.linalg.norm(w)  # rescale only (span unchanged) to avoid overflow
        basis.append(w)
    B = np.array(basis).T

    S = B.conj().T @ B
    Hk = B.conj().T @ H @ B
    return _thresholded_gevp(Hk, S)


def krylov_ground_energy(hamiltonian, dim: int, initial_state=None, seed: int = 0) -> dict:
    """
    Estimate the ground-state energy of ``hamiltonian`` from a ``dim``-vector Krylov
    subspace.

    Returns dict with ``energy`` (lowest Ritz value), ``exact_energy`` (true ground
    energy), ``error``, and ``ritz_values`` (the full projected spectrum -- its lowest
    few entries approximate the low-lying levels).
    """
    ritz = krylov_spectrum(hamiltonian, dim, initial_state, seed)
    exact = float(np.linalg.eigvalsh(np.asarray(hamiltonian, dtype=complex)).real.min())
    return {
        "energy": float(ritz[0]),
        "exact_energy": exact,
        "error": abs(float(ritz[0]) - exact),
        "ritz_values": ritz,
    }
