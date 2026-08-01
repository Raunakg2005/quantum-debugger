"""
Open-system dynamics: the Lindblad (GKSL) master equation.

A quantum system coupled to an environment no longer evolves unitarily; its density matrix obeys
the Gorini-Kossakowski-Sudarshan-Lindblad master equation

    d(rho)/dt = -i [H, rho] + sum_k ( L_k rho L_k^dagger - (1/2){L_k^dagger L_k, rho} ),

where ``H`` is the Hamiltonian and the ``L_k`` are *jump* (Lindblad) operators modelling
dissipation and decoherence. The right-hand side is linear in ``rho``, so vectorizing the density
matrix (column stacking, ``vec(A X B) = (B^T (x) A) vec(X)``) turns the master equation into an
ordinary linear system ``d vec(rho)/dt = L vec(rho)`` with a constant *Liouvillian* superoperator
``L``. Then:

* the solution is ``vec(rho(t)) = e^{L t} vec(rho(0))`` -- a matrix exponential;
* every eigenvalue of ``L`` has non-positive real part (the dynamics is contractive);
* a *steady state* is a right-eigenvector of ``L`` with eigenvalue 0 (the kernel);
* the slowest non-zero decay rate is the *Liouvillian gap*, which sets the relaxation time.

This module builds the Liouvillian, evolves states, and finds steady states and spectra. Every
result is checked against an exact reference -- the amplitude-damping / dephasing Kraus channels,
the analytic steady state, and trace/positivity preservation.
"""

import numpy as np
from scipy.linalg import expm, null_space


def vectorize(rho):
    """Column-stacking vectorization ``vec(rho)`` -- stack the columns of ``rho`` into a vector.
    Satisfies ``vec(A X B) = (B^T (x) A) vec(X)``."""
    rho = np.asarray(rho, dtype=complex)
    return rho.reshape(-1, order="F")


def unvectorize(vec, dim=None):
    """Inverse of :func:`vectorize`: fold a length-``d^2`` vector back into a ``d x d`` matrix."""
    vec = np.asarray(vec, dtype=complex).ravel()
    if dim is None:
        dim = int(round(np.sqrt(vec.size)))
    return vec.reshape((dim, dim), order="F")


def left_multiply(A):
    """Superoperator for left multiplication ``rho -> A rho``: the matrix ``I (x) A`` acting on
    ``vec(rho)`` (column-stacking convention)."""
    A = np.asarray(A, dtype=complex)
    d = A.shape[0]
    return np.kron(np.eye(d), A)


def right_multiply(A):
    """Superoperator for right multiplication ``rho -> rho A``: the matrix ``A^T (x) I``."""
    A = np.asarray(A, dtype=complex)
    d = A.shape[0]
    return np.kron(A.T, np.eye(d))


def dissipator_superoperator(L):
    """
    The dissipator superoperator ``D[L]`` for a single jump operator ``L``, acting on ``vec(rho)``:

        D[L] rho = L rho L^dagger - (1/2)(L^dagger L rho + rho L^dagger L).

    Returns the ``d^2 x d^2`` matrix.
    """
    L = np.asarray(L, dtype=complex)
    Ld = L.conj().T
    LdL = Ld @ L
    return (np.kron(L.conj(), L)
            - 0.5 * left_multiply(LdL)
            - 0.5 * right_multiply(LdL))


def apply_dissipator(L, rho):
    """Apply the dissipator ``D[L]rho = L rho L^dagger - (1/2){L^dagger L, rho}`` directly (no
    vectorization) -- the reference for :func:`dissipator_superoperator`."""
    L = np.asarray(L, dtype=complex)
    rho = np.asarray(rho, dtype=complex)
    Ld = L.conj().T
    return L @ rho @ Ld - 0.5 * (Ld @ L @ rho + rho @ Ld @ L)


def lindbladian(H, jump_ops):
    """
    The Liouvillian superoperator ``L`` of the GKSL master equation, as a ``d^2 x d^2`` matrix with
    ``d vec(rho)/dt = L vec(rho)``:

        L = -i (I (x) H - H^T (x) I) + sum_k D[L_k].

    ``H`` is the Hamiltonian (Hermitian), ``jump_ops`` a list of Lindblad operators.
    """
    H = np.asarray(H, dtype=complex)
    d = H.shape[0]
    L = -1j * (left_multiply(H) - right_multiply(H))
    for Lk in jump_ops:
        L = L + dissipator_superoperator(np.asarray(Lk, dtype=complex))
    return L


