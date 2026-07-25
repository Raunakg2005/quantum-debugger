"""
Clifford Data Regression (CDR)

A learning-based error mitigation method. The trick: near-Clifford circuits are
*classically simulable*, so for a set of training states you know both the exact
expectation and the noisy one. Fit a simple regression ``ideal ~= a * noisy + b`` on
that training data, then apply the learned correction to the real (non-Clifford)
circuit's noisy result.

CDR needs no model of the noise -- it learns the correction directly from data. For a
global-depolarizing-style channel the map is a pure rescaling (``b = 0``, ``a > 1``),
and CDR recovers the noise-free value exactly; for structured noise the linear fit
removes the dominant error. This module builds the regression on the density-matrix
engine and verifies the correction.
"""

import numpy as np


def fit_cdr_model(noisy_values, ideal_values) -> dict:
    """
    Fit the CDR linear model ``ideal ~= slope * noisy + intercept`` from paired training
    data (the noisy and exact expectations of the training states).

    Returns dict with ``slope``, ``intercept``, and ``r_squared`` (fit quality).
    """
    x = np.asarray(noisy_values, dtype=float)
    y = np.asarray(ideal_values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = np.sum((y - pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 1e-15 else 1.0
    return {"slope": float(slope), "intercept": float(intercept), "r_squared": float(r2)}


def apply_cdr(model: dict, noisy_value: float) -> float:
    """Apply a fitted CDR ``model`` to correct a single ``noisy_value``."""
    return float(model["slope"] * noisy_value + model["intercept"])


def cdr_mitigate(noisy_fn, ideal_fn, training_states, target_state,
                 ideal_target=None) -> dict:
    """
    Full CDR: measure each ``training_states`` element with ``noisy_fn`` and ``ideal_fn``
    (noisy and exact expectations), fit the regression, and correct ``target_state``'s
    noisy value.

    Returns dict with ``model`` (fitted parameters), ``raw`` (target noisy value),
    ``mitigated`` (CDR-corrected), and -- if ``ideal_target`` is given -- ``ideal``,
    ``raw_error``, ``mitigated_error``, ``improved``.
    """
    noisy_train = [noisy_fn(s) for s in training_states]
    ideal_train = [ideal_fn(s) for s in training_states]
    model = fit_cdr_model(noisy_train, ideal_train)

    raw = noisy_fn(target_state)
    mitigated = apply_cdr(model, raw)
    result = {"model": model, "raw": raw, "mitigated": mitigated}
    if ideal_target is None:
        ideal_target = ideal_fn(target_state)
    result.update(
        ideal=ideal_target,
        raw_error=abs(raw - ideal_target),
        mitigated_error=abs(mitigated - ideal_target),
        improved=abs(mitigated - ideal_target) < abs(raw - ideal_target) + 1e-12,
    )
    return result
