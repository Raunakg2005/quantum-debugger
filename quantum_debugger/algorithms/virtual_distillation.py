"""
Virtual distillation (error mitigation by purification)

A noisy state ``rho`` is a mixture dominated by the intended pure state ``|psi>`` plus
error components. Raising it to a power concentrates weight on its largest eigenvector:
``rho^M / Tr(rho^M) -> |lambda_max><lambda_max|`` as ``M`` grows. So the *corrected*
expectation

    <O>_M = Tr(O rho^M) / Tr(rho^M)

is much closer to the noise-free value ``<psi|O|psi>`` than the raw ``Tr(O rho)`` --
without ever running error correction. On hardware this is estimated from ``M`` copies
of ``rho`` and a controlled-derangement circuit; here it is computed exactly on the
density-matrix engine to show the error suppression.
"""

import numpy as np


def virtual_distillation(rho, observable, m: int = 2) -> float:
    """
    Virtual-distillation estimate ``Tr(O rho^m) / Tr(rho^m)`` of the expectation of
    ``observable`` for the noisy density matrix ``rho`` with ``m`` copies. ``m = 1`` is
    the raw (uncorrected) expectation; larger ``m`` suppresses the error further.
    """
    R = np.asarray(rho, dtype=complex)
    O = np.asarray(observable, dtype=complex)
    Rm = np.linalg.matrix_power(R, m)
    return float(np.real(np.trace(O @ Rm) / np.trace(Rm)))


def distillation_report(rho, observable, ideal_state=None, m: int = 2) -> dict:
    """
    Compare raw and virtually-distilled expectation values.

    Returns dict with ``raw`` (``m=1``), ``distilled`` (order ``m``), and -- if the
    noise-free ``ideal_state`` is supplied -- ``ideal``, ``raw_error``,
    ``distilled_error``, and ``improved`` (whether distillation reduced the error).
    """
    O = np.asarray(observable, dtype=complex)
    raw = virtual_distillation(rho, O, m=1)
    distilled = virtual_distillation(rho, O, m=m)
    result = {"raw": raw, "distilled": distilled}
    if ideal_state is not None:
        psi = np.asarray(ideal_state, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        ideal = float(np.real(psi.conj() @ O @ psi))
        result.update(
            ideal=ideal,
            raw_error=abs(raw - ideal),
            distilled_error=abs(distilled - ideal),
            improved=abs(distilled - ideal) < abs(raw - ideal),
        )
    return result
