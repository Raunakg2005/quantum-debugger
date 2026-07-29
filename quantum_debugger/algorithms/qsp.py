"""
Quantum Signal Processing (QSP)

QSP is the one-qubit heart of modern quantum algorithms. Interleave a fixed "signal"
rotation ``W(x)`` (encoding a number ``x = cos theta`` in ``[-1, 1]``) with tunable
``Z`` rotations set by a phase sequence ``(phi_0, ..., phi_d)``:

    U(x) = R_z(phi_0) prod_{k=1}^{d} [ W(x) R_z(phi_k) ],

and the top-left matrix element ``<0|U(x)|0>`` becomes a degree-``d`` polynomial
``P(x)`` in the signal, of definite parity ``d mod 2`` and bounded by 1. Choosing the
phases *designs* the polynomial -- and lifting this to a block-encoded operator gives
Quantum Singular Value Transformation, the unifying framework behind amplitude
amplification, Hamiltonian simulation, and quantum linear algebra.

The cleanest check: with all phases zero, ``W(x)^d`` has ``<0|.|0> = T_d(x)``, the
Chebyshev polynomial of the first kind -- reproduced here to machine precision.
"""

import numpy as np


def signal_operator(x: float) -> np.ndarray:
    """The QSP signal operator ``W(x) = [[x, i sqrt(1-x^2)], [i sqrt(1-x^2), x]]`` (an
    X-rotation encoding ``x = cos theta``)."""
    s = np.sqrt(max(0.0, 1 - x * x))
    return np.array([[x, 1j * s], [1j * s, x]], dtype=complex)


def _rz(phi):
    return np.array([[np.exp(1j * phi), 0], [0, np.exp(-1j * phi)]], dtype=complex)


def qsp_unitary(phases, x: float) -> np.ndarray:
    """
    The QSP unitary ``R_z(phi_0) prod_k [W(x) R_z(phi_k)]`` for phase sequence
    ``phases`` at signal value ``x``. A sequence of ``d + 1`` phases applies ``d``
    signal operators (a degree-``d`` transform).
    """
    U = _rz(phases[0])
    for phi in phases[1:]:
        U = U @ signal_operator(x) @ _rz(phi)
    return U


def qsp_response(phases, xs) -> np.ndarray:
    """
    The QSP polynomial ``P(x) = Re <0|U(x)|0>`` evaluated at each ``x`` in ``xs`` for
    the given phase sequence -- a real degree-``d`` polynomial of parity ``d mod 2``,
    bounded by 1 in magnitude.
    """
    return np.array([float(np.real(qsp_unitary(phases, x)[0, 0])) for x in xs])


def chebyshev_via_qsp(degree: int, xs) -> np.ndarray:
    """
    The Chebyshev polynomial ``T_degree`` realized by QSP with all-zero phases
    (``<0|W(x)^degree|0>``), evaluated at ``xs``. Equals ``cos(degree * arccos(x))``.
    """
    phases = [0.0] * (degree + 1)
    return qsp_response(phases, xs)


def qsp_complementary_response(phases, xs):
    """
    The QSP achievable polynomial ``P(x) = <0|U(x)|0>`` together with its *complementary*
    partner ``Q(x)`` defined by ``<0|U(x)|1> = i sqrt(1-x^2) Q(x)``. The two obey the QSP
    completion identity

        |P(x)|^2 + (1 - x^2) |Q(x)|^2 = 1     for all x in [-1, 1],

    the algebraic condition that decides exactly which polynomials a phase sequence can
    realize (and the constraint a QSP-phase solver must satisfy). Returns ``(P, Q)`` as
    complex arrays over ``xs``; the tests verify the identity holds to machine precision.
    """
    xs = np.asarray(xs, dtype=float)
    P = np.empty(len(xs), dtype=complex)
    Q = np.empty(len(xs), dtype=complex)
    for i, x in enumerate(xs):
        U = qsp_unitary(phases, x)
        P[i] = U[0, 0]
        root = np.sqrt(max(1 - x**2, 0.0))
        Q[i] = U[0, 1] / (1j * root) if root > 1e-12 else 0.0
    return P, Q
