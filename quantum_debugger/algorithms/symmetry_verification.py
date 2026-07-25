"""
Symmetry verification (error mitigation by post-selection)

Many computations have a symmetry the ideal state must respect -- a fixed parity, a
conserved particle number, a stabilizer. Errors often break that symmetry, kicking the
state into the wrong sector. **Symmetry verification** measures the symmetry and throws
away the runs that fail it, post-selecting onto the correct sector:

    rho -> P rho P / Tr(P rho),      P = (I + s S) / 2,

for a symmetry operator ``S`` (eigenvalues +/-1) and desired sector ``s``. Any error
that leaves the ``+s`` eigenspace is removed for free, at the cost of discarding the
rejected fraction. This module applies the projection on the density-matrix engine and
verifies the improvement.
"""

import numpy as np


def symmetry_project(rho, symmetry, sector: int = 1) -> dict:
    """
    Post-select ``rho`` onto the ``sector`` (+1 or -1) eigenspace of the symmetry
    operator ``symmetry`` (Hermitian, eigenvalues +/-1).

    Returns dict with ``rho`` (the post-selected, renormalized density matrix) and
    ``acceptance`` (``Tr(P rho)``, the fraction of runs kept).
    """
    R = np.asarray(rho, dtype=complex)
    S = np.asarray(symmetry, dtype=complex)
    P = (np.eye(S.shape[0], dtype=complex) + sector * S) / 2
    projected = P @ R @ P
    acceptance = float(np.real(np.trace(projected)))
    if acceptance > 1e-15:
        projected = projected / acceptance
    return {"rho": projected, "acceptance": acceptance}


def symmetry_verified_expectation(rho, symmetry, observable, sector: int = 1,
                                  ideal_state=None) -> dict:
    """
    Compare an observable's expectation before and after symmetry post-selection.

    Returns dict with ``raw``, ``verified``, ``acceptance``, and -- if the noise-free
    ``ideal_state`` is given -- ``ideal``, ``raw_error``, ``verified_error``, and
    ``improved``.
    """
    R = np.asarray(rho, dtype=complex)
    O = np.asarray(observable, dtype=complex)
    raw = float(np.real(np.trace(O @ R)))

    ps = symmetry_project(R, symmetry, sector)
    verified = float(np.real(np.trace(O @ ps["rho"])))

    result = {"raw": raw, "verified": verified, "acceptance": ps["acceptance"]}
    if ideal_state is not None:
        psi = np.asarray(ideal_state, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        ideal = float(np.real(psi.conj() @ O @ psi))
        result.update(
            ideal=ideal,
            raw_error=abs(raw - ideal),
            verified_error=abs(verified - ideal),
            improved=abs(verified - ideal) < abs(raw - ideal) + 1e-12,
        )
    return result
