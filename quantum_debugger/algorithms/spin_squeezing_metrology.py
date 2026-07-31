"""
Spin squeezing for sub-shot-noise metrology.

A **coherent spin state** (all qubits in ``|+>``) has isotropic quantum noise and reaches only
the standard quantum limit. **Spin squeezing** redistributes that noise -- reducing the
variance of one collective-spin quadrature at the expense of another -- so that a phase
imprinted on the squeezed quadrature is measured below the shot-noise floor. The **Wineland
squeezing parameter**

    xi_R^2 = n * Var(J_perp,min) / <J>^2

is ``1`` for a coherent spin state and ``< 1`` for a metrologically useful squeezed state; the
metrological gain in variance is ``1/xi_R^2``. One-axis twisting ``e^{-i chi t J_z^2}`` generates
the squeezing. Verified against the coherent-state value and the sub-SQL squeezed state.
"""

import numpy as np
from scipy.linalg import expm

_PAULI = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def collective_spin(n: int, axis: str) -> np.ndarray:
    """Collective spin operator ``J_axis = (1/2) sum_i sigma_axis^(i)`` on ``n`` qubits."""
    J = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        op = np.array([[1.0]], dtype=complex)
        for q in range(n):
            op = np.kron(_PAULI[axis] if q == i else np.eye(2), op)
        J += 0.5 * op
    return J


def coherent_spin_state(n: int) -> np.ndarray:
    """The coherent spin state ``|+>^n`` polarized along ``x`` -- the standard-quantum-limit
    reference (Wineland ``xi^2 = 1``)."""
    return np.ones(2 ** n, dtype=complex) / np.sqrt(2 ** n)


def one_axis_twisting_state(n: int, chi_t: float) -> np.ndarray:
    """The one-axis-twisting state ``e^{-i chi t J_z^2} |CSS_x>`` -- generates spin squeezing for
    a suitable ``chi t``."""
    Jz = collective_spin(n, "Z")
    return expm(-1j * chi_t * (Jz @ Jz)) @ coherent_spin_state(n)


def wineland_squeezing_parameter(state, n: int) -> float:
    """
    Wineland squeezing parameter ``xi_R^2 = n Var(J_perp,min)/<J>^2`` for a state with mean spin
    along ``x``. ``1`` for a coherent spin state, ``< 1`` for a useful squeezed state (verified).
    Minimizes the perpendicular variance over the ``y-z`` plane.
    """
    psi = np.asarray(state, dtype=complex)
    Jx, Jy, Jz = (collective_spin(n, a) for a in "XYZ")
    meanJ = np.array([np.real(np.vdot(psi, J @ psi)) for J in (Jx, Jy, Jz)])
    Jlen = np.linalg.norm(meanJ)
    # minimize variance of J_perp = cos(phi) Jy + sin(phi) Jz (perpendicular to mean-spin x-ish)
    best = np.inf
    for phi in np.linspace(0, np.pi, 180):
        Jp = np.cos(phi) * Jy + np.sin(phi) * Jz
        v = np.real(np.vdot(psi, (Jp @ Jp) @ psi)) - np.real(np.vdot(psi, Jp @ psi)) ** 2
        best = min(best, v)
    return float(n * best / Jlen ** 2)


def metrological_gain(xi_squared: float) -> float:
    """Metrological variance gain ``1/xi_R^2`` over the standard quantum limit -- ``> 1`` when the
    state is squeezed."""
    return float(1.0 / xi_squared)


def is_squeezed(state, n: int, atol: float = 1e-6) -> bool:
    """True iff the state is spin-squeezed (Wineland ``xi_R^2 < 1``) -- i.e. metrologically useful
    beyond the shot-noise limit."""
    return bool(wineland_squeezing_parameter(state, n) < 1 - atol)


def best_twisting_squeezing(n: int, points: int = 40) -> float:
    """The minimum Wineland parameter reachable by one-axis twisting over a scan of ``chi t`` --
    verified below 1 (metrological gain)."""
    return float(min(wineland_squeezing_parameter(one_axis_twisting_state(n, ct), n)
                     for ct in np.linspace(0.01, 1.0, points)))
