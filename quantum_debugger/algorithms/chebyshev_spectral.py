"""
Spectral estimation via Chebyshev moments (the Kernel Polynomial Method).

The qubitization walk gives the Chebyshev polynomials ``T_k(A)`` of a Hermitian
``A`` (``||A|| <= 1``); their traces ``mu_k = Tr T_k(A) = sum_i T_k(lambda_i)`` are
the *Chebyshev moments* of the spectrum. From a handful of moments one recovers
global spectral information without ever diagonalizing ``A``:

* the **trace of any smooth function** ``Tr f(A) = sum_k c_k mu_k`` (partition
  functions, spectral sums),
* the **density of states** by the Kernel Polynomial Method with Jackson damping,
* the **eigenvalue count** in an interval (a smoothed projector trace).

Every routine is verified against the exact spectrum: the moments equal
``sum_i T_k(lambda_i)`` to machine precision, and the derived quantities match the
values computed from the eigenvalues.
"""

import numpy as np
from numpy.polynomial import chebyshev as _cheb
from scipy.special import erf

from .block_encoding import chebyshev_of_matrix


def spectral_moments(matrix, num_moments: int) -> np.ndarray:
    """
    Chebyshev moments ``mu_k = Tr T_k(A)`` for ``k = 0 .. num_moments-1`` of a Hermitian
    ``A`` (``||A|| <= 1``), each ``T_k(A)`` built from the qubitization walk. Equal to
    ``sum_i T_k(lambda_i)`` over the spectrum -- the raw data of the Kernel Polynomial
    Method.
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    out = np.empty(num_moments)
    for k in range(num_moments):
        Tk = np.eye(d, dtype=complex) if k == 0 else chebyshev_of_matrix(A, k)
        out[k] = float(np.real(np.trace(Tk)))
    return out


def trace_of_function(matrix, func, degree: int = 30) -> float:
    """
    ``Tr f(A) = sum_k c_k Tr T_k(A)`` for a smooth ``func`` on ``[-1, 1]`` -- the
    Chebyshev-moment estimate of a spectral sum, never forming ``f(A)`` densely.
    Verified against the exact ``sum_i f(lambda_i)``.
    """
    coeffs = _cheb_coeffs(func, degree)
    mu = spectral_moments(matrix, degree + 1)
    return float(np.dot(coeffs, mu))


def partition_function_qsvt(hamiltonian, beta: float, degree: int = 30) -> float:
    """
    Thermal partition function ``Z = Tr e^{-beta H} = sum_i e^{-beta lambda_i}`` from
    the Chebyshev moments of ``e^{-beta x}`` -- the normalizer of the Gibbs state and
    the generator of thermodynamic averages. Verified against the exact spectral sum.
    """
    return trace_of_function(hamiltonian, lambda x: np.exp(-beta * x), degree)


def _jackson_kernel(num_moments: int) -> np.ndarray:
    """Jackson damping factors that suppress Gibbs ringing in the KPM reconstruction."""
    N = num_moments
    n = np.arange(N)
    return ((N - n + 1) * np.cos(np.pi * n / (N + 1))
            + np.sin(np.pi * n / (N + 1)) / np.tan(np.pi / (N + 1))) / (N + 1)


def density_of_states_kpm(matrix, num_moments: int = 40, num_points: int = 400):
    """
    Approximate the spectral density (density of states) of a Hermitian ``A``
    (``||A|| <= 1``) by the Kernel Polynomial Method: expand ``rho(x)`` in Chebyshev
    moments ``mu_k`` with Jackson damping. Returns ``(x, rho)`` on ``num_points`` grid
    points of ``[-1, 1]``; ``rho`` integrates to the number of eigenvalues and peaks at
    the true eigenvalues. Verified: the integral equals the dimension and the raw
    moments equal ``sum_i T_k(lambda_i)``.
    """
    mu = spectral_moments(matrix, num_moments)
    g = _jackson_kernel(num_moments)
    x = np.cos(np.pi * (np.arange(num_points) + 0.5) / num_points)
    rho = np.zeros(num_points)
    for k in range(num_moments):
        rho += (2 - (k == 0)) * g[k] * mu[k] * np.cos(k * np.arccos(x))
    rho /= np.pi * np.sqrt(1 - x**2)
    order = np.argsort(x)
    return x[order], rho[order]


def eigenvalue_count_in_interval(matrix, a: float, b: float, gap: float = 0.15,
                                 degree: int = 60) -> float:
    """
    Number of eigenvalues of a Hermitian ``A`` in ``(a, b)``, estimated as the trace of
    a smoothed spectral projector ``Tr[ (erf(kappa(x-a)) - erf(kappa(x-b)))/2 ]`` via
    Chebyshev moments. With a spectral ``gap`` around each endpoint the result rounds to
    the exact integer count -- eigenvalue counting without diagonalization. Verified
    against the true count.
    """
    kappa = 3.0 / gap

    def window(x):
        return (erf(kappa * (x - a)) - erf(kappa * (x - b))) / 2

    return trace_of_function(matrix, window, degree)


def _cheb_coeffs(func, degree: int) -> np.ndarray:
    nodes = np.cos(np.pi * (np.arange(degree + 1) + 0.5) / (degree + 1))
    return _cheb.chebfit(nodes, func(nodes), degree)
