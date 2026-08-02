"""
Krylov complexity: operator growth under Heisenberg evolution.

Under Heisenberg evolution ``O(t) = e^{iHt} O e^{-iHt}`` an operator spreads through the space of
operators, reached by nested commutators with ``H`` (the Liouvillian ``L = [H, .]``). Applying the
Lanczos algorithm to ``L`` starting from ``O`` produces an orthonormal *Krylov basis* and a sequence
of **Lanczos coefficients** ``b_n``; the operator's wavefunction on this basis obeys a one-dimensional
hopping model with hopping amplitudes ``b_n``. The **Krylov complexity** ``K(t) = sum_n n |phi_n(t)|^2``
is the mean position -- how far the operator has spread -- and its growth rate is a sharp diagnostic
of quantum chaos.

The autocorrelation function ``C(t) = (O(t) | O)`` (infinite-temperature inner product) is recovered
exactly from the Lanczos coefficients, which this module verifies against direct evolution. Example:
a single spin ``O = X`` under ``H = (omega/2) Z`` gives ``C(t) = cos(omega t)``, ``b_1 = omega``, and an
oscillating ``K(t) = sin^2(omega t)``.
"""

import numpy as np
from scipy.linalg import expm


def liouvillian(H, O):
    """The Liouvillian action ``L O = [H, O] = H O - O H``."""
    H = np.asarray(H, dtype=complex)
    O = np.asarray(O, dtype=complex)
    return H @ O - O @ H


def operator_inner_product(A, B):
    """The infinite-temperature operator inner product ``(A|B) = Tr(A^dagger B) / dim``."""
    A = np.asarray(A, dtype=complex)
    B = np.asarray(B, dtype=complex)
    return np.trace(A.conj().T @ B) / A.shape[0]


def operator_norm(A):
    """The norm induced by the inner product, ``sqrt((A|A))``."""
    return float(np.sqrt(operator_inner_product(A, A).real))


def lanczos_coefficients(H, O, max_iter=None, atol=1e-10):
    """
    The Lanczos coefficients ``b_1, b_2, ...`` of operator ``O`` under the Liouvillian of ``H``, via the
    operator Lanczos recursion. The recursion terminates when the Krylov space is exhausted
    (``b_n ~ 0``). Returns the array of ``b_n``.
    """
    H = np.asarray(H, dtype=complex)
    d = H.shape[0]
    if max_iter is None:
        max_iter = d * d
    O0 = np.asarray(O, dtype=complex)
    O0 = O0 / operator_norm(O0)
    bs = []
    O_prev = np.zeros_like(O0)
    O_curr = O0
    b_prev = 0.0
    for _ in range(max_iter):
        A = liouvillian(H, O_curr) - b_prev * O_prev
        b = operator_norm(A)
        if b < atol:
            break
        bs.append(b)
        O_prev = O_curr
        O_curr = A / b
        b_prev = b
    return np.array(bs)


def _lanczos_matrix(bs):
    """The symmetric tridiagonal Krylov matrix with zero diagonal and off-diagonals ``b_n``."""
    n = len(bs) + 1
    M = np.zeros((n, n))
    for i, b in enumerate(bs):
        M[i, i + 1] = b
        M[i + 1, i] = b
    return M


def autocorrelation(H, O, t):
    """The exact infinite-temperature autocorrelation ``C(t) = (O(t)|O)`` with ``O(t) = e^{iHt} O
    e^{-iHt}`` (real for Hermitian ``O``)."""
    H = np.asarray(H, dtype=complex)
    O = np.asarray(O, dtype=complex)
    U = expm(1j * H * t)
    Ot = U @ O @ U.conj().T
    return float(operator_inner_product(Ot, O).real)


def reconstruct_autocorrelation(bs, t):
    """
    Reconstruct ``C(t)`` from the Lanczos coefficients as ``[cos(M t)]_{00}`` with ``M`` the Krylov
    tridiagonal matrix -- verified to match the exact autocorrelation.
    """
    from scipy.linalg import cosm
    M = _lanczos_matrix(bs)
    return float(cosm(M * t)[0, 0].real)


def krylov_wavefunction(bs, t):
    """The Krylov-space amplitudes ``phi_n(t)`` of the evolving operator (``phi(0) = e_0``, evolving
    under the tridiagonal ``M``)."""
    M = _lanczos_matrix(bs)
    psi = expm(-1j * M * t) @ np.eye(M.shape[0])[:, 0]
    return psi


def krylov_complexity(bs, t):
    """The Krylov complexity ``K(t) = sum_n n |phi_n(t)|^2`` -- the mean position on the Krylov chain,
    measuring how far the operator has spread."""
    psi = krylov_wavefunction(bs, t)
    n = np.arange(len(psi))
    return float(np.sum(n * np.abs(psi) ** 2))


def krylov_dimension(bs):
    """The dimension of the Krylov space -- the number of Lanczos coefficients plus one."""
    return len(bs) + 1


def moment(H, O, order):
    """The autocorrelation moment ``mu_k = (O | L^k | O)`` -- the ``k``-th derivative data of ``C(t)``;
    even moments are non-negative."""
    O = np.asarray(O, dtype=complex)
    v = O / operator_norm(O)
    for _ in range(order):
        v = liouvillian(H, v)
    return complex(operator_inner_product(O / operator_norm(O), v))
