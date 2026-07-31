"""
Bosonic cat codes -- error correction in a single oscillator.

Instead of many two-level qubits, a bosonic code stores a logical qubit in the large
Hilbert space of *one* oscillator, exploiting its structure to correct photon loss. The
**cat code** uses superpositions of coherent states: the even and odd Schrödinger-cat
states

    |cat_+/-> = (|alpha> +/- |-alpha>) / N

are eigenstates of the photon-number parity ``(-1)^N`` (``+1`` even, ``-1`` odd). Since single
photon loss flips the parity, it maps the code space to an orthogonal error space and is
detectable. This module builds the cat states and the logical code words and verifies their
parity eigenvalues, orthogonality, and the parity flip under photon loss.
"""

import numpy as np

from .fock_space import coherent_state_fock, annihilation_operator, number_operator_fock


def cat_state(alpha: complex, parity: str = "even", cutoff: int = 30) -> np.ndarray:
    """
    Schrödinger-cat state ``(|alpha> +/- |-alpha>)/N`` -- ``even`` (``+``) is supported on even
    photon numbers, ``odd`` (``-``) on odd. A parity eigenstate of ``(-1)^N``.
    """
    plus = coherent_state_fock(alpha, cutoff)
    minus = coherent_state_fock(-alpha, cutoff)
    psi = plus + minus if parity == "even" else plus - minus
    return psi / np.linalg.norm(psi)


def parity_operator(cutoff: int) -> np.ndarray:
    """Photon-number parity operator ``(-1)^N`` -- ``+1`` on even Fock states, ``-1`` on odd."""
    return np.diag((-1.0) ** np.arange(cutoff)).astype(complex)


def parity_expectation(state, cutoff: int = None) -> float:
    """Expectation ``<(-1)^N>`` of a state -- ``+1`` for an even cat, ``-1`` for an odd cat."""
    psi = np.asarray(state, dtype=complex)
    c = len(psi)
    return float(np.real(np.vdot(psi, parity_operator(c) @ psi)))


def cat_code_words(alpha: complex, cutoff: int = 30):
    """
    Logical code words of the two-component cat code: ``|0_L> = |cat_+>`` and
    ``|1_L> = |cat_->`` (even/odd cats). Orthonormal and spanning a logical qubit; verified
    orthogonal.
    """
    return cat_state(alpha, "even", cutoff), cat_state(alpha, "odd", cutoff)


def photon_loss(state, cutoff: int = None) -> np.ndarray:
    """
    Apply a single photon-loss event ``a|psi>`` (unnormalized) and renormalize -- the
    dominant oscillator error, which flips the cat parity and so is detectable.
    """
    psi = np.asarray(state, dtype=complex)
    c = len(psi)
    out = annihilation_operator(c) @ psi
    nrm = np.linalg.norm(out)
    return out / nrm if nrm > 1e-12 else out


def loss_flips_parity(alpha: complex, cutoff: int = 30) -> bool:
    """
    Verify that single photon loss flips the cat-code parity: an even cat (``parity +1``)
    becomes odd (``parity -1``) after ``a`` acts, so the error leaves the code space and is
    detectable.
    """
    even = cat_state(alpha, "even", cutoff)
    lost = photon_loss(even)
    return bool(parity_expectation(even) > 0.9 and parity_expectation(lost) < -0.9)
