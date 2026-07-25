"""
Weak values (Aharonov-Albert-Vaidman)

Between a pre-selected state ``|psi>`` and a post-selected state ``|phi>``, a weakly
measured observable ``A`` reads not an eigenvalue but the **weak value**

    A_w = <phi|A|psi> / <phi|psi>,

which can lie far outside the spectrum of ``A`` -- even become complex. When the
pre- and post-selection are nearly orthogonal, ``A_w`` is *amplified* without bound
(the basis of weak-value metrology).

This module computes ``A_w`` directly and, independently, runs the actual weak
measurement: a pointer qubit coupled to the system by ``U = exp(-i g A x Y / 2)``,
post-selected on ``|phi>``. In the weak-coupling limit the pointer's ``<X>`` shift
per unit coupling converges to ``Re(A_w)`` -- verified numerically.
"""

import numpy as np
from scipy.linalg import expm

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)


def weak_value(A, pre, post) -> complex:
    """
    The weak value ``A_w = <post|A|pre> / <post|pre>`` of observable ``A`` for
    pre-selection ``pre`` and post-selection ``post`` (state vectors). May lie
    outside the eigenvalue range of ``A`` and may be complex.
    """
    A = np.asarray(A, dtype=complex)
    pre = np.asarray(pre, dtype=complex)
    post = np.asarray(post, dtype=complex)
    pre = pre / np.linalg.norm(pre)
    post = post / np.linalg.norm(post)
    overlap = np.vdot(post, pre)
    if abs(overlap) < 1e-15:
        raise ValueError("pre- and post-selection are orthogonal (weak value diverges)")
    return complex(np.vdot(post, A @ pre) / overlap)


def weak_measurement_shift(A, pre, post, coupling: float) -> float:
    """
    Run the actual weak measurement at strength ``coupling`` and return the pointer's
    ``<X>`` expectation after post-selection. A pointer qubit (initially ``|0>``) is
    coupled to the system by ``exp(-i g A x Y / 2)``; the system is then projected
    onto ``post``. For small ``g`` the shift is ``g * Re(A_w)`` -- see
    :func:`weak_value_demo`.
    """
    A = np.asarray(A, dtype=complex)
    pre = np.asarray(pre, dtype=complex) / np.linalg.norm(pre)
    post = np.asarray(post, dtype=complex) / np.linalg.norm(post)

    pointer0 = np.array([1, 0], dtype=complex)  # pointer = high qubit, system = low
    psi = np.kron(pointer0, pre)
    U = expm(-1j * coupling * np.kron(_Y, A) / 2)
    psi = U @ psi

    proj = np.kron(np.eye(2, dtype=complex), np.outer(post, post.conj()))
    psi = proj @ psi
    norm = np.linalg.norm(psi)
    if norm < 1e-15:
        raise ValueError("post-selection succeeds with vanishing probability")
    psi = psi / norm

    x_pointer = np.kron(_X, np.eye(2, dtype=complex))
    return float(np.real(psi.conj() @ x_pointer @ psi))


def weak_value_demo(A, pre, post, coupling: float = 1e-3) -> dict:
    """
    Compare the weak value with the measured weak-measurement pointer shift.

    Returns dict with ``weak_value`` (complex ``A_w``), ``real_part`` (``Re A_w``),
    ``pointer_shift_per_coupling`` (the measured ``<X>/g`` at small ``g``),
    ``outside_spectrum`` (whether ``Re A_w`` exceeds ``max|eigenvalue|`` of ``A``),
    and ``matches`` (shift ~ ``Re A_w``).
    """
    A = np.asarray(A, dtype=complex)
    aw = weak_value(A, pre, post)
    shift = weak_measurement_shift(A, pre, post, coupling) / coupling
    spectrum = np.max(np.abs(np.linalg.eigvalsh(A)))
    return {
        "weak_value": aw,
        "real_part": float(aw.real),
        "pointer_shift_per_coupling": shift,
        "outside_spectrum": bool(abs(aw.real) > spectrum + 1e-9),
        "matches": bool(abs(shift - aw.real) < 1e-2),
    }
