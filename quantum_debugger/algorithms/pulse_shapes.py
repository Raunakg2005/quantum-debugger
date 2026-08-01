"""
Control-pulse shapes and the pulse-area theorem.

The rotation a resonant drive produces is set by its *area*. For a drive
``H(t) = (Omega(t)/2) sigma_axis`` the qubit rotates by ``theta = integral Omega(t) dt`` about that
axis, so a pulse of area ``pi`` is a bit-flip (X) gate regardless of its shape. This module provides
the common envelopes -- square, Gaussian, and DRAG (Derivative Removal by Adiabatic Gate, which adds
a quadrature correction to suppress leakage) -- and the area/rotation relations, verified against the
exact rotation unitary.
"""

import numpy as np
from scipy.linalg import expm

_PAULI = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def square_pulse(amplitude, n_steps):
    """A constant (square) envelope of the given ``amplitude`` over ``n_steps`` samples."""
    return np.full(n_steps, float(amplitude))


def gaussian_pulse(times, t0, sigma, amplitude):
    """A Gaussian envelope ``amplitude * exp(-(t - t0)^2 / (2 sigma^2))`` sampled at ``times``."""
    t = np.asarray(times, dtype=float)
    return amplitude * np.exp(-((t - t0) ** 2) / (2.0 * sigma ** 2))


def drag_pulse(times, t0, sigma, amplitude, beta):
    """
    A DRAG pulse: the in-phase Gaussian envelope and its quadrature correction
    ``-beta * d/dt(Gaussian)`` that cancels leakage to a nearby level. Returns ``(I, Q)`` envelopes.
    """
    t = np.asarray(times, dtype=float)
    I = gaussian_pulse(t, t0, sigma, amplitude)
    Q = -beta * (-(t - t0) / sigma ** 2) * I
    return I, Q


def pulse_area(envelope, dt):
    """The pulse area ``integral Omega(t) dt`` -- the rotation angle a resonant drive produces."""
    return float(np.sum(np.asarray(envelope, dtype=float)) * dt)


def gaussian_area(sigma, amplitude):
    """Analytic area of a (full) Gaussian envelope, ``amplitude * sigma * sqrt(2 pi)``."""
    return float(amplitude * sigma * np.sqrt(2.0 * np.pi))


def rotation_from_area(area):
    """The rotation angle equals the pulse area, ``theta = area`` (pulse-area theorem)."""
    return float(area)


def pi_pulse_amplitude(duration):
    """The constant amplitude whose area over ``duration`` is ``pi`` -- a square pi (bit-flip) pulse:
    ``Omega = pi / duration``."""
    return float(np.pi / duration)


def pulse_unitary(area, axis="X"):
    """The single-qubit rotation ``exp(-i (area/2) sigma_axis)`` produced by a pulse of the given
    ``area`` about ``axis`` -- a ``pi`` pulse about X is the bit-flip gate (up to global phase)."""
    return expm(-1j * (area / 2.0) * _PAULI[axis])


def pi_pulse_is_bit_flip(axis="X", atol=1e-9):
    """Verify the pulse-area theorem: an area-``pi`` pulse about ``X`` equals the Pauli-X gate up to
    a global phase (``|Tr(X^dagger U)| / 2 = 1``)."""
    U = pulse_unitary(np.pi, axis)
    P = _PAULI[axis]
    return bool(np.isclose(abs(np.trace(P.conj().T @ U)) / 2.0, 1.0, atol=atol))


def square_pulse_unitary(amplitude, duration, axis="X"):
    """The unitary of a square resonant pulse: ``exp(-i (amplitude*duration/2) sigma_axis)`` -- area
    equals ``amplitude * duration``."""
    return pulse_unitary(amplitude * duration, axis)
