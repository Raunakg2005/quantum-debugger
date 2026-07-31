"""
Gaussian states in the covariance-matrix formalism.

A continuous-variable mode has quadratures ``(x, p)``; a Gaussian state is fully described
by its first moments (the displacement) and its ``2n x 2n`` **covariance matrix** ``sigma``.
In the convention where the vacuum is ``sigma = I``, physicality is the Robertson-Schrödinger
condition ``sigma + i Omega >= 0``, equivalently the **symplectic (Williamson) eigenvalues**
``nu_k >= 1``. From those eigenvalues follow the purity ``1/prod nu_k`` and the von Neumann
entropy. This module builds the standard Gaussian states (vacuum, squeezed, thermal) and
computes these invariants, verified against the harmonic-oscillator closed forms.
"""

import numpy as np


def omega(n_modes: int) -> np.ndarray:
    """The symplectic form ``Omega = ⊕ [[0,1],[-1,0]]`` on ``n_modes`` (``x,p`` ordering per
    mode)."""
    w = np.array([[0, 1], [-1, 0]], dtype=float)
    O = np.zeros((2 * n_modes, 2 * n_modes))
    for i in range(n_modes):
        O[2 * i:2 * i + 2, 2 * i:2 * i + 2] = w
    return O


def vacuum_covariance(n_modes: int) -> np.ndarray:
    """Covariance matrix of the vacuum (or any coherent state): the identity ``I_{2n}``."""
    return np.eye(2 * n_modes)


def squeezed_covariance(r: float, phi: float = 0.0) -> np.ndarray:
    """
    Single-mode squeezed-vacuum covariance: variances ``e^{-2r}`` and ``e^{2r}`` along the
    squeezed/anti-squeezed quadratures, rotated by ``phi``. A pure state (symplectic
    eigenvalue 1) that beats the vacuum noise in one quadrature.
    """
    S = np.diag([np.exp(-2 * r), np.exp(2 * r)])
    c, s = np.cos(phi), np.sin(phi)
    R = np.array([[c, -s], [s, c]])
    return R @ S @ R.T


def thermal_covariance(n_bar: float) -> np.ndarray:
    """Single-mode thermal-state covariance ``(2 n_bar + 1) I`` for mean photon number
    ``n_bar`` -- a mixed state with symplectic eigenvalue ``2 n_bar + 1``."""
    return (2 * n_bar + 1) * np.eye(2)


def symplectic_eigenvalues(cov) -> np.ndarray:
    """
    Williamson symplectic eigenvalues ``nu_k`` of a covariance matrix: the moduli of the
    eigenvalues of ``i Omega sigma`` (taken once each). They must be ``>= 1`` for a physical
    state; ``nu_k = 1`` for a pure mode.
    """
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0] // 2
    ev = np.linalg.eigvals(1j * omega(n) @ cov)
    nus = np.sort(np.abs(np.real_if_close(ev)))[::-1]
    return nus[:n]                                  # positive halves


def is_physical_covariance(cov, atol: float = 1e-9) -> bool:
    """True iff ``sigma`` is a valid covariance matrix: symmetric with all symplectic
    eigenvalues ``>= 1`` (the uncertainty principle)."""
    cov = np.asarray(cov, dtype=float)
    if not np.allclose(cov, cov.T, atol=atol):
        return False
    return bool(np.all(symplectic_eigenvalues(cov) >= 1 - atol))


def purity_gaussian(cov) -> float:
    """Purity ``Tr(rho^2) = 1 / prod nu_k`` of a Gaussian state from its symplectic
    eigenvalues: 1 for a pure state, ``1/(2 n_bar + 1)`` for a thermal state."""
    return float(1.0 / np.prod(symplectic_eigenvalues(cov)))


def gaussian_entropy(cov) -> float:
    """
    von Neumann entropy of a Gaussian state (in nats), summing the per-mode oscillator
    entropy ``g((nu-1)/2)`` with ``g(x) = (x+1)ln(x+1) - x ln x`` over the symplectic
    eigenvalues. Zero for a pure state.
    """
    def g(x):
        return (x + 1) * np.log(x + 1) - x * np.log(x) if x > 1e-12 else 0.0
    return float(sum(g((nu - 1) / 2) for nu in symplectic_eigenvalues(cov)))
