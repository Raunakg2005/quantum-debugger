"""
Wigner and Husimi quasiprobability distributions.

Phase-space quasiprobabilities represent a bosonic state as a distribution over the
``(x, p)`` plane. The **Wigner function** is real and normalized like a probability, but can
go *negative* -- and Wigner negativity is a signature of genuinely non-classical states
(and a resource for quantum advantage). It is evaluated by the displaced-parity formula
``W(alpha) = (2/pi) Tr[D(-alpha) rho D(alpha) Pi]`` with parity ``Pi = (-1)^N``. The
**Husimi Q** function ``Q(alpha) = <alpha|rho|alpha>/pi`` is instead everywhere non-negative.
Verified: the vacuum Wigner is a positive Gaussian peaking at ``2/pi`` and integrating to 1,
while a Schrödinger-cat state shows Wigner negativity.
"""

import numpy as np

from .fock_space import displacement_operator, number_operator_fock, coherent_state_fock


def _parity(cutoff):
    return np.diag((-1.0) ** np.arange(cutoff)).astype(complex)


def wigner_point(rho, alpha: complex, cutoff: int) -> float:
    """
    Wigner function at the phase-space point ``alpha = (x + i p)/sqrt(2)`` via the
    displaced-parity formula ``(2/pi) Tr[D(-alpha) rho D(alpha) Pi]``. Real-valued; may be
    negative for non-classical states.
    """
    rho = np.asarray(rho, dtype=complex)
    D = displacement_operator(-alpha, cutoff)
    val = (2 / np.pi) * np.trace(D @ rho @ D.conj().T @ _parity(cutoff))
    return float(np.real(val))


def wigner_grid(rho, xs, ps, cutoff: int) -> np.ndarray:
    """Wigner function sampled on a grid of ``xs = Re(alpha)`` (rows) and ``ps = Im(alpha)``
    (columns), i.e. ``alpha = x + i p``; with this convention it integrates to 1."""
    W = np.zeros((len(xs), len(ps)))
    for i, x in enumerate(xs):
        for j, p in enumerate(ps):
            W[i, j] = wigner_point(rho, x + 1j * p, cutoff)
    return W


def wigner_negativity(rho, cutoff: int, span: float = 3.0, points: int = 41) -> float:
    """
    Wigner negativity: the integrated absolute value of the negative part of the Wigner
    function (0 for a classical Gaussian state, positive for a cat/Fock state). A witness of
    non-classicality.
    """
    xs = ps = np.linspace(-span, span, points)
    W = wigner_grid(rho, xs, ps, cutoff)
    dx = xs[1] - xs[0]
    return float(np.sum(np.abs(W[W < 0])) * dx * dx)


def wigner_integral(rho, cutoff: int, span: float = 3.5, points: int = 61) -> float:
    """Integral of the Wigner function over phase space -- equals 1 for a normalized state
    (a normalization check). Uses ``alpha = x + i p`` so the measure is ``dx dp``."""
    xs = ps = np.linspace(-span, span, points)
    W = wigner_grid(rho, xs, ps, cutoff)
    dx = xs[1] - xs[0]
    return float(np.sum(W) * dx * dx)


def husimi_q(rho, alpha: complex, cutoff: int) -> float:
    """
    Husimi Q function ``Q(alpha) = <alpha|rho|alpha> / pi`` -- the coherent-state overlap
    density. Everywhere non-negative and normalized, the smoothed cousin of the Wigner
    function.
    """
    rho = np.asarray(rho, dtype=complex)
    a = coherent_state_fock(alpha, cutoff)
    return float(np.real(np.vdot(a, rho @ a)) / np.pi)
