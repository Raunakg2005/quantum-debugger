"""
Single-qubit relaxation and decoherence: T1, T2, and Bloch-vector decay.

For a qubit the Lindblad dynamics reduces to a closed form on the Bloch vector. Amplitude damping
at rate ``gamma_1`` relaxes the population (energy decay) with time constant ``T1 = 1/gamma_1``;
adding pure dephasing at rate ``gamma_phi`` shrinks the coherence with

    1/T2 = 1/(2 T1) + 1/T_phi,      T_phi = 1/gamma_phi,

so the coherence time is bounded by ``T2 <= 2 T1``. In the Bloch picture the transverse components
``(r_x, r_y)`` decay to zero as ``e^{-t/T2}`` while the longitudinal component ``r_z`` relaxes to
its equilibrium value as ``e^{-t/T1}``. This module gives those closed forms and the T1/T2
relations, each verified against the exact Lindblad evolution.
"""

import numpy as np

from .lindblad import evolve_lindblad, amplitude_damping_jump, dephasing_jump

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def bloch_vector(rho):
    """The Bloch vector ``(r_x, r_y, r_z)`` of a qubit density matrix, ``r_i = Tr(sigma_i rho)``."""
    rho = np.asarray(rho, dtype=complex)
    return np.array([np.trace(_X @ rho).real,
                     np.trace(_Y @ rho).real,
                     np.trace(_Z @ rho).real])


def density_from_bloch(r):
    """The density matrix ``(I + r . sigma)/2`` for a Bloch vector ``r = (r_x, r_y, r_z)``."""
    rx, ry, rz = r
    return 0.5 * (_I + rx * _X + ry * _Y + rz * _Z)


def t2_from_t1_tphi(T1, T_phi):
    """The coherence time from ``1/T2 = 1/(2 T1) + 1/T_phi``."""
    return 1.0 / (1.0 / (2.0 * T1) + 1.0 / T_phi)


def t2_upper_bound(T1):
    """The fundamental limit ``T2 <= 2 T1`` -- reached only with no pure dephasing."""
    return 2.0 * T1


def relaxation_times(gamma_1, gamma_phi):
    """
    The relaxation/decoherence times implied by amplitude-damping rate ``gamma_1`` and
    pure-dephasing rate ``gamma_phi``: ``T1 = 1/gamma_1``, ``T_phi = 1/gamma_phi``, and the combined
    ``T2`` (with ``1/T2 = gamma_1/2 + gamma_phi``).
    """
    T1 = 1.0 / gamma_1
    T_phi = np.inf if gamma_phi == 0 else 1.0 / gamma_phi
    inv_T2 = gamma_1 / 2.0 + gamma_phi
    return {"T1": T1, "T_phi": T_phi, "T2": 1.0 / inv_T2}


def bloch_decay(r0, t, gamma_1, gamma_phi=0.0):
    """
    Closed-form Bloch vector at time ``t`` under amplitude damping (``gamma_1``) plus pure dephasing
    (``gamma_phi``): transverse components decay as ``e^{-t/T2}``, the longitudinal component relaxes
    toward ``+1`` (the ground state) as ``e^{-t/T1}``.
    """
    rx0, ry0, rz0 = r0
    T1 = 1.0 / gamma_1
    inv_T2 = gamma_1 / 2.0 + gamma_phi
    ez = np.exp(-t / T1)
    et = np.exp(-inv_T2 * t)
    return np.array([rx0 * et, ry0 * et, 1.0 + (rz0 - 1.0) * ez])


def bloch_decay_matches_lindblad(r0, t, gamma_1, gamma_phi=0.0, atol=1e-6):
    """True iff the closed-form :func:`bloch_decay` agrees with the exact Lindblad evolution under
    the amplitude-damping and dephasing jump operators."""
    rho0 = density_from_bloch(r0)
    jumps = [amplitude_damping_jump(gamma_1)]
    if gamma_phi > 0:
        jumps.append(dephasing_jump(gamma_phi))
    rho_t = evolve_lindblad(np.zeros((2, 2), dtype=complex), jumps, rho0, t)
    return bool(np.allclose(bloch_vector(rho_t), bloch_decay(r0, t, gamma_1, gamma_phi), atol=atol))


def purity(rho):
    """Purity ``Tr(rho^2)`` -- 1 for a pure state, 1/2 for the maximally mixed qubit; decreases under
    decoherence."""
    rho = np.asarray(rho, dtype=complex)
    return float(np.trace(rho @ rho).real)
