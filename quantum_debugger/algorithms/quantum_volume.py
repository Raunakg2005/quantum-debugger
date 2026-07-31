"""
Quantum volume -- a single-number benchmark of usable circuit size.

Quantum volume runs random square circuits (``n`` qubits, ``n`` layers of random two-qubit
gates) and asks whether the device reproduces the *heavy outputs* -- the bitstrings whose
ideal probability exceeds the median. A circuit "passes" if its **heavy-output probability**
(HOP) exceeds ``2/3``; the quantum volume is ``2^n`` for the largest ``n`` that passes with
confidence. For ideal Haar-random circuits the HOP converges to ``(1 + ln 2)/2 ~ 0.847``.
This module computes heavy outputs, the HOP, the pass criterion, and the ideal asymptote,
verified against those closed forms.
"""

import numpy as np


def heavy_outputs(ideal_probs):
    """Indices of the heavy outputs -- the outcomes whose ideal probability is *above the
    median* probability. The set the device must reproduce."""
    p = np.asarray(ideal_probs, dtype=float)
    median = np.median(p)
    return np.where(p > median)[0]


def heavy_output_probability(ideal_probs, sampled_indices=None) -> float:
    """
    Heavy-output probability (HOP): if ``sampled_indices`` is given, the fraction of samples
    landing on heavy outputs; otherwise the total *ideal* weight on the heavy set. The
    quantity quantum volume thresholds at ``2/3``.
    """
    p = np.asarray(ideal_probs, dtype=float)
    heavy = set(heavy_outputs(p).tolist())
    if sampled_indices is None:
        return float(sum(p[i] for i in heavy))
    s = np.asarray(sampled_indices)
    return float(np.mean([1.0 if i in heavy else 0.0 for i in s]))


def quantum_volume_pass(hop: float, threshold: float = 2.0 / 3.0) -> bool:
    """Quantum-volume pass criterion: the heavy-output probability must exceed ``2/3``."""
    return bool(hop > threshold)


def ideal_heavy_output_probability() -> float:
    """The asymptotic ideal HOP of Haar-random circuits, ``(1 + ln 2)/2 ~ 0.847`` -- the
    value a perfect device approaches, comfortably above the ``2/3`` threshold."""
    return float((1 + np.log(2)) / 2)


def quantum_volume(n_qubits_passed: int) -> int:
    """Quantum volume ``2^n`` for the largest square circuit width ``n`` that passes."""
    return int(2 ** n_qubits_passed)
