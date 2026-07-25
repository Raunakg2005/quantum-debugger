"""
Classical shadows (many observables from few measurements)

Full tomography of an ``n``-qubit state costs exponentially many measurements. The
classical-shadows protocol (Huang, Kueng & Preskill, Nature Physics 16, 1050, 2020)
instead measures each qubit in a *random* Pauli basis, and from each shot builds an
unbiased single-shot estimator ("snapshot") of the whole density matrix:

    rho_hat = prod_q ( 3 |b_q><b_q| - I ),

where ``|b_q>`` is the measured eigenstate on qubit ``q``. Averaging snapshots gives
an unbiased estimate of ``rho``, and hence of ANY observable ``<O> = Tr(O rho)`` --
so a single collection of random measurements estimates many observables at once,
with a cost set by their locality, not by the Hilbert-space dimension.

This module implements the random-Pauli (local) version and verifies that the
estimates are unbiased and converge to the true expectation values.
"""

import itertools

import numpy as np

_PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
_I = _PAULI["I"]


def _eigvecs(pauli):
    w, v = np.linalg.eigh(_PAULI[pauli])
    return {0: v[:, 1], 1: v[:, 0]}  # index 0 -> +1 eigenvector, 1 -> -1


def _observable_matrix(pauli_string):
    O = np.array([[1]], dtype=complex)
    for c in pauli_string:
        O = np.kron(_PAULI[c], O)
    return O


def collect_shadows(state_vector, shots: int, seed: int = 0) -> dict:
    """
    Collect ``shots`` classical-shadow snapshots of a pure ``state_vector``: each shot
    picks a random X/Y/Z basis per qubit, samples an outcome, and records the basis and
    bits. Returns a dict ``{"bases": ..., "outcomes": ..., "n": ...}`` reusable to
    estimate any observable via :func:`estimate_observable`.
    """
    state = np.asarray(state_vector, dtype=complex)
    state = state / np.linalg.norm(state)
    n = int(round(np.log2(len(state))))
    rng = np.random.default_rng(seed)

    bases, outcomes = [], []
    for _ in range(shots):
        basis = [rng.choice(("X", "Y", "Z")) for _ in range(n)]
        vecs = [_eigvecs(b) for b in basis]
        probs = np.empty(2**n)
        keys = list(itertools.product((0, 1), repeat=n))
        for idx, bits in enumerate(keys):
            v = np.array([1], dtype=complex)
            for q in range(n):
                v = np.kron(vecs[q][bits[q]], v)
            probs[idx] = abs(np.vdot(v, state)) ** 2
        probs /= probs.sum()
        outcomes.append(keys[rng.choice(len(keys), p=probs)])
        bases.append(basis)
    return {"bases": bases, "outcomes": outcomes, "n": n}


def estimate_observable(shadows: dict, pauli_string: str) -> float:
    """
    Estimate ``<P>`` for a Pauli string ``pauli_string`` from a collection of
    :func:`collect_shadows` snapshots. Unbiased -- converges to the true expectation.
    """
    O = _observable_matrix(pauli_string)
    n = shadows["n"]
    ests = []
    for basis, bits in zip(shadows["bases"], shadows["outcomes"]):
        snap = np.array([[1]], dtype=complex)
        for q in range(n):
            b = _eigvecs(basis[q])[bits[q]]
            snap = np.kron(3 * np.outer(b, b.conj()) - _I, snap)
        ests.append(float(np.real(np.trace(snap @ O))))
    return float(np.mean(ests))


def shadow_estimates(state_vector, observables, shots: int = 2000, seed: int = 0) -> dict:
    """
    Estimate several Pauli ``observables`` of ``state_vector`` from ONE collection of
    ``shots`` random measurements.

    Returns dict with ``estimates`` and ``true_values`` (per observable) and
    ``max_error`` -- the largest deviation, which shrinks as ``shots`` grows.
    """
    state = np.asarray(state_vector, dtype=complex)
    state = state / np.linalg.norm(state)
    shadows = collect_shadows(state, shots, seed)

    estimates, true_values = {}, {}
    for obs in observables:
        estimates[obs] = estimate_observable(shadows, obs)
        true_values[obs] = float(np.real(state.conj() @ _observable_matrix(obs) @ state))

    max_error = max(abs(estimates[o] - true_values[o]) for o in observables)
    return {"estimates": estimates, "true_values": true_values, "max_error": max_error}
