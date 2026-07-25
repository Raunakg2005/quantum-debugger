"""
Quantum state discrimination (Helstrom & unambiguous)

Non-orthogonal quantum states cannot be told apart perfectly -- the operational
core of quantum cryptography. Two optimal strategies, both with exact closed
forms, both constructed explicitly here:

  * **Minimum-error (Helstrom, 1976)**: guess every time, minimizing the error

        P_err = (1 - || p0 rho0 - p1 rho1 ||_1) / 2,

    achieved by projecting onto the positive part of ``p0 rho0 - p1 rho1``. For two
    equiprobable pure states with overlap ``s``: ``P_err = (1 - sqrt(1 - s^2))/2``.

  * **Unambiguous (Ivanovic-Dieks-Peres)**: never guess wrong -- allow an
    "inconclusive" outcome instead. For equiprobable pure states the maximal
    success probability is ``1 - |<psi0|psi1>|``, achieved by a 3-outcome POVM
    whose conclusive elements project onto the states' mutual orthogonal
    complements.
"""

import numpy as np


def _as_dm(state):
    state = np.asarray(state, dtype=complex)
    if state.ndim == 1:
        state = state / np.linalg.norm(state)
        return np.outer(state, state.conj())
    return state


def helstrom_bound(p0: float, state0, p1: float, state1) -> float:
    """
    Minimum achievable error probability for discriminating ``state0`` (prior
    ``p0``) from ``state1`` (prior ``p1``): ``(1 - ||p0 rho0 - p1 rho1||_1)/2``.
    States may be vectors or density matrices. Zero iff the states are orthogonal.
    """
    rho0, rho1 = _as_dm(state0), _as_dm(state1)
    M = p0 * rho0 - p1 * rho1
    trace_norm = float(np.sum(np.abs(np.linalg.eigvalsh(M))))
    return (1 - trace_norm) / 2


def helstrom_measurement(p0: float, state0, p1: float, state1) -> dict:
    """
    Construct the optimal (Helstrom) measurement explicitly -- project onto the
    positive eigenspace of ``p0 rho0 - p1 rho1`` -- and evaluate its actual error
    probability, which meets :func:`helstrom_bound` exactly.

    Returns dict with ``error_probability`` and ``bound``.
    """
    rho0, rho1 = _as_dm(state0), _as_dm(state1)
    M = p0 * rho0 - p1 * rho1
    vals, vecs = np.linalg.eigh(M)
    dim = M.shape[0]
    P0 = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        if vals[i] > 0:
            P0 += np.outer(vecs[:, i], vecs[:, i].conj())
    P1 = np.eye(dim, dtype=complex) - P0
    err = float(np.real(p0 * np.trace(P1 @ rho0) + p1 * np.trace(P0 @ rho1)))
    return {"error_probability": err, "bound": helstrom_bound(p0, rho0, p1, rho1)}


def unambiguous_discrimination(psi0, psi1) -> dict:
    """
    Unambiguous discrimination of two equiprobable pure qubit states via the
    explicit IDP POVM: conclusive element ``E_i`` proportional to the projector onto
    the state orthogonal to the *other* state (so it can never fire wrongly), plus
    the inconclusive remainder ``E_? = I - E_0 - E_1``.

    Returns dict with ``success_probability`` (= ``1 - |<psi0|psi1>|`` exactly),
    ``error_probability`` (exactly 0), ``inconclusive_probability``
    (= ``|<psi0|psi1>|``), ``analytic`` (the IDP bound), and ``povm_valid``.
    """
    a = np.asarray(psi0, dtype=complex)
    b = np.asarray(psi1, dtype=complex)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    if a.shape != (2,):
        raise ValueError("unambiguous_discrimination expects single-qubit pure states")
    overlap = abs(np.vdot(a, b))

    def perp(v):
        return np.array([-np.conj(v[1]), np.conj(v[0])], dtype=complex)

    a_perp_b = perp(b)  # orthogonal to psi1 -> conclusively identifies psi0
    b_perp_a = perp(a)  # orthogonal to psi0 -> conclusively identifies psi1
    c = 1.0 / (1.0 + overlap)
    E0 = c * np.outer(a_perp_b, a_perp_b.conj())
    E1 = c * np.outer(b_perp_a, b_perp_a.conj())
    Eq = np.eye(2, dtype=complex) - E0 - E1

    povm_valid = bool(np.all(np.linalg.eigvalsh(Eq).real > -1e-10))
    p_succ = float(0.5 * np.real(a.conj() @ E0 @ a) + 0.5 * np.real(b.conj() @ E1 @ b))
    p_err = float(0.5 * np.real(a.conj() @ E1 @ a) + 0.5 * np.real(b.conj() @ E0 @ b))
    p_inc = float(0.5 * np.real(a.conj() @ Eq @ a) + 0.5 * np.real(b.conj() @ Eq @ b))

    return {
        "success_probability": p_succ,
        "error_probability": p_err,
        "inconclusive_probability": p_inc,
        "analytic": 1 - overlap,
        "povm_valid": povm_valid,
    }
