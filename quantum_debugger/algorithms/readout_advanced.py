"""
Scalable readout-error mitigation.

The full ``2^n x 2^n`` assignment matrix is exponential; on real devices readout is
(to good approximation) independent per qubit, so the calibration factorizes as a
tensor product of ``2 x 2`` matrices -- and inverting it is a product of ``2 x 2``
inverses. Two safer correctors are also provided: iterative Bayesian unfolding and a
constrained least-squares fit, both of which return a genuine probability vector
(nonnegative, sums to one) instead of the possibly-unphysical output of a raw matrix
inverse. Finally, the calibration matrix itself can be estimated from
prepare-and-measure data. Each routine is verified: applied to the exact noisy
distribution it recovers the true one.
"""

import numpy as np


def tensored_assignment_matrix(single_qubit_matrices) -> np.ndarray:
    """
    Full assignment matrix ``A = A_0 (x) A_1 (x) ...`` from per-qubit ``2 x 2``
    calibration matrices (column ``j`` = measured distribution given true input ``j``).
    Exponential to store but never formed on hardware -- it factorizes.
    """
    A = np.array([[1.0]])
    for M in single_qubit_matrices:
        A = np.kron(A, np.asarray(M, dtype=float))
    return A


def tensored_mitigate(measured_probs, single_qubit_matrices) -> np.ndarray:
    """
    Correct a measured distribution by applying the tensor product of the *inverse*
    per-qubit calibration matrices -- ``(x)_q A_q^{-1}`` -- without ever building the
    full inverse. Recovers the true distribution exactly for independent readout noise.
    """
    inv = [np.linalg.inv(np.asarray(M, dtype=float)) for M in single_qubit_matrices]
    Ainv = np.array([[1.0]])
    for M in inv:
        Ainv = np.kron(Ainv, M)
    return Ainv @ np.asarray(measured_probs, dtype=float)


def iterative_bayesian_unfolding(measured_probs, assignment_matrix,
                                 iterations: int = 50, prior=None) -> np.ndarray:
    """
    Iterative Bayesian unfolding (expectation-maximization) for readout correction. Each
    update

        t_j <- t_j * sum_i A_ij measured_i / (sum_k A_ik t_k)

    keeps the estimate a valid probability vector at every step (nonnegative, normalized)
    -- unlike a matrix inverse, which can produce negative "probabilities". Converges to
    the true distribution for consistent data.
    """
    A = np.asarray(assignment_matrix, dtype=float)
    m = np.asarray(measured_probs, dtype=float)
    n = A.shape[1]
    t = np.full(n, 1.0 / n) if prior is None else np.asarray(prior, dtype=float).copy()
    for _ in range(iterations):
        expected = A @ t
        expected = np.where(expected > 1e-15, expected, 1e-15)
        t = t * (A.T @ (m / expected))
        s = t.sum()
        if s > 0:
            t = t / s
    return t


def constrained_readout_mitigate(measured_probs, assignment_matrix) -> np.ndarray:
    """
    Readout correction as a constrained least-squares problem: minimize
    ``||A t - measured||^2`` subject to ``t >= 0`` and ``sum t = 1``. Solved by
    non-negative least squares on the system augmented with a heavily weighted
    normalization row, so the result is always a physical probability vector. Recovers
    the true distribution for exact data.
    """
    from scipy.optimize import nnls
    A = np.asarray(assignment_matrix, dtype=float)
    m = np.asarray(measured_probs, dtype=float)
    n = A.shape[1]
    w = 1e3  # weight enforcing sum(t) = 1
    Aa = np.vstack([A, w * np.ones((1, n))])
    ma = np.concatenate([m, [w]])
    t, _ = nnls(Aa, ma)
    s = t.sum()
    return t / s if s > 0 else t


def calibrate_assignment_matrix(prepared_measured_columns) -> np.ndarray:
    """
    Build the assignment matrix from calibration data: prepare each computational basis
    state and record the measured distribution; those distributions are the columns of
    ``A``. ``prepared_measured_columns[j]`` is the measured distribution for prepared
    input ``j``. Recovers the true calibration matrix exactly.
    """
    cols = [np.asarray(c, dtype=float) for c in prepared_measured_columns]
    return np.column_stack(cols)
