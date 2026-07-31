"""
Distinguishability measures for quantum states.

How different are two density matrices? The answer underlies hypothesis testing,
tomography error bars, and convergence proofs. This module collects the standard
measures and the inequalities that relate them:

* **Trace distance** ``T = (1/2)||rho - sigma||_1`` -- the operational bias with which the
  states can be told apart by an optimal measurement.
* **Uhlmann fidelity** ``F = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2`` -- reduces to
  ``|<psi|phi>|^2`` for pure states.
* **Bures distance / angle** and the **Hilbert-Schmidt** distance -- metrics on state
  space.
* **Quantum relative entropy** ``S(rho||sigma) = Tr rho(log rho - log sigma)`` -- the
  asymmetric divergence, non-negative by Klein's inequality.

Verified against Bell/product states, the Fuchs-van de Graaf inequalities
``1 - sqrt(F) <= T <= sqrt(1 - F)``, and Klein's inequality.
"""

import numpy as np
from scipy.linalg import sqrtm, logm


def _herm(rho):
    return np.asarray(rho, dtype=complex)


def trace_distance(rho, sigma) -> float:
    """
    Trace distance ``(1/2) ||rho - sigma||_1`` (half the sum of singular values of the
    difference) -- the maximum probability advantage in distinguishing the two states.
    ``0`` for equal states, ``1`` for orthogonal ones.
    """
    diff = _herm(rho) - _herm(sigma)
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh((diff + diff.conj().T) / 2))))


def uhlmann_fidelity(rho, sigma) -> float:
    """
    Uhlmann fidelity ``F(rho, sigma) = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2`` in the
    convention ``F(psi, psi) = 1``. For pure states it equals the squared overlap
    ``|<psi|phi>|^2``.
    """
    r = _herm(rho); s = _herm(sigma)
    sr = sqrtm(r)
    inner = sqrtm(sr @ s @ sr)
    f = np.real(np.trace(inner))
    return float(np.clip(f, 0.0, 1.0) ** 2)


def bures_distance(rho, sigma) -> float:
    """Bures distance ``sqrt(2(1 - sqrt(F)))`` -- the metric induced by the fidelity."""
    return float(np.sqrt(max(2 * (1 - np.sqrt(uhlmann_fidelity(rho, sigma))), 0.0)))


def bures_angle(rho, sigma) -> float:
    """Bures angle ``arccos(sqrt(F))`` -- a geodesic distance on state space in ``[0, pi/2]``."""
    return float(np.arccos(np.clip(np.sqrt(uhlmann_fidelity(rho, sigma)), 0.0, 1.0)))


def hilbert_schmidt_distance(rho, sigma) -> float:
    """Hilbert-Schmidt distance ``||rho - sigma||_2 = sqrt(Tr[(rho-sigma)^2])``."""
    diff = _herm(rho) - _herm(sigma)
    return float(np.sqrt(np.real(np.trace(diff.conj().T @ diff))))


def fuchs_van_de_graaf(rho, sigma) -> dict:
    """
    The Fuchs-van de Graaf bounds relating trace distance ``T`` and fidelity ``F``:
    ``1 - sqrt(F) <= T <= sqrt(1 - F)``. Returns ``T``, ``F``, and the two bounds -- a
    verifiable consistency check between the two measures.
    """
    T = trace_distance(rho, sigma)
    F = uhlmann_fidelity(rho, sigma)
    return {"trace_distance": T, "fidelity": F,
            "lower": 1 - np.sqrt(F), "upper": np.sqrt(max(1 - F, 0.0))}


def quantum_relative_entropy(rho, sigma, base: float = 2.0) -> float:
    """
    Quantum relative entropy ``S(rho||sigma) = Tr rho(log rho - log sigma)`` -- the
    asymmetric divergence quantifying how hard it is to mistake ``rho`` for ``sigma``.
    Non-negative (Klein's inequality), zero iff the states are equal; ``+inf`` when the
    support of ``rho`` is not contained in that of ``sigma``.
    """
    r = _herm(rho); s = _herm(sigma)
    wr, vr = np.linalg.eigh(r)
    ws, vs = np.linalg.eigh(s)
    # if supp(rho) not subset of supp(sigma) -> divergence
    for i, w in enumerate(wr):
        if w > 1e-12:
            proj = vr[:, i]
            if np.real(proj.conj() @ (vs[:, ws <= 1e-12] @ vs[:, ws <= 1e-12].conj().T) @ proj) > 1e-9:
                return float("inf")
    logr = vr @ np.diag([np.log(w) if w > 1e-12 else 0.0 for w in wr]) @ vr.conj().T
    logs = vs @ np.diag([np.log(w) if w > 1e-12 else 0.0 for w in ws]) @ vs.conj().T
    val = np.real(np.trace(r @ (logr - logs))) / np.log(base)
    return float(max(val, 0.0))
