"""
Linear Combination of Unitaries (LCU)

Most operators of interest -- a molecular Hamiltonian, a data matrix -- come naturally
as a weighted sum of easy unitaries, ``H = sum_i alpha_i U_i`` with ``alpha_i > 0``.
LCU block-encodes such an ``H`` using two ingredients on an ancilla register:

  * **PREPARE**: ``|0> -> (1/sqrt(lambda)) sum_i sqrt(alpha_i) |i>``, ``lambda = sum alpha_i``;
  * **SELECT**: ``sum_i |i><i| (x) U_i`` (apply ``U_i`` controlled on ancilla ``i``).

Then ``PREPARE-dagger . SELECT . PREPARE`` has top-left block ``H / lambda`` -- a block
encoding of ``H`` with subnormalization ``lambda``. This is the standard way to feed a
Hamiltonian into qubitization / QSVT, and the engine behind LCU-based Hamiltonian
simulation and the Taylor-series and linear-systems algorithms.
"""

import numpy as np


def _prepare_unitary(amplitudes) -> np.ndarray:
    """A unitary whose first column is the (normalized) ``amplitudes`` vector."""
    a = len(amplitudes)
    v = np.asarray(amplitudes, dtype=complex)
    v = v / np.linalg.norm(v)
    basis = [v]
    for e in np.eye(a, dtype=complex):
        w = e - sum(np.vdot(b, e) * b for b in basis)
        if np.linalg.norm(w) > 1e-9:
            basis.append(w / np.linalg.norm(w))
        if len(basis) == a:
            break
    return np.array(basis).T


def lcu_block_encoding(coeffs, unitaries) -> dict:
    """
    Block-encode ``H = sum_i coeffs[i] * unitaries[i]`` (with ``coeffs[i] > 0``) via LCU.

    Returns dict with:
      * ``unitary``          -- the full ``PREPARE-dagger SELECT PREPARE`` unitary
      * ``subnormalization`` -- ``lambda = sum coeffs`` (the block encodes ``H/lambda``)
      * ``dim``              -- the system dimension (top-left block size)
    """
    coeffs = np.asarray(coeffs, dtype=float)
    if np.any(coeffs < 0):
        raise ValueError("LCU coefficients must be non-negative")
    m = len(coeffs)
    lam = float(coeffs.sum())
    dim = np.asarray(unitaries[0]).shape[0]

    a = 1
    while a < m:
        a *= 2
    amps = np.zeros(a, dtype=complex)
    for i in range(m):
        amps[i] = np.sqrt(coeffs[i] / lam)
    P = _prepare_unitary(amps)

    select = np.zeros((a * dim, a * dim), dtype=complex)
    for i in range(a):
        Ui = np.asarray(unitaries[i], dtype=complex) if i < m else np.eye(dim, dtype=complex)
        select[i * dim:(i + 1) * dim, i * dim:(i + 1) * dim] = Ui

    Pfull = np.kron(P, np.eye(dim, dtype=complex))
    full = Pfull.conj().T @ select @ Pfull
    return {"unitary": full, "subnormalization": lam, "dim": dim}


def lcu_matrix(coeffs, unitaries) -> np.ndarray:
    """The dense operator ``sum_i coeffs[i] * unitaries[i]`` (for verification)."""
    return sum(
        c * np.asarray(u, dtype=complex) for c, u in zip(coeffs, unitaries)
    )
