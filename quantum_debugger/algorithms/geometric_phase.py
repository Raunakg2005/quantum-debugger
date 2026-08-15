"""
Geometric (Pancharatnam-Berry) phase

Carry a qubit around a closed loop of states and it acquires a phase that depends
only on the *geometry* of the loop -- not on timing, energy, or dynamics. For a
geodesic triangle of Bloch vectors ``n1 -> n2 -> n3 -> n1`` the Pancharatnam phase

    gamma = arg( <n1|n2> <n2|n3> <n3|n1> ) = Omega / 2   (mod 2 pi),

where ``Omega`` is the solid angle of the triangle, signed right-handed by
``sign(n1 . (n2 x n3))``. (The textbook form ``-Omega'/2`` refers to the
complementary cap ``Omega' = 4 pi - Omega`` traversed with the loop -- the two
agree mod ``2 pi`` because a full sphere contributes ``e^{-i 4 pi / 2} = 1`` for
spin 1/2.) This module computes ``gamma`` from the actual spinor overlaps and
verifies it against the solid angle computed *classically* (spherical excess,
L'Huilier's theorem) -- two entirely independent computations that must agree.

The phase is gauge invariant (re-phasing any intermediate state leaves it
unchanged) and orientation-odd (reversing the loop flips its sign). Geometric
phases of this kind are the working principle of holonomic quantum gates.
"""

import numpy as np


def bloch_spinor(n) -> np.ndarray:
    """The spin-up state along unit Bloch vector ``n``: ``(cos(t/2), e^{i p} sin(t/2))``."""
    n = np.asarray(n, dtype=float)
    n = n / np.linalg.norm(n)
    theta = np.arccos(np.clip(n[2], -1, 1))
    phi = np.arctan2(n[1], n[0])
    return np.array(
        [np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)], dtype=complex
    )


def pancharatnam_phase(states) -> float:
    """
    The Pancharatnam phase of a closed loop of states:
    ``arg( <s1|s2> <s2|s3> ... <sN|s1> )`` in radians. Gauge invariant -- each
    state may carry an arbitrary phase without changing the result.
    """
    total = 1.0 + 0j
    N = len(states)
    for i in range(N):
        total *= np.vdot(states[i], states[(i + 1) % N])
    return float(np.angle(total))


def solid_angle(n1, n2, n3) -> float:
    """
    Signed solid angle of the geodesic triangle with vertices at unit vectors
    ``n1, n2, n3`` (positive for counterclockwise orientation seen from outside),
    via the spherical excess ``E = A + B + C - pi`` (L'Huilier), signed by
    ``sign(n1 . (n2 x n3))``.
    """
    vs = [np.asarray(v, dtype=float) for v in (n1, n2, n3)]
    vs = [v / np.linalg.norm(v) for v in vs]
    a = np.arccos(np.clip(np.dot(vs[1], vs[2]), -1, 1))
    b = np.arccos(np.clip(np.dot(vs[0], vs[2]), -1, 1))
    c = np.arccos(np.clip(np.dot(vs[0], vs[1]), -1, 1))
    s = (a + b + c) / 2
    inner = (
        np.tan(s / 2) * np.tan((s - a) / 2) * np.tan((s - b) / 2) * np.tan((s - c) / 2)
    )
    E = 4 * np.arctan(np.sqrt(max(0.0, inner)))
    orientation = np.sign(np.dot(vs[0], np.cross(vs[1], vs[2])))
    return float(orientation * E)


def berry_phase_triangle(n1, n2, n3) -> dict:
    """
    Transport a qubit around the geodesic Bloch triangle ``n1 -> n2 -> n3 -> n1``
    and compare the quantum Pancharatnam phase with the classical geometry:

        gamma = Omega / 2   (mod 2 pi),

    with ``Omega`` the right-hand-signed solid angle (see module docstring for the
    relation to the textbook ``-Omega'/2`` convention).

    Returns dict with ``phase`` (from spinor overlaps), ``solid_angle`` (from
    spherical trigonometry), ``analytic`` (``Omega/2`` wrapped to ``(-pi, pi]``),
    and ``matches``.
    """
    states = [bloch_spinor(n) for n in (n1, n2, n3)]
    gamma = pancharatnam_phase(states)
    omega = solid_angle(n1, n2, n3)
    analytic = float(np.angle(np.exp(1j * omega / 2)))
    return {
        "phase": gamma,
        "solid_angle": omega,
        "analytic": analytic,
        "matches": bool(abs(np.angle(np.exp(1j * (gamma - analytic)))) < 1e-9),
    }