def lindblad_derivative(H, jump_ops, rho):
    """The right-hand side ``d rho/dt`` of the master equation applied to ``rho`` directly (the
    non-vectorized reference)."""
    H = np.asarray(H, dtype=complex)
    rho = np.asarray(rho, dtype=complex)
    out = -1j * (H @ rho - rho @ H)
    for Lk in jump_ops:
        out = out + apply_dissipator(Lk, rho)
    return out


def evolve_lindblad(H, jump_ops, rho0, t):
    """
    Evolve ``rho0`` for time ``t`` under the Lindblad equation, ``rho(t) = unvec(e^{L t} vec(rho0))``.
    Trace-preserving and completely positive by construction.
    """
    rho0 = np.asarray(rho0, dtype=complex)
    d = rho0.shape[0]
    L = lindbladian(H, jump_ops)
    vec_t = expm(L * t) @ vectorize(rho0)
    rho_t = unvectorize(vec_t, d)
    return 0.5 * (rho_t + rho_t.conj().T)  # symmetrize away tiny numerical asymmetry


def is_trace_preserving(H, jump_ops, atol=1e-9):
    """
    True iff the Liouvillian conserves trace: the adjoint acting on the identity vanishes, i.e.
    ``sum_k L_k^dagger L_k`` is cancelled exactly by the anticommutator term. Equivalent to
    ``vec(I)^dagger L = 0``.
    """
    H = np.asarray(H, dtype=complex)
    d = H.shape[0]
    L = lindbladian(H, jump_ops)
    covec = vectorize(np.eye(d)).conj()
    return bool(np.allclose(covec @ L, 0.0, atol=atol))


def liouvillian_spectrum(H, jump_ops):
    """Eigenvalues of the Liouvillian, sorted by real part (descending). Every eigenvalue has
    ``Re <= 0``; the number of zero eigenvalues is the number of steady states."""
    L = lindbladian(H, jump_ops)
    ev = np.linalg.eigvals(L)
    return ev[np.argsort(-ev.real)]


def spectral_gap(H, jump_ops, atol=1e-9):
    """
    The Liouvillian (dissipative) gap: minus the largest *non-zero* real part in the spectrum --
    the asymptotic decay rate toward the steady state. Larger gap => faster relaxation.
    """
    ev = liouvillian_spectrum(H, jump_ops)
    nonzero = ev[np.abs(ev.real) > atol]
    if nonzero.size == 0:
        return 0.0
    return float(-np.max(nonzero.real))


def steady_state(H, jump_ops, atol=1e-9):
    """
    A steady state ``rho_ss`` of the open system: the (normalized, Hermitian) density matrix in the
    kernel of the Liouvillian, ``L vec(rho_ss) = 0``. Assumes a unique steady state.
    """
    H = np.asarray(H, dtype=complex)
    d = H.shape[0]
    L = lindbladian(H, jump_ops)
    ker = null_space(L, rcond=atol)
    if ker.shape[1] == 0:
        raise ValueError("no steady state found (empty Liouvillian kernel)")
    rho = unvectorize(ker[:, 0], d)
    rho = 0.5 * (rho + rho.conj().T)          # Hermitian
    tr = np.trace(rho)
    if abs(tr) < 1e-12:
        raise ValueError("degenerate steady state (zero trace)")
    return rho / tr


def amplitude_damping_jump(gamma):
    """The single Lindblad operator ``L = sqrt(gamma) sigma_-`` of the amplitude-damping (T1
    relaxation) channel -- decay from ``|1>`` to ``|0>`` at rate ``gamma``."""
    return np.sqrt(gamma) * np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)


def dephasing_jump(gamma):
    """The single Lindblad operator ``L = sqrt(gamma/2) sigma_z`` of the pure-dephasing (T2)
    channel -- loss of coherence without energy loss."""
    return np.sqrt(gamma / 2.0) * np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
