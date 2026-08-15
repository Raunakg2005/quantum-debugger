"""
The Holevo bound & accessible information

Alice encodes a classical symbol ``i`` (probability ``p_i``) into a quantum state
``rho_i`` and sends it to Bob. How much classical information can Bob's *best*
measurement extract? Two quantities frame the answer:

  * **Holevo quantity** ``chi = S(sum_i p_i rho_i) - sum_i p_i S(rho_i)`` -- an
    upper bound on the extractable (accessible) information. For n qubits
    ``chi <= n``: a qubit can never carry more than one classical bit.
  * **Accessible information** ``I_acc = max over measurements I(X : Y)`` -- what a
    measurement actually achieves.

For two equiprobable pure states with overlap ``cos(theta)`` both are exact:

    chi   = h((1 + cos(theta)) / 2),
    I_acc = 1 - h((1 + sin(theta)) / 2)      (Levitin; Helstrom measurement),

and ``I_acc < chi`` strictly for non-orthogonal states -- quantum information that
exists but cannot be extracted. This module computes both genuinely (the accessible
information by numerical optimization over projective measurements) and verifies the
closed forms.
"""

import numpy as np

from ..density_matrix import DensityMatrix

_I2 = np.eye(2, dtype=complex)
_SX = np.array([[0, 1], [1, 0]], dtype=complex)
_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def _h(x: float) -> float:
    if x <= 0 or x >= 1:
        return 0.0
    return float(-x * np.log2(x) - (1 - x) * np.log2(1 - x))


def holevo_bound(probs, states) -> float:
    """
    The Holevo quantity ``chi = S(rho_avg) - sum_i p_i S(rho_i)`` in bits, for an
    ensemble of density matrices (or pure state vectors) ``states`` with
    probabilities ``probs``. Upper-bounds the classical information any measurement
    can extract; at most ``n`` for n-qubit carriers.
    """
    dms = []
    for s in states:
        s = np.asarray(s, dtype=complex)
        dms.append(DensityMatrix(state_vector=s) if s.ndim == 1 else DensityMatrix(rho=s))
    avg = sum(p * dm.rho for p, dm in zip(probs, dms))
    chi = DensityMatrix(rho=avg).von_neumann_entropy()
    for p, dm in zip(probs, dms):
        chi -= p * dm.von_neumann_entropy()
    return float(chi)


def accessible_information(probs, states, restarts: int = 8, seed: int = 0) -> float:
    """
    Accessible information of a qubit ensemble: the mutual information ``I(X : Y)``
    between Alice's symbol and Bob's outcome, maximized over projective measurements
    (Bloch direction optimized by Nelder-Mead with restarts). Never exceeds
    :func:`holevo_bound` -- and for non-orthogonal states it stays strictly below.
    """
    from scipy.optimize import minimize

    dms = []
    for s in states:
        s = np.asarray(s, dtype=complex)
        dms.append(DensityMatrix(state_vector=s) if s.ndim == 1 else DensityMatrix(rho=s))
    probs = np.asarray(probs, dtype=float)

    def neg_mi(x):
        theta, phi = x
        nvec = (
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        )
        P = (_I2 + nvec[0] * _SX + nvec[1] * _SY + nvec[2] * _SZ) / 2
        # joint distribution p(i, k) for outcomes k in {P, I-P}
        joint = np.zeros((len(dms), 2))
        for i, (p, dm) in enumerate(zip(probs, dms)):
            q = float(np.real(np.trace(P @ dm.rho)))
            joint[i, 0] = p * q
            joint[i, 1] = p * (1 - q)
        py = joint.sum(axis=0)
        mi = 0.0
        for i in range(len(dms)):
            for k in range(2):
                if joint[i, k] > 1e-15:
                    mi += joint[i, k] * np.log2(joint[i, k] / (probs[i] * py[k]))
        return -mi

    rng = np.random.default_rng(seed)
    best = 0.0
    for _ in range(restarts):
        x0 = [rng.uniform(0, np.pi), rng.uniform(0, 2 * np.pi)]
        res = minimize(neg_mi, x0, method="Nelder-Mead",
                       options={"xatol": 1e-10, "fatol": 1e-13, "maxiter": 800})
        best = max(best, -float(res.fun))
    return best


def dense_coding_capacity(F: float) -> dict:
    """
    Superdense coding with a *noisy* shared resource: Alice encodes 2 bits by
    applying I/X/Y/Z to her half of a Werner pair of fidelity ``F`` and sends it.
    Bob's best decoding extracts the Holevo quantity of the resulting 4-state
    ensemble, computed here directly with :func:`holevo_bound` and equal to the
    closed form

        C = 2 - S(rho_W)      (the average encoded state is I/4),

    where ``S`` is the Werner state's entropy. ``C = 2`` bits for a perfect Bell
    pair, drops below the classical 1 bit when the pair is too noisy, and hits 0
    for the maximally mixed resource (``F = 1/4``).

    Returns dict with ``capacity`` (from the ensemble), ``analytic``
    (``2 - S(rho_W)``), and ``beats_classical`` (``capacity > 1``).
    """
    from .distillation import werner_state

    rho = werner_state(F)
    paulis = [
        np.eye(2, dtype=complex),
        np.array([[0, 1], [1, 0]], dtype=complex),
        np.array([[0, -1j], [1j, 0]], dtype=complex),
        np.array([[1, 0], [0, -1]], dtype=complex),
    ]
    # Alice's qubit is qubit 0 (little-endian): encoded state (I x P_A) rho (...)
    ensemble = []
    for P in paulis:
        op = np.kron(np.eye(2, dtype=complex), P)
        ensemble.append(op @ rho @ op.conj().T)
    capacity = holevo_bound([0.25] * 4, ensemble)

    s_w = DensityMatrix(rho=rho).von_neumann_entropy()
    return {
        "capacity": capacity,
        "analytic": 2 - s_w,
        "beats_classical": capacity > 1 + 1e-9,
    }


def holevo_gap(theta: float) -> dict:
    """
    The gap for two equiprobable pure states ``|0>`` and
    ``cos(theta)|0> + sin(theta)|1>`` (overlap ``cos(theta)``).

    Returns dict with ``chi`` (= ``h((1+cos theta)/2)``), ``accessible``
    (= ``1 - h((1+sin theta)/2)``, achieved by the Helstrom measurement), the two
    ``analytic`` values, and ``gap = chi - accessible`` (> 0 unless the states are
    orthogonal or identical): information the carrier holds but no measurement can
    reach.
    """
    s0 = np.array([1, 0], dtype=complex)
    s1 = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
    probs = [0.5, 0.5]
    chi = holevo_bound(probs, [s0, s1])
    acc = accessible_information(probs, [s0, s1])
    return {
        "chi": chi,
        "accessible": acc,
        "chi_analytic": _h((1 + abs(np.cos(theta))) / 2),
        "accessible_analytic": 1 - _h((1 + abs(np.sin(theta))) / 2),
        "gap": chi - acc,
    }
