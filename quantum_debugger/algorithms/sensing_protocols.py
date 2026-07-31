"""
Sensing protocols -- turning quantum Fisher information into precision.

Given the QFI of a probe, these formulas translate it into the operational figures of a
sensing experiment: the signal-to-noise ratio, the phase and frequency precision from the
Cramér-Rao bound, the ``sqrt(n)`` gain of an entangled (Heisenberg) probe over an
uncorrelated one, and the QFI-per-particle that distinguishes standard-quantum-limited
(``1``) from Heisenberg-limited (``n``) sensing. All are closed-form and verified against the
QFI limits.
"""

import numpy as np


def signal_to_noise(qfi: float, shots: int) -> float:
    """Signal-to-noise ratio ``sqrt(shots * F_Q)`` of a phase measurement -- grows with the QFI
    and the number of repetitions."""
    return float(np.sqrt(shots * qfi))


def phase_precision(qfi: float, shots: int) -> float:
    """Phase precision ``1/sqrt(shots * F_Q)`` from the Cramér-Rao bound."""
    return float(1.0 / np.sqrt(shots * qfi))


def frequency_precision(qfi: float, interrogation_time: float, shots: int) -> float:
    """Frequency precision ``1/(sqrt(shots F_Q) * T)`` -- phase precision divided by the
    interrogation time ``T`` (longer ``T`` sharpens the fringe)."""
    return float(1.0 / (np.sqrt(shots * qfi) * interrogation_time))


def entanglement_gain(n: int) -> float:
    """Precision gain ``sqrt(n)`` of a Heisenberg-limited (entangled) probe over ``n``
    uncorrelated probes -- the metrological payoff of entanglement."""
    return float(np.sqrt(n))


def qfi_per_particle(qfi: float, n: int) -> float:
    """QFI per particle ``F_Q / n`` -- ``1`` at the standard quantum limit, ``n`` at the
    Heisenberg limit, the scaling that certifies a metrological quantum advantage."""
    return float(qfi / n)


def is_heisenberg_scaling(qfi_values, n_values, atol: float = 0.2) -> bool:
    """
    True iff the QFI scales as ``n^2`` (Heisenberg) rather than ``n`` (standard limit), checked by
    the log-log slope of QFI vs ``n`` being near 2. The signature of a genuinely quantum-enhanced
    sensor.
    """
    slope = np.polyfit(np.log(n_values), np.log(qfi_values), 1)[0]
    return bool(abs(slope - 2) < atol)
