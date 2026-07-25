"""
Quantum Zeno effect

"A watched pot never boils": frequent measurement freezes coherent evolution.
A qubit starting in ``|0>`` under a Rabi drive ``U(t) = exp(-i omega t X / 2)``
would flip to ``|1>``; interrupting the drive with ``N`` projective measurements
suppresses the transition, and in the limit ``N -> infinity`` the state never
leaves ``|0>`` at all.

Two exactly-solvable variants, both simulated as genuine channels on the
density-matrix engine and verified against their closed forms:

  * **Unread measurements** (decoherence in the measurement basis,
    ``rho -> P0 rho P0 + P1 rho P1`` after each drive interval): the final
    population of ``|0>`` is exactly ``1/2 + cos^N(omega T / N) / 2``.
  * **Post-selected survival** (outcome 0 demanded every time): the probability of
    passing all ``N`` measurements is exactly ``cos^{2N}(omega T / 2N)``.

Both tend to 1 as ``N`` grows, while the measurement-free drive leaves only
``cos^2(omega T / 2)`` in ``|0>``.

Reference: Misra & Sudarshan, "The Zeno's paradox in quantum theory"
(J. Math. Phys. 18, 756, 1977).
"""

import numpy as np

from ..density_matrix import DensityMatrix

_P0 = np.array([[1, 0], [0, 0]], dtype=complex)
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)


def _rabi(theta):
    """exp(-i theta X / 2): rotation by theta about X."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def quantum_zeno(omega_t: float, n_measurements: int) -> dict:
    """
    Drive a qubit from ``|0>`` for total Rabi angle ``omega_t``, interrupted by
    ``n_measurements`` equally spaced *unread* projective measurements (each applied
    as the exact measurement channel). Simulated on the density matrix.

    Returns dict with:
      * ``survival``          -- final population of ``|0>``
      * ``analytic``          -- ``1/2 + cos^N(omega_t / N) / 2`` (matches exactly)
      * ``free_survival``     -- no measurements: ``cos^2(omega_t / 2)``
      * ``frozen``            -- whether measuring beat free evolution
    """
    if n_measurements < 1:
        raise ValueError("n_measurements must be >= 1")
    N = n_measurements
    U = _rabi(omega_t / N)

    dm = DensityMatrix(1)
    for _ in range(N):
        dm.apply_unitary(U, [0])
        dm.rho = _P0 @ dm.rho @ _P0 + _P1 @ dm.rho @ _P1  # unread measurement

    survival = float(np.real(dm.rho[0, 0]))
    analytic = 0.5 + 0.5 * np.cos(omega_t / N) ** N
    free = float(np.cos(omega_t / 2) ** 2)
    return {
        "survival": survival,
        "analytic": float(analytic),
        "free_survival": free,
        "frozen": survival > free,
    }


def zeno_postselected(omega_t: float, n_measurements: int) -> dict:
    """
    Same drive, but demanding measurement outcome 0 *every* time (post-selection).
    The probability of surviving all ``N`` checks is exactly
    ``cos^{2N}(omega_t / 2N) -> 1`` as ``N`` grows -- and the surviving state is
    still exactly ``|0>``.

    Returns dict with ``survival_probability``, ``analytic``, and
    ``state_fidelity`` (of the surviving state to ``|0>``; exactly 1).
    """
    if n_measurements < 1:
        raise ValueError("n_measurements must be >= 1")
    N = n_measurements
    U = _rabi(omega_t / N)

    dm = DensityMatrix(1)
    prob = 1.0
    for _ in range(N):
        dm.apply_unitary(U, [0])
        kept = _P0 @ dm.rho @ _P0
        p = float(np.real(np.trace(kept)))
        prob *= p
        if p < 1e-15:  # branch impossible (e.g. a full pi pulse before one check)
            prob = 0.0
            dm.rho = _P0.copy()  # the demanded outcome state, reached with prob 0
            break
        dm.rho = kept / p

    return {
        "survival_probability": prob,
        "analytic": float(np.cos(omega_t / (2 * N)) ** (2 * N)),
        "state_fidelity": float(np.real(dm.rho[0, 0])),
    }
