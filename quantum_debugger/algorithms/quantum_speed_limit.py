"""
Quantum speed limits: how fast a state can evolve.

There is a fundamental minimum time for a quantum state to become distinguishable from itself. Two
complementary bounds set it (with hbar = 1):

* **Mandelstam-Tamm**: the Bhattacharyya angle between ``|psi(0)>`` and ``|psi(t)>`` grows no faster
  than the energy uncertainty, ``arccos|<psi(0)|psi(t)>| <= Delta E * t``. To reach an orthogonal
  state, ``t >= (pi/2) / Delta E``.
* **Margolus-Levitin**: the same orthogonalization needs ``t >= (pi/2) / E``, where ``E`` is the
  mean energy above the ground state.

The actual speed limit is the tighter (larger) of the two. For a two-level system driven resonantly
the Mandelstam-Tamm bound is *saturated* -- the evolution is as fast as quantum mechanics allows.

This module computes the energy statistics, both bounds, the actual orthogonalization time, and
verifies that a qubit precession saturates the Mandelstam-Tamm limit (hbar = 1).
"""

import numpy as np
from scipy.linalg import expm


def mean_energy(psi, H):
    """The mean energy ``<psi|H|psi>``."""
    psi = np.asarray(psi, dtype=complex).ravel()
    H = np.asarray(H, dtype=complex)
    return float(np.vdot(psi, H @ psi).real)


def energy_variance(psi, H):
    """The energy variance ``<H^2> - <H>^2`` -- its square root is the energy uncertainty
    ``Delta E``."""
    psi = np.asarray(psi, dtype=complex).ravel()
    H = np.asarray(H, dtype=complex)
    h = np.vdot(psi, H @ psi).real
    h2 = np.vdot(psi, H @ (H @ psi)).real
    return float(h2 - h * h)


def energy_uncertainty(psi, H):
    """The energy uncertainty ``Delta E = sqrt(Var H)`` -- the Mandelstam-Tamm speed scale."""
    return float(np.sqrt(max(energy_variance(psi, H), 0.0)))


def mandelstam_tamm_time(delta_E, overlap=0.0):
    """
    The Mandelstam-Tamm minimum time to reach a state with amplitude overlap ``|<psi0|psi_t>| =
    overlap``: ``t >= arccos(overlap) / Delta E``. For orthogonality (``overlap = 0``) this is
    ``(pi/2) / Delta E``.
    """
    return float(np.arccos(np.clip(overlap, 0.0, 1.0)) / delta_E)


def margolus_levitin_time(mean_energy_above_ground, overlap=0.0):
    """
    The Margolus-Levitin minimum time to orthogonality, ``t >= (pi/2) / E`` (``overlap = 0``), where
    ``E`` is the mean energy above the ground state. For partial overlap the same ``arccos`` prefactor
    scaling is used as an estimate.
    """
    return float(np.arccos(np.clip(overlap, 0.0, 1.0)) / mean_energy_above_ground)


def quantum_speed_limit_time(psi0, H, overlap=0.0):
    """
    The quantum speed-limit time: the tighter (larger) of the Mandelstam-Tamm and Margolus-Levitin
    bounds for evolving ``psi0`` under ``H`` to overlap ``overlap``. Uses ``Delta E`` and the mean
    energy above the ground state.
    """
    psi0 = np.asarray(psi0, dtype=complex).ravel()
    H = np.asarray(H, dtype=complex)
    dE = energy_uncertainty(psi0, H)
    E_above = mean_energy(psi0, H) - float(np.linalg.eigvalsh(H).min())
    t_mt = mandelstam_tamm_time(dE, overlap)
    t_ml = margolus_levitin_time(E_above, overlap) if E_above > 1e-12 else 0.0
    return max(t_mt, t_ml)


def evolution_overlap(psi0, H, t):
    """The survival amplitude ``|<psi0| e^{-iHt} |psi0>|`` after evolving for time ``t``."""
    psi0 = np.asarray(psi0, dtype=complex).ravel()
    H = np.asarray(H, dtype=complex)
    psi_t = expm(-1j * H * t) @ psi0
    return float(abs(np.vdot(psi0, psi_t)))


def orthogonalization_time(psi0, H, t_max=None, points=4000, threshold=5e-2):
    """
    The *first* time the evolved state becomes orthogonal to ``psi0`` (survival amplitude hits 0),
    found by locating the first sub-threshold crossing on a coarse grid and refining around it.
    Returns ``None`` if no orthogonal time is found within ``t_max``.
    """
    psi0 = np.asarray(psi0, dtype=complex).ravel()
    H = np.asarray(H, dtype=complex)
    dE = energy_uncertainty(psi0, H)
    if t_max is None:
        t_max = 4.0 * np.pi / max(dE, 1e-9)
    ts = np.linspace(1e-6, t_max, points)
    ov = np.array([evolution_overlap(psi0, H, t) for t in ts])
    below = np.where(ov < threshold)[0]
    if below.size == 0:
        return None
    first = int(below[0])
    # extend over the first contiguous sub-threshold run, then take its coarse minimum
    last = first
    while last + 1 < points and ov[last + 1] < threshold:
        last += 1
    c = first + int(np.argmin(ov[first:last + 1]))
    lo = ts[max(c - 2, 0)]
    hi = ts[min(c + 2, points - 1)]
    fine = np.linspace(lo, hi, 500)
    ovf = np.array([evolution_overlap(psi0, H, t) for t in fine])
    return float(fine[np.argmin(ovf)])


def saturates_mandelstam_tamm(psi0, H, atol=1e-3):
    """
    True iff the actual orthogonalization time equals the Mandelstam-Tamm bound ``(pi/2)/Delta E``
    -- i.e. the evolution is time-optimal. Verified for a two-level precession.
    """
    t_actual = orthogonalization_time(psi0, H)
    if t_actual is None:
        return False
    t_bound = mandelstam_tamm_time(energy_uncertainty(psi0, H), overlap=0.0)
    return bool(abs(t_actual - t_bound) <= max(atol, 1e-3 * t_bound))
