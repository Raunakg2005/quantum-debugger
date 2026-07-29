"""
QSVT applications -- matrix functions of a block-encoded Hermitian operator.

Once ``A`` (Hermitian, ``||A|| <= 1``) is block-encoded, qubitization gives its
Chebyshev polynomials ``T_k(A)`` and QSVT applies any smooth scalar function
*eigenvalue-by-eigenvalue*: ``f(A) = sum_i f(lambda_i) |v_i><v_i|``. This module
packages the standard applications built on that primitive -- the matrix sign
function, spectral projectors, roots, real exponential and logarithm, Gibbs
(thermal) states, and ground-state projection -- each realized through the
Chebyshev route and verified against the exact matrix function.

Two ingredients make the applications converge geometrically:

* **Interval rescaling.** For roots and the logarithm the spectrum lives on a
  positive sub-interval ``[a, b] subset (0, 1]``. Fitting there (not on all of
  ``[-1, 1]``, where ``sqrt``/``log`` are undefined) keeps the Chebyshev series on
  the analytic region, so it converges fast. The matrix is rescaled to
  ``y = (2A - (a+b)I)/(b-a)`` (spectrum in ``[-1, 1]``) and the Chebyshev walk is
  applied to ``y``.
* **erf smoothing of the sign.** The discontinuous ``sign(x)`` is replaced by
  ``erf(kappa x)``, whose sharpness ``kappa`` is set by the spectral gap; the
  smooth surrogate has a geometrically convergent Chebyshev series and equals the
  sign to ``~1e-5`` on eigenvalues a gap away from the jump -- exactly the QSVT
  construction for the sign/projector primitives.
"""

import numpy as np
from numpy.polynomial import chebyshev as _cheb
from scipy.special import erf

from .block_encoding import chebyshev_of_matrix


def _spectral_domain(A, margin: float = 1e-6):
    """Enclosing interval ``[lambda_min, lambda_max]`` of a Hermitian ``A``."""
    w = np.linalg.eigvalsh(np.asarray(A, dtype=complex))
    lo, hi = float(w[0]), float(w[-1])
    if hi - lo < margin:
        lo, hi = lo - margin, hi + margin
    return lo, hi


def matrix_function_on_interval(matrix, func, degree: int, domain=None) -> np.ndarray:
    """
    Approximate ``func(A)`` for a Hermitian ``A`` whose spectrum lies in
    ``domain = (a, b)`` by a Chebyshev series fitted *on that interval* and evaluated
    through the qubitization walk of the rescaled matrix
    ``y = (2A - (a+b)I)/(b-a)``. When ``domain`` is ``None`` it is taken as the
    matrix's own eigenvalue range. This is the interval-aware companion to the
    ``[-1, 1]`` fit used elsewhere -- essential when ``func`` (``sqrt``, ``log``,
    ``1/sqrt``) is only analytic on a positive sub-interval.
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    a, b = domain if domain is not None else _spectral_domain(A)
    y = (2 * A - (a + b) * np.eye(d)) / (b - a)
    nodes = np.cos(np.pi * (np.arange(degree + 1) + 0.5) / (degree + 1))
    xs = ((b - a) * nodes + (a + b)) / 2  # map fit nodes back to [a, b]
    coeffs = _cheb.chebfit(nodes, func(xs), degree)
    result = np.zeros((d, d), dtype=complex)
    for k, ck in enumerate(coeffs):
        Tk = np.eye(d, dtype=complex) if k == 0 else chebyshev_of_matrix(y, k)
        result += ck * Tk
    return result


def _smooth_sign(kappa):
    return lambda x: erf(kappa * x)


def matrix_sign_qsvt(matrix, gap: float = 0.2, degree: int = 61) -> np.ndarray:
    """
    Matrix sign function ``sign(A)`` via QSVT -- ``+1`` on the positive-eigenvalue
    subspace, ``-1`` on the negative one. The discontinuity at 0 is smoothed by
    ``erf(kappa x)`` with ``kappa = 3/gap`` (so eigenvalues at least ``gap`` from 0 map
    to ``+/-1`` within ``~1e-5``). Verified against the exact sign on gapped spectra.
    """
    kappa = 3.0 / gap
    from .matrix_functions import matrix_function_chebyshev
    return matrix_function_chebyshev(matrix, _smooth_sign(kappa), degree)


def spectral_projector_qsvt(matrix, threshold: float = 0.0, gap: float = 0.2,
                            degree: int = 61, above: bool = True) -> np.ndarray:
    """
    Projector onto the eigenspace with ``lambda > threshold`` (or ``< threshold`` when
    ``above=False``), built as ``(I +/- sign(A - threshold))/2`` through the erf-smoothed
    QSVT sign. Requires a spectral ``gap`` around ``threshold``; verified idempotent and
    equal to the exact spectral projector. This is the eigenvalue-thresholding primitive
    behind ground-state filtering.
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    kappa = 3.0 / gap

    def step(x):
        s = erf(kappa * (x - threshold))
        return (1 + s) / 2 if above else (1 - s) / 2

    from .matrix_functions import matrix_function_chebyshev
    return matrix_function_chebyshev(A, step, degree)


