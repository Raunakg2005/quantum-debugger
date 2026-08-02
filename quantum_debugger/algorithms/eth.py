"""
The eigenstate thermalization hypothesis (ETH).

Why does an isolated chaotic quantum system reach thermal equilibrium? ETH answers: the individual
energy eigenstates already look thermal. Concretely, the matrix elements of a local observable ``O``
in the energy eigenbasis obey

    O_{mn} = O(E) delta_{mn} + e^{-S(E)/2} f(E, omega) R_{mn},

where ``O(E)`` is a smooth function of energy (so *diagonal* elements are a smooth curve with tiny
eigenstate-to-eigenstate fluctuations) and the *off-diagonal* elements are exponentially small
pseudo-random numbers. The practical consequences, verified here on random-matrix (chaotic)
Hamiltonians and contrasted with an integrable (diagonal) one:

* an eigenstate expectation value matches the microcanonical average (thermalization);
* the diagonal fluctuations and off-diagonal variance shrink as the Hilbert space grows.
"""

import numpy as np


def eigenbasis(H):
    """Diagonalize a Hermitian ``H``; returns sorted ``(energies, eigenvectors)`` with eigenvectors as
    columns."""
    H = np.asarray(H, dtype=complex)
    w, V = np.linalg.eigh(H)
    return w, V


def observable_matrix(V, O):
    """The observable in the energy eigenbasis, ``V^dagger O V`` -- diagonal entries are eigenstate
    expectations, off-diagonal entries the ETH pseudo-random elements."""
    V = np.asarray(V, dtype=complex)
    O = np.asarray(O, dtype=complex)
    return V.conj().T @ O @ V


def diagonal_elements(V, O):
    """The diagonal matrix elements ``O_{nn}`` -- the eigenstate expectation values."""
    return np.real(np.diag(observable_matrix(V, O)))


def offdiagonal_elements(V, O):
    """All off-diagonal matrix elements ``O_{mn}`` (``m != n``) as a flat array."""
    M = observable_matrix(V, O)
    mask = ~np.eye(M.shape[0], dtype=bool)
    return M[mask]


def eigenstate_expectation(V, O, index):
    """The expectation of ``O`` in energy eigenstate ``index``: ``<index|O|index>``."""
    M = observable_matrix(V, O)
    return float(M[index, index].real)


def microcanonical_average(energies, diag, E, half_width):
    """The microcanonical average of a diagonal-element series ``diag`` over the energy window
    ``[E - half_width, E + half_width]`` -- the thermal prediction at energy ``E``."""
    energies = np.asarray(energies, dtype=float)
    diag = np.asarray(diag, dtype=float)
    mask = np.abs(energies - E) <= half_width
    if not np.any(mask):
        return float("nan")
    return float(diag[mask].mean())


def eth_diagonal_fluctuation(V, O):
    """
    The size of eigenstate-to-eigenstate fluctuations of the diagonal elements: the RMS of
    ``O_{n+1,n+1} - O_{nn}`` over neighbouring eigenstates. ETH predicts this shrinks with system
    size (the diagonal is a smooth curve).
    """
    diag = diagonal_elements(V, O)
    return float(np.sqrt(np.mean(np.diff(diag) ** 2)))


def eth_offdiagonal_variance(V, O):
    """The variance of the off-diagonal matrix elements -- exponentially small under ETH, shrinking
    with the Hilbert-space dimension."""
    off = offdiagonal_elements(V, O)
    return float(np.var(off))


def eigenstate_matches_microcanonical(H, O, half_width_frac=0.15):
    """
    Test ETH thermalization: the mid-spectrum eigenstate expectation of ``O`` should match the
    microcanonical average over a small energy window around it. Returns the absolute difference.
    """
    w, V = eigenbasis(H)
    diag = diagonal_elements(V, O)
    mid = len(w) // 2
    span = (w.max() - w.min())
    micro = microcanonical_average(w, diag, w[mid], half_width_frac * span)
    return float(abs(diag[mid] - micro))


def thermalizes(H, O, tol=0.1, half_width_frac=0.15):
    """True iff the mid-spectrum eigenstate expectation matches the microcanonical average within
    ``tol`` -- the ETH thermalization criterion."""
    return eigenstate_matches_microcanonical(H, O, half_width_frac) <= tol
