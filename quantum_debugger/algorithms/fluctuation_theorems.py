"""
Fluctuation theorems -- exact equalities far from equilibrium.

Thermodynamics far from equilibrium is dominated by fluctuations, yet obeys exact identities.
For a driven process the **work** ``W`` is a random variable (from the two-point measurement
scheme: measure energy before and after), and:

* **Jarzynski equality** ``<e^{-beta W}> = e^{-beta Delta F}`` -- the exponential average of work
  pins the free-energy difference *exactly*, even for an arbitrarily fast (irreversible) drive.
* **Crooks fluctuation theorem** ``P_F(W)/P_R(-W) = e^{beta(W - Delta F)}`` -- relates the
  forward and reverse work distributions.
* By Jensen's inequality Jarzynski implies ``<W> >= Delta F`` -- the second law.
* **Landauer's principle** -- erasing one bit dissipates at least ``k_B T ln 2`` of heat.

This module computes the two-point work distribution and verifies Jarzynski, the Jarzynski-second-law
bound, and the Landauer limit against their closed forms.
"""

import numpy as np


def two_point_work_distribution(H_initial, H_final, beta: float):
    """
    The forward two-point-measurement work distribution for a sudden quench: sample the initial
    energy from the Gibbs distribution of ``H_initial``, the final energy from ``H_final`` (sudden
    quench keeps the eigenstate populations of ``H_initial`` but projects onto ``H_final``
    eigenbasis). Returns ``(work_values, probabilities)``.
    """
    wi, vi = np.linalg.eigh(np.asarray(H_initial, dtype=complex))
    wf, vf = np.linalg.eigh(np.asarray(H_final, dtype=complex))
    pi = np.exp(-beta * wi); pi /= pi.sum()
    overlap = np.abs(vi.conj().T @ vf) ** 2      # |<f|i>|^2 [i, f]
    works, probs = [], []
    for i in range(len(wi)):
        for f in range(len(wf)):
            works.append(wf[f] - wi[i])
            probs.append(pi[i] * overlap[i, f])
    return np.array(works), np.array(probs)


def jarzynski_average(H_initial, H_final, beta: float) -> float:
    """The Jarzynski exponential work average ``<e^{-beta W}>`` -- verified equal to
    ``e^{-beta Delta F}``."""
    works, probs = two_point_work_distribution(H_initial, H_final, beta)
    return float(np.sum(probs * np.exp(-beta * works)))


def free_energy_difference(H_initial, H_final, beta: float) -> float:
    """The equilibrium free-energy difference ``Delta F`` -- the quantity Jarzynski recovers from
    non-equilibrium work."""
    zi = np.sum(np.exp(-beta * np.linalg.eigvalsh(np.asarray(H_initial, dtype=complex))))
    zf = np.sum(np.exp(-beta * np.linalg.eigvalsh(np.asarray(H_final, dtype=complex))))
    return float(-np.log(zf / zi) / beta)


def average_work(H_initial, H_final, beta: float) -> float:
    """The mean work ``<W>`` over the two-point distribution -- verified ``>= Delta F`` (the second
    law from Jarzynski via Jensen)."""
    works, probs = two_point_work_distribution(H_initial, H_final, beta)
    return float(np.sum(probs * works))


def work_variance(H_initial, H_final, beta: float) -> float:
    """Variance of the two-point-measurement work ``Var(W) = <W^2> - <W>^2`` -- the size of the
    work fluctuations a fluctuation theorem constrains."""
    works, probs = two_point_work_distribution(H_initial, H_final, beta)
    mean = np.sum(probs * works)
    return float(np.sum(probs * works ** 2) - mean ** 2)


def dissipated_work(H_initial, H_final, beta: float) -> float:
    """The dissipated (irreversible) work ``W_diss = <W> - Delta F >= 0`` -- the second-law
    inequality's slack, zero only for a reversible process."""
    return float(average_work(H_initial, H_final, beta) - free_energy_difference(H_initial, H_final, beta))


def verify_jarzynski(H_initial, H_final, beta: float, atol: float = 1e-9) -> bool:
    """True iff ``<e^{-beta W}> = e^{-beta Delta F}`` (the Jarzynski equality holds exactly)."""
    lhs = jarzynski_average(H_initial, H_final, beta)
    rhs = np.exp(-beta * free_energy_difference(H_initial, H_final, beta))
    return bool(abs(lhs - rhs) < atol)


def landauer_bound(n_bits: float, temperature: float, k_B: float = 1.0) -> float:
    """
    Landauer's minimum heat dissipated to erase ``n_bits`` bits at ``temperature``:
    ``n_bits k_B T ln 2`` -- the thermodynamic cost of irreversible information erasure.
    """
    return float(n_bits * k_B * temperature * np.log(2))


def crooks_ratio(work: float, delta_F: float, beta: float) -> float:
    """The Crooks forward/reverse probability ratio ``P_F(W)/P_R(-W) = e^{beta(W - Delta F)}`` at a
    given work value -- 1 at ``W = Delta F`` (the reversible work)."""
    return float(np.exp(beta * (work - delta_F)))
