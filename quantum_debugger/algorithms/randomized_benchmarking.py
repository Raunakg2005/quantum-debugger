"""
Randomized Benchmarking (single-qubit)

Estimate the average error per Clifford gate independently of state-preparation
and measurement (SPAM) errors. Random sequences of Clifford gates are applied,
followed by the single recovery Clifford that inverts the whole sequence; without
noise the qubit returns to |0> exactly. Under noise the survival probability decays
as ``S(m) = A p^m + B``, and the average gate error is ``(1 - p) (d - 1) / d`` with
``d = 2``.

A per-gate single-qubit depolarizing channel of strength ``lambda`` is used as the
noise model, applied via density-matrix evolution.
"""

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_S = np.array([[1, 0], [0, 1j]], dtype=complex)
_I = np.eye(2, dtype=complex)
_PAULIS = [
    _I,
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
]


def _canonical_key(U):
    """Global-phase-invariant hashable key for a 2x2 unitary."""
    flat = U.ravel()
    # Pick the FIRST significant entry (deterministic under magnitude ties, unlike
    # argmax) and rotate it to the positive real axis to remove the global phase.
    phase = next(v for v in flat if abs(v) > 1e-9)
    flat = flat * (abs(phase) / phase)
    return tuple(np.round(flat, 6))


def single_qubit_clifford_group():
    """Return the 24 single-qubit Clifford unitaries (as 2x2 arrays)."""
    group = {}
    frontier = [_I]
    group[_canonical_key(_I)] = _I
    while frontier:
        U = frontier.pop()
        for gen in (_H, _S):
            V = gen @ U
            key = _canonical_key(V)
            if key not in group:
                group[key] = V
                frontier.append(V)
    return list(group.values())


_CLIFFORDS = single_qubit_clifford_group()
_KEY_TO_INDEX = {_canonical_key(U): i for i, U in enumerate(_CLIFFORDS)}


def _inverse_clifford(U):
    """Return the group element equal to U^dagger (up to global phase)."""
    return _CLIFFORDS[_KEY_TO_INDEX[_canonical_key(U.conj().T)]]


def _depolarize(rho, lam):
    """Single-qubit depolarizing channel: rho -> (1-lam) rho + lam I/2."""
    return (1 - lam) * rho + lam * (np.trace(rho) * _I / 2)


def _survival_probability(sequence_length, lam, rng, shots=1):
    """Mean survival probability P(|0>) over ``shots`` random RB sequences."""
    total = 0.0
    for _ in range(shots):
        idxs = rng.integers(len(_CLIFFORDS), size=sequence_length)
        composed = _I.copy()
        rho = np.array([[1, 0], [0, 0]], dtype=complex)  # |0><0|
        for i in idxs:
            C = _CLIFFORDS[int(i)]
            rho = C @ rho @ C.conj().T
            rho = _depolarize(rho, lam)
            composed = C @ composed
        recovery = _inverse_clifford(composed)
        rho = recovery @ rho @ recovery.conj().T
        rho = _depolarize(rho, lam)
        total += float(np.real(rho[0, 0]))
    return total / shots


def _fit_decay(lengths, survivals):
    """Fit S(m) = A p^m + B by a small grid+least-squares search over p."""
    lengths = np.asarray(lengths, dtype=float)
    survivals = np.asarray(survivals, dtype=float)
    best = (None, np.inf, 0.0, 0.5)
    for p in np.linspace(0.5, 1.0, 501):
        basis = np.vstack([p**lengths, np.ones_like(lengths)]).T
        (A, B), res, *_ = np.linalg.lstsq(basis, survivals, rcond=None)
        pred = A * p**lengths + B
        err = float(np.sum((pred - survivals) ** 2))
        if err < best[1]:
            best = (p, err, A, B)
    return {"p": float(best[0]), "A": float(best[2]), "B": float(best[3])}


def randomized_benchmarking(
    lengths=(1, 2, 4, 8, 16, 32),
    depolarizing=0.02,
    shots=40,
    seed=0,
):
    """
    Run single-qubit randomized benchmarking.

    Args:
        lengths: sequence lengths (number of random Cliffords) to sample
        depolarizing: per-gate depolarizing strength ``lambda``
        shots: random sequences averaged per length
        seed: RNG seed

    Returns:
        dict with 'lengths', 'survival' (per length), fitted 'p', 'A', 'B', and
        'average_error' = (1 - p) (d - 1) / d with d = 2.
    """
    rng = np.random.default_rng(seed)
    lengths = list(lengths)
    survival = [_survival_probability(m, depolarizing, rng, shots) for m in lengths]
    fit = _fit_decay(lengths, survival)
    p = fit["p"]
    return {
        "lengths": lengths,
        "survival": survival,
        "p": p,
        "A": fit["A"],
        "B": fit["B"],
        "average_error": float((1 - p) * (2 - 1) / 2),
    }
