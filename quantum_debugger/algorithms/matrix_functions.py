"""
Matrix functions via Chebyshev / QSVT

Once a Hermitian ``A`` (``||A|| <= 1``) is block-encoded, qubitization gives its
Chebyshev polynomials ``T_k(A)`` (see :mod:`block_encoding`). A general function
``f(A)`` then follows from the classical Chebyshev expansion

    f(A) ~= sum_{k=0}^{d} c_k T_k(A),

where the ``c_k`` are the Chebyshev coefficients of ``f`` on ``[-1, 1]``. Each
``T_k(A)`` is realized by ``k`` steps of the qubitization walk, and their weighted sum
is a linear combination of unitaries -- so this is exactly the QSVT/qubitization route
to Hamiltonian simulation (``f(x) = e^{-i t x}``), matrix inversion (``f(x) = 1/x``),
and spectral filters. The Chebyshev series converges geometrically for smooth ``f``,
which this module verifies against the exact matrix function.
"""

import numpy as np
from numpy.polynomial import chebyshev as _cheb

from .block_encoding import chebyshev_of_matrix


def chebyshev_coefficients(func, degree: int) -> np.ndarray:
    """
    Chebyshev-series coefficients ``c_0, ..., c_degree`` approximating ``func`` on
    ``[-1, 1]`` (fit at Chebyshev nodes). ``func`` is applied to a numpy array.
    """
    nodes = np.cos(np.pi * (np.arange(degree + 1) + 0.5) / (degree + 1))
    return _cheb.chebfit(nodes, func(nodes), degree)


def matrix_function_chebyshev(matrix, func, degree: int) -> np.ndarray:
    """
    Approximate ``func(A)`` for a Hermitian ``matrix`` ``A`` (``||A|| <= 1``) by the
    degree-``degree`` Chebyshev series ``sum_k c_k T_k(A)``, with each ``T_k(A)`` built
    from the qubitization walk. Converges to the exact matrix function as ``degree``
    grows (geometrically for smooth ``func``).
    """
    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    coeffs = chebyshev_coefficients(func, degree)
    result = np.zeros((d, d), dtype=complex)
    for k, ck in enumerate(coeffs):
        Tk = np.eye(d, dtype=complex) if k == 0 else chebyshev_of_matrix(A, k)
        result += ck * Tk
    return result


def matrix_inverse_qsvt(matrix, degree: int = 30, samples: int = 400) -> np.ndarray:
    """
    Approximate ``A^{-1}`` for a Hermitian positive-definite ``matrix`` (spectrum in
    ``(0, 1]``) by fitting ``1/x`` with a Chebyshev series over the spectral support and
    building each ``T_k(A)`` from the qubitization walk -- the QSVT route to matrix
    inversion (the heart of the quantum linear-systems algorithm).

    The fit of the singular ``1/x`` is ill-conditioned at high ``degree``; ``degree``
    should scale with the condition number. Returns the approximate inverse.
    """
    import warnings
    from numpy.polynomial import chebyshev as _cheb

    A = np.asarray(matrix, dtype=complex)
    d = A.shape[0]
    w = np.linalg.eigvalsh(A).real
    lo, hi = w.min(), w.max()
    xs = np.linspace(lo, hi, samples)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # 1/x fit is expectedly ill-conditioned
        coeffs = _cheb.chebfit(xs, 1.0 / xs, degree)

    result = np.zeros((d, d), dtype=complex)
    for k, ck in enumerate(coeffs):
        Tk = np.eye(d, dtype=complex) if k == 0 else chebyshev_of_matrix(A, k)
        result += ck * Tk
    return result


def solve_linear_system_qsvt(matrix, b, degree: int = 30) -> dict:
    """
    Solve ``A x = b`` for a Hermitian positive-definite ``matrix`` via the QSVT matrix
    inverse.

    Returns dict with ``solution`` (the QSVT ``A^{-1} b``), ``exact`` (``numpy.linalg.solve``),
    ``error`` (2-norm), and ``fidelity`` (normalized overlap of the two solutions).
    """
    A = np.asarray(matrix, dtype=complex)
    b = np.asarray(b, dtype=complex)
    x = matrix_inverse_qsvt(A, degree) @ b
    exact = np.linalg.solve(A, b)
    fidelity = float(
        abs(np.vdot(exact, x)) ** 2
        / (np.linalg.norm(exact) ** 2 * np.linalg.norm(x) ** 2)
    )
    return {
        "solution": x,
        "exact": exact,
        "error": float(np.linalg.norm(x - exact)),
        "fidelity": fidelity,
    }


def hamiltonian_simulation_qsvt(hamiltonian, time: float, degree: int = 20) -> dict:
    """
    Approximate the time-evolution operator ``e^{-i H t}`` of a Hermitian
    ``hamiltonian`` (``||H|| <= 1``) via the Chebyshev/QSVT expansion of
    ``f(x) = e^{-i x t}``.

    Returns dict with ``unitary`` (the approximation), ``exact`` (``expm(-i H t)`` via
    diagonalization), ``error`` (spectral-norm difference), and ``unitarity_error``
    (how far the approximation is from unitary).
    """
    H = np.asarray(hamiltonian, dtype=complex)
    approx = matrix_function_chebyshev(H, lambda x: np.exp(-1j * time * x), degree)

    w, v = np.linalg.eigh(H)
    exact = v @ np.diag(np.exp(-1j * time * w)) @ v.conj().T
    return {
        "unitary": approx,
        "exact": exact,
        "error": float(np.linalg.norm(approx - exact, 2)),
        "unitarity_error": float(
            np.linalg.norm(approx.conj().T @ approx - np.eye(H.shape[0]), 2)
        ),
    }
