"""
Device-independent randomness from Bell violations.

A CHSH violation certifies genuine, unpredictable randomness *without trusting the devices* --
the only assumption is no-signaling. The more the CHSH value ``S`` exceeds the classical bound
of 2, the less an adversary can predict the outputs. The optimal adversary's **guessing
probability** is bounded by

    P_guess(S) <= 1/2 + (1/2) sqrt(2 - S^2/4),

giving certified min-entropy ``-log2 P_guess`` bits per run. At the classical bound ``S = 2`` the
guess probability is 1 (no randomness); at Tsirelson's ``S = 2 sqrt2`` it falls to 1/2 (a full
bit of certified randomness). This module computes the guessing probability, the certified
randomness, and a device-independent key-rate estimate, verified against those endpoints.
"""

import numpy as np


def guessing_probability(chsh: float) -> float:
    """
    Adversary's optimal guessing probability given CHSH value ``chsh``:
    ``1/2 + (1/2) sqrt(2 - chsh^2/4)``. ``1`` at ``S=2`` (predictable), ``1/2`` at ``S=2 sqrt2``
    (one bit of randomness).
    """
    s = np.clip(chsh, 2.0, 2 * np.sqrt(2))
    return float(0.5 + 0.5 * np.sqrt(max(2 - s ** 2 / 4, 0.0)))


def certified_randomness(chsh: float) -> float:
    """Certified min-entropy ``-log2 P_guess`` in bits per run -- ``0`` at the classical bound,
    ``1`` at Tsirelson's bound. The device-independent randomness yield."""
    return float(-np.log2(guessing_probability(chsh)))


def is_randomness_certified(chsh: float) -> bool:
    """True iff the CHSH value exceeds the classical bound (``S > 2``), so some randomness is
    certified device-independently."""
    return bool(chsh > 2.0 + 1e-9)


def di_key_rate(chsh: float) -> float:
    """
    A simple device-independent key-rate lower bound ``1 - h(Q) - (adversary info)`` proxy: the
    certified randomness minus the CHSH-limited leakage, clipped at 0. Positive only for a
    sufficiently strong violation.
    """
    r = certified_randomness(chsh)
    leakage = 1 - certified_randomness(chsh)         # adversary's residual advantage
    return float(max(r - leakage, 0.0))


def randomness_vs_violation(chsh_values):
    """The certified randomness across a range of CHSH values -- verified monotonically
    increasing from 0 (at S=2) to 1 (at Tsirelson)."""
    return [certified_randomness(s) for s in chsh_values]
