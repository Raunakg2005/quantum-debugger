"""
Symplectic transforms -- the Gaussian unitaries.

Passive and active linear-optical elements (phase shifters, beamsplitters, squeezers) act
on the quadratures by **symplectic** matrices ``S`` -- those preserving the symplectic form,
``S Omega S^T = Omega``. A Gaussian unitary transforms a covariance matrix as
``sigma -> S sigma S^T`` and a displacement as ``d -> S d``. This module provides the
generators of the Gaussian group and verifies they are symplectic and that they map
physical states to physical states.
"""

import numpy as np

from .gaussian_states import omega


def is_symplectic(S, atol: float = 1e-9) -> bool:
    """True iff ``S Omega S^T = Omega`` -- ``S`` is a symplectic (Gaussian-unitary)
    transform."""
    S = np.asarray(S, dtype=float)
    n = S.shape[0] // 2
    O = omega(n)
    return bool(np.allclose(S @ O @ S.T, O, atol=atol))


def phase_rotation_symplectic(phi: float) -> np.ndarray:
    """Single-mode phase-space rotation (phase shifter) by ``phi`` -- a passive symplectic
    ``[[cos, sin], [-sin, cos]]``."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[c, s], [-s, c]])


def squeezing_symplectic(r: float, phi: float = 0.0) -> np.ndarray:
    """Single-mode squeezing symplectic ``diag(e^{-r}, e^{r})`` (rotated by ``phi``) -- an
    active transform that squeezes one quadrature."""
    S = np.diag([np.exp(-r), np.exp(r)])
    c, s = np.cos(phi), np.sin(phi)
    R = np.array([[c, -s], [s, c]])
    return R @ S @ R.T


def beamsplitter_symplectic(theta: float) -> np.ndarray:
    """
    Two-mode beamsplitter symplectic with transmissivity ``cos^2(theta)`` -- a passive
    element mixing the quadratures of two modes (``x1,p1,x2,p2`` ordering).
    """
    c, s = np.cos(theta), np.sin(theta)
    S = np.eye(4)
    S[0, 0] = S[1, 1] = S[2, 2] = S[3, 3] = c
    S[0, 2] = S[1, 3] = s
    S[2, 0] = S[3, 1] = -s
    return S


def apply_symplectic(cov, S) -> np.ndarray:
    """Transform a covariance matrix by a Gaussian unitary: ``sigma -> S sigma S^T``."""
    S = np.asarray(S, dtype=float)
    return S @ np.asarray(cov, dtype=float) @ S.T


def two_mode_squeezing_symplectic(r: float) -> np.ndarray:
    """
    Two-mode squeezing symplectic -- the entangling transform that creates EPR/two-mode
    squeezed states from two vacua (``x1,p1,x2,p2`` ordering).
    """
    ch, sh = np.cosh(r), np.sinh(r)
    S = np.zeros((4, 4))
    S[0, 0] = S[1, 1] = S[2, 2] = S[3, 3] = ch
    S[0, 2] = S[2, 0] = sh
    S[1, 3] = S[3, 1] = -sh
    return S
