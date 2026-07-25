"""
Adiabatic quantum computation & the adiabatic theorem

An alternative to the circuit model: encode the answer in the ground state of a
"problem" Hamiltonian ``H_final``, start in the easily-prepared ground state of a
"driver" ``H_initial``, and slowly interpolate

    H(s) = (1 - s) H_initial + s H_final,      s = t / T,   0 -> 1.

The adiabatic theorem guarantees the system stays in the instantaneous ground state
-- ending in the ground state of ``H_final`` -- provided the total time ``T`` is large
compared to the inverse square of the minimum spectral gap along the path. Run too
fast and the system is excited (a diabatic transition). This module evolves the state
under the time-dependent Hamiltonian and measures the final ground-state fidelity,
verifying both regimes.
"""

import numpy as np
from scipy.linalg import expm


def _ground_state(H):
    _, vecs = np.linalg.eigh(H)
    return vecs[:, 0].astype(complex)


def adiabatic_evolution(h_initial, h_final, total_time: float, steps: int = None) -> dict:
    """
    Prepare the ground state of ``h_initial``, sweep ``H(s) = (1-s) H_i + s H_f`` over
    total time ``total_time``, and return how well the result matches the ground state
    of ``h_final``.

    ``steps`` defaults to ``max(50, 30 * total_time)`` (enough for the piecewise-constant
    integrator to be accurate). Returns dict with:
      * ``fidelity``        -- overlap-squared of the final state with the target ground state
      * ``final_energy``    -- ``<H_final>`` of the final state
      * ``target_energy``   -- exact ground energy of ``h_final``
      * ``min_gap``         -- the minimum spectral gap of ``H(s)`` along the path
      * ``adiabatic``       -- whether the run stayed near the ground state (fidelity > 0.9)
    """
    H_i = np.asarray(h_initial, dtype=complex)
    H_f = np.asarray(h_final, dtype=complex)
    if steps is None:
        steps = max(50, int(30 * total_time))

    psi = _ground_state(H_i)
    dt = total_time / steps
    min_gap = np.inf
    for k in range(steps):
        s = (k + 0.5) / steps
        H_s = (1 - s) * H_i + s * H_f
        ev = np.linalg.eigvalsh(H_s).real
        min_gap = min(min_gap, ev[1] - ev[0])
        psi = expm(-1j * H_s * dt) @ psi

    target = _ground_state(H_f)
    fidelity = float(abs(np.vdot(target, psi)) ** 2)
    return {
        "fidelity": fidelity,
        "final_energy": float(np.real(psi.conj() @ H_f @ psi)),
        "target_energy": float(np.linalg.eigvalsh(H_f).real.min()),
        "min_gap": float(min_gap),
        "adiabatic": fidelity > 0.9,
    }