def matrix_sqrt_qsvt(matrix, degree: int = 40, domain=None) -> np.ndarray:
    """
    Principal square root ``sqrt(A)`` of a positive-definite ``A`` (spectrum in
    ``(0, 1]``) via an interval-rescaled QSVT series. Verified by
    ``sqrt(A) @ sqrt(A) = A`` and against ``scipy.linalg.sqrtm``.
    """
    return matrix_function_on_interval(matrix, np.sqrt, degree, domain)


def matrix_inverse_sqrt_qsvt(matrix, degree: int = 40, domain=None) -> np.ndarray:
    """
    Inverse square root ``A^{-1/2}`` of a positive-definite ``A`` (spectrum in
    ``[delta, 1]``) via interval-rescaled QSVT -- the operator that whitens ``A``
    (``A^{-1/2} A A^{-1/2} = I``). The degree grows as ``delta`` shrinks, as the theory
    predicts.
    """
    return matrix_function_on_interval(matrix, lambda x: 1.0 / np.sqrt(x), degree, domain)


def matrix_power_qsvt(matrix, power: float, degree: int = 40, domain=None) -> np.ndarray:
    """
    General matrix power ``A^power`` of a positive-definite ``A`` (spectrum in
    ``[delta, 1]``) via interval-rescaled QSVT -- integer, fractional, or negative
    exponents alike (``power=0.5`` recovers :func:`matrix_sqrt_qsvt`, ``power=-1`` the
    inverse). Verified against the exact ``sum_i lambda_i^power |v_i><v_i|``.
    """
    return matrix_function_on_interval(matrix, lambda x: np.power(x, power), degree, domain)


def pseudo_inverse_qsvt(matrix, epsilon: float = 1e-3, degree: int = 60) -> np.ndarray:
    """
    Moore-Penrose pseudo-inverse of a (possibly singular) Hermitian ``A`` via the
    Tikhonov-regularized QSVT filter ``h(x) = x / (x^2 + epsilon)`` -- ``~1/lambda`` on
    eigenvalues well above ``sqrt(epsilon)`` and ``~0`` on the kernel, so the null space
    is annihilated instead of blowing up. ``h`` is analytic on ``[-1, 1]`` so the
    Chebyshev series converges geometrically. Verified against ``numpy.linalg.pinv`` for
    rank-deficient matrices with a spectral gap.
    """
    from .matrix_functions import matrix_function_chebyshev
    return matrix_function_chebyshev(matrix, lambda x: x / (x**2 + epsilon), degree)


def bandpass_filter_qsvt(matrix, center: float, width: float, degree: int = 40) -> np.ndarray:
    """
    Gaussian spectral bandpass filter ``exp(-((A - center)/width)^2)`` via QSVT -- a
    smooth window that keeps the eigenspaces within ``~width`` of ``center`` and
    suppresses the rest, the building block of eigenstate filtering and windowed phase
    estimation. Verified against the exact ``sum_i exp(-((lambda_i-center)/width)^2)
    |v_i><v_i|``.
    """
    from .matrix_functions import matrix_function_chebyshev
    return matrix_function_chebyshev(
        matrix, lambda x: np.exp(-((x - center) / width) ** 2), degree)


def matrix_exp_qsvt(matrix, degree: int = 30) -> np.ndarray:
    """
    Real matrix exponential ``exp(A)`` (Hermitian ``A``, spectrum in ``[-1, 1]``) via
    the QSVT/Chebyshev series -- the imaginary-time sibling of ``e^{-iHt}``. Verified
    against ``scipy.linalg.expm``.
    """
    from .matrix_functions import matrix_function_chebyshev
    return matrix_function_chebyshev(matrix, np.exp, degree)


def matrix_log_qsvt(matrix, degree: int = 40, domain=None) -> np.ndarray:
    """
    Matrix logarithm ``log(A)`` of a positive-definite ``A`` (spectrum in
    ``[delta, 1]``) via interval-rescaled QSVT. Verified against ``scipy.linalg.logm``.
    """
    return matrix_function_on_interval(matrix, np.log, degree, domain)


def gibbs_state_qsvt(hamiltonian, beta: float, degree: int = 30) -> np.ndarray:
    """
    Thermal (Gibbs) density matrix ``rho = e^{-beta H} / Z`` for a Hermitian ``H``
    (spectrum in ``[-1, 1]``), building ``e^{-beta H}`` through the QSVT Chebyshev
    series and normalizing by ``Z = Tr e^{-beta H}``. Verified against the exact Gibbs
    state; reduces to the maximally mixed state at ``beta = 0`` and concentrates on the
    ground state as ``beta -> infinity``.
    """
    from .matrix_functions import matrix_function_chebyshev
    H = np.asarray(hamiltonian, dtype=complex)
    expH = matrix_function_chebyshev(H, lambda x: np.exp(-beta * x), degree)
    rho = (expH + expH.conj().T) / 2
    return rho / np.real(np.trace(rho))


def ground_state_projector_qsvt(hamiltonian, cutoff: float, gap: float = 0.2,
                                degree: int = 61) -> np.ndarray:
    """
    Projector onto the low-energy subspace ``{lambda < cutoff}`` of a Hermitian ``H``
    via erf-smoothed QSVT spectral filtering -- the ground-state-preparation primitive.
    With ``cutoff`` in the gap above the ground energy this is the ground-state
    projector; applying it to (almost) any state and renormalizing yields the ground
    state. Verified against the exact projector.
    """
    return spectral_projector_qsvt(hamiltonian, threshold=cutoff, gap=gap,
                                   degree=degree, above=False)
