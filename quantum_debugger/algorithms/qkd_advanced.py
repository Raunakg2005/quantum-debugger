"""
Quantum key distribution -- key rates and security thresholds.

QKD turns quantum correlations into shared secret keys. The **secret key rate** after error
correction and privacy amplification depends on the observed **quantum bit error rate (QBER)**:

* **BB84** (four states, two bases): ``r = 1 - 2 h(QBER)`` -- positive below the famous
  ``QBER = 11%`` threshold.
* **Six-state** (three bases): a slightly higher threshold ``~12.6%`` thanks to more symmetry
  constraints on the eavesdropper.
* **E91 (Ekert)**: security is certified by a CHSH violation; the QBER is read off the CHSH
  value ``S`` via ``QBER = (1 - S/(2 sqrt2))/2``.

This module implements the key-rate formulas, the binary entropy, and the QBER thresholds, and
verifies the rates vanish exactly at their thresholds.
"""

import numpy as np


def binary_entropy(p: float) -> float:
    """Binary entropy ``h(p)``."""
    if p <= 0 or p >= 1:
        return 0.0
    return float(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


def bb84_key_rate(qber: float) -> float:
    """BB84 asymptotic secret key rate ``1 - 2 h(QBER)`` (Shor-Preskill) -- clipped at 0.
    Positive below ``QBER ~ 11%``."""
    return float(max(0.0, 1 - 2 * binary_entropy(qber)))


def bb84_threshold() -> float:
    """The BB84 security threshold ``QBER ~ 0.110`` where the key rate hits zero -- verified via
    :func:`bb84_key_rate`."""
    # solve 1 - 2 h(q) = 0  ->  h(q) = 1/2
    from scipy.optimize import brentq
    return float(brentq(lambda q: binary_entropy(q) - 0.5, 1e-6, 0.5 - 1e-6))


def six_state_key_rate(qber: float) -> float:
    """
    Six-state protocol key rate ``1 - h(QBER) - QBER - (1-QBER) h((1-3 QBER/2)/(1-QBER)) ...``
    approximated by the standard ``1 + (1-1.5 Q) log2(1-1.5 Q) + 1.5 Q log2(0.5 Q)`` form,
    clipped at 0 -- a higher threshold (``~12.6%``) than BB84.
    """
    return float(max(0.0, _six_state_rate_unclipped(qber)))


def _six_state_rate_unclipped(q: float) -> float:
    if q <= 0:
        return 1.0
    return 1 + (1 - 1.5 * q) * np.log2(max(1 - 1.5 * q, 1e-12)) + 1.5 * q * np.log2(max(0.5 * q, 1e-12))


def six_state_threshold() -> float:
    """The six-state security threshold ``QBER ~ 0.126`` where the (unclipped) key rate crosses
    zero -- verified above the BB84 threshold."""
    from scipy.optimize import brentq
    return float(brentq(_six_state_rate_unclipped, 0.05, 0.2))


def qber_from_chsh(chsh: float) -> float:
    """The QBER inferred from a CHSH value ``S`` in the E91 protocol,
    ``QBER = (1 - S/(2 sqrt2))/2`` -- 0 at Tsirelson's bound, ``~14.6%`` at the classical bound."""
    return float((1 - chsh / (2 * np.sqrt(2))) / 2)


def e91_key_rate(chsh: float) -> float:
    """
    E91 (Ekert) secret key rate from the CHSH value: convert to QBER and apply the BB84 rate.
    Positive only for a strong-enough violation (``S`` well above 2); maximal at Tsirelson's
    bound.
    """
    return bb84_key_rate(qber_from_chsh(chsh))


def secret_fraction(qber: float, protocol: str = "bb84") -> float:
    """The asymptotic secret fraction for a protocol at a given QBER -- the fraction of sifted
    bits that become secret key."""
    return {"bb84": bb84_key_rate, "six_state": six_state_key_rate}[protocol](qber)


def sifting_ratio(protocol: str = "bb84") -> float:
    """The basis-reconciliation (sifting) efficiency: the fraction of sent qubits kept after
    Alice and Bob compare bases -- ``1/2`` for BB84, ``1/3`` for six-state (more bases)."""
    return {"bb84": 0.5, "six_state": 1.0 / 3.0}[protocol]


def decoy_state_gain(mu: float, transmittance: float) -> float:
    """
    Decoy-state single-photon gain estimate ``mu e^{-mu} * transmittance`` -- the fraction of
    pulses that are single-photon *and* detected, the term that defeats photon-number-splitting
    attacks in a weak-coherent-pulse BB84. Maximized near ``mu ~ 0.5``.
    """
    return float(mu * np.exp(-mu) * transmittance)
