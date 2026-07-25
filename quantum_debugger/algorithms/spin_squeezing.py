"""
Spin squeezing (metrologically useful entanglement)

A coherent spin state -- all ``N`` qubits pointing the same way -- has isotropic
transverse noise and reaches only the standard quantum limit (SQL) for phase
estimation. *Entangling* the spins can redistribute that noise: a spin-squeezed state
has reduced variance along one transverse direction (at the cost of the orthogonal
one), beating the SQL. The Wineland squeezing parameter

    xi^2 = N * min_phi Var(J_phi) / |<J>|^2

is ``1`` at the SQL and ``< 1`` for a metrologically useful (entangled) state -- and
``xi^2 = 1 / (delta phi^2 * N)`` directly gives the phase-sensitivity gain.

The one-axis-twisting Hamiltonian ``H = chi J_z^2`` (Kitagawa & Ueda, Phys. Rev. A 47,
5138, 1993) generates squeezing from a coherent state pointing along ``x``. This
module evolves under it and computes ``xi^2``, verifying it dips below 1 and improves
with ``N``.
"""

import numpy as np
from scipy.linalg import expm

_SX = np.array([[0, 1], [1, 0]], dtype=complex) / 2
_SY = np.array([[0, -1j], [1j, 0]], dtype=complex) / 2
_SZ = np.array([[1, 0], [0, -1]], dtype=complex) / 2


def _collective_spin(n):
    def embed(op, i):
        out = np.array([[1]], dtype=complex)
        for k in range(n):
            out = np.kron(op if k == i else np.eye(2, dtype=complex), out)
        return out

    Jx = sum(embed(_SX, i) for i in range(n))
    Jy = sum(embed(_SY, i) for i in range(n))
    Jz = sum(embed(_SZ, i) for i in range(n))
    return Jx, Jy, Jz


def one_axis_twisting(n: int, chi_t: float) -> float:
    """
    Wineland squeezing parameter ``xi^2`` of an ``n``-qubit coherent spin state (along
    ``x``) after evolving under one-axis twisting ``H = chi J_z^2`` for ``chi t = chi_t``.
    ``xi^2 = 1`` at ``chi_t = 0`` (SQL); ``< 1`` once squeezed.
    """
    Jx, Jy, Jz = _collective_spin(n)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    psi = plus
    for _ in range(n - 1):
        psi = np.kron(plus, psi)
    psi = expm(-1j * chi_t * (Jz @ Jz)) @ psi

    mean = np.array([np.real(psi.conj() @ J @ psi) for J in (Jx, Jy, Jz)])
    norm = np.linalg.norm(mean)
    nv = mean / norm
    ref = np.array([0, 0, 1.0]) if abs(nv[2]) < 0.9 else np.array([1.0, 0, 0])
    e1 = np.cross(nv, ref)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(nv, e1)
    J1 = e1[0] * Jx + e1[1] * Jy + e1[2] * Jz
    J2 = e2[0] * Jx + e2[1] * Jy + e2[2] * Jz

    # Minimum transverse variance over all angles in the plane, in closed form from
    # the 2x2 covariance matrix (no angle scan): the smaller eigenvalue of
    # [[Var(J1), Cov], [Cov, Var(J2)]].
    def expect(M):
        return float(np.real(psi.conj() @ M @ psi))

    m1, m2 = expect(J1), expect(J2)
    v1 = expect(J1 @ J1) - m1**2
    v2 = expect(J2 @ J2) - m2**2
    cov = 0.5 * expect(J1 @ J2 + J2 @ J1) - m1 * m2
    min_var = 0.5 * (v1 + v2) - 0.5 * np.sqrt((v1 - v2) ** 2 + 4 * cov**2)
    return float(n * min_var / norm**2)


def best_squeezing(n: int, points: int = 60, t_max: float = 1.5) -> dict:
    """
    Scan one-axis-twisting time to find the optimal squeezing for ``n`` qubits.

    Returns dict with:
      * ``sql``              -- ``xi^2`` at ``t = 0`` (exactly 1, the standard quantum limit)
      * ``best_xi2``         -- the minimum ``xi^2`` achieved (``< 1`` = squeezed)
      * ``best_chi_t``       -- the twisting time that achieves it
      * ``squeezing_dB``     -- ``10 log10(best_xi2)`` (negative = below the SQL)
      * ``metrological_gain``-- ``1 / best_xi2``, the factor by which phase sensitivity beats the SQL
    """
    times = np.linspace(0, t_max, points)
    xis = [one_axis_twisting(n, t) for t in times]
    idx = int(np.argmin(xis))
    best = xis[idx]
    return {
        "sql": xis[0],
        "best_xi2": best,
        "best_chi_t": float(times[idx]),
        "squeezing_dB": float(10 * np.log10(best)),
        "metrological_gain": float(1 / best),
    }
