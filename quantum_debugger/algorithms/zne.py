"""
Zero-Noise Extrapolation (ZNE)

The most widely used error-mitigation method. You cannot turn a device's noise *down*,
but you can turn it *up* -- run the computation at several amplified noise levels,
measure the observable at each, and extrapolate the trend back to the zero-noise limit.

Here noise is amplified by *folding*: applying the noise channel ``c`` times gives noise
scale ``c``. Measuring ``<O>(c)`` at ``c = 1, 2, 3, ...`` and fitting a model in ``c``
(linear/Richardson, or exponential when the observable decays geometrically -- as
depolarizing noise makes it) recovers the noise-free value ``<O>(0)``. This module runs
the amplification on the density-matrix engine and verifies the extrapolation.
"""

import numpy as np


def fold_noise_expectation(density_matrix_factory, channels_per_scale, observable,
                           scale: int) -> float:
    """
    Expectation of ``observable`` at integer noise ``scale``: rebuild the state via
    ``density_matrix_factory()`` and apply ``channels_per_scale`` (a callable taking the
    DensityMatrix and applying one noise layer) ``scale`` times.
    """
    dm = density_matrix_factory()
    O = np.asarray(observable, dtype=complex)
    for _ in range(scale):
        channels_per_scale(dm)
    return float(np.real(np.trace(O @ dm.rho)))


def extrapolate_zero_noise(scales, values, method: str = "linear") -> float:
    """
    Extrapolate measured ``values`` at noise ``scales`` to the zero-noise limit.

    ``method`` is ``"linear"`` (Richardson, a straight-line fit) or ``"exponential"``
    (fit ``log|value|`` linearly -- exact when the observable decays geometrically).
    Returns the estimated noise-free value.
    """
    scales = np.asarray(scales, dtype=float)
    values = np.asarray(values, dtype=float)
    if method == "linear":
        return float(np.polyval(np.polyfit(scales, values, 1), 0.0))
    if method == "exponential":
        sign = np.sign(values[0]) if values[0] != 0 else 1.0
        fit = np.polyfit(scales, np.log(np.abs(values)), 1)
        return float(sign * np.exp(np.polyval(fit, 0.0)))
    raise ValueError("method must be 'linear' or 'exponential'")


def zero_noise_extrapolation(density_matrix_factory, noise_layer, observable,
                             scales=(1, 2, 3), method: str = "exponential",
                             ideal_state=None) -> dict:
    """
    Full ZNE: measure ``observable`` at each noise ``scale`` (noise amplified by folding
    the ``noise_layer``) and extrapolate to zero noise.

    Returns dict with ``values`` (per scale), ``raw`` (scale-1 value), ``mitigated``
    (the extrapolation), and -- if ``ideal_state`` is given -- ``ideal``, ``raw_error``,
    ``mitigated_error``, ``improved``.
    """
    values = [
        fold_noise_expectation(density_matrix_factory, noise_layer, observable, s)
        for s in scales
    ]
    mitigated = extrapolate_zero_noise(scales, values, method)
    result = {"values": values, "raw": values[0], "mitigated": mitigated}
    if ideal_state is not None:
        psi = np.asarray(ideal_state, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        ideal = float(np.real(psi.conj() @ np.asarray(observable, dtype=complex) @ psi))
        result.update(
            ideal=ideal,
            raw_error=abs(values[0] - ideal),
            mitigated_error=abs(mitigated - ideal),
            improved=abs(mitigated - ideal) < abs(values[0] - ideal) + 1e-12,
        )
    return result
