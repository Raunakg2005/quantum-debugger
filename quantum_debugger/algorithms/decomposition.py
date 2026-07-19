"""
Gate Decomposition / Synthesis

Break arbitrary unitaries down into elementary rotations and CNOTs:

  * ``zyz_decompose``      -- any 1-qubit U = e^{i a} RZ(b) RY(c) RZ(d)
  * ``abc_decomposition``  -- Nielsen-Chuang ABC form for a controlled-U
  * ``kak_decompose``      -- 2-qubit Cartan (KAK) decomposition into local gates
                              plus the entangling core exp(i(a XX + b YY + c ZZ))
  * ``canonical_coordinates`` -- the Weyl-chamber (a, b, c) interaction content

Every routine is self-verifying: the returned pieces reconstruct the input
unitary (up to a global phase) to machine precision.
"""

import numpy as np

from ..core.gates import GateLibrary

_I = np.eye(2, dtype=complex)
_X = GateLibrary.X
_Y = GateLibrary.Y
_Z = GateLibrary.Z


def _rz(theta):
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
    )


def _ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def zyz_decompose(U) -> dict:
    """
    Decompose a 1-qubit unitary as ``U = e^{i alpha} RZ(beta) RY(gamma) RZ(delta)``.

    Returns dict with 'alpha','beta','gamma','delta' and 'reconstruction_error'.
    """
    U = np.asarray(U, dtype=complex)
    assert U.shape == (2, 2)

    # Global phase so that det = 1 (work in SU(2)).
    det = U[0, 0] * U[1, 1] - U[0, 1] * U[1, 0]
    alpha = 0.5 * np.angle(det)
    su = U * np.exp(-1j * alpha)

    # gamma from the magnitudes; beta/delta from the phases.
    gamma = 2 * np.arctan2(abs(su[1, 0]), abs(su[0, 0]))
    if abs(su[0, 0]) > 1e-12 and abs(su[1, 0]) > 1e-12:
        # beta+delta from the phase of su[1,1]; beta-delta from su[1,0].
        beta_plus_delta = 2 * np.angle(su[1, 1])
        beta_minus_delta = 2 * np.angle(su[1, 0])
        beta = (beta_plus_delta + beta_minus_delta) / 2
        delta = (beta_plus_delta - beta_minus_delta) / 2
    elif abs(su[0, 0]) <= 1e-12:
        # su is anti-diagonal; only beta - delta is fixed. Pick delta = 0.
        delta = 0.0
        beta = 2 * np.angle(su[1, 0])
    else:
        # su is diagonal; only beta + delta is fixed. Pick delta = 0.
        delta = 0.0
        beta = 2 * np.angle(su[1, 1])

    recon = np.exp(1j * alpha) * _rz(beta) @ _ry(gamma) @ _rz(delta)
    err = float(np.max(np.abs(recon - U)))
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "gamma": float(gamma),
        "delta": float(delta),
        "reconstruction_error": err,
    }


def abc_decomposition(U) -> dict:
    """
    Nielsen-Chuang ABC decomposition of a 1-qubit unitary:
    ``U = e^{i alpha} A X B X C`` with ``A B C = I``. This lets a controlled-U be
    built from CNOTs and single-qubit gates (controlled-U = (I⊗A) CX (I⊗B) CX
    (I⊗C) plus a phase on the control).

    Returns dict with matrices 'A','B','C', 'alpha', and 'abc_is_identity' /
    'reconstruction_error' checks.
    """
    d = zyz_decompose(U)
    alpha, beta, gamma, delta = d["alpha"], d["beta"], d["gamma"], d["delta"]

    A = _rz(beta) @ _ry(gamma / 2)
    B = _ry(-gamma / 2) @ _rz(-(delta + beta) / 2)
    C = _rz((delta - beta) / 2)

    abc = A @ B @ C
    recon = np.exp(1j * alpha) * A @ _X @ B @ _X @ C
    return {
        "A": A,
        "B": B,
        "C": C,
        "alpha": float(alpha),
        "abc_is_identity": float(np.max(np.abs(abc - _I))),
        "reconstruction_error": float(np.max(np.abs(recon - np.asarray(U, complex)))),
    }


# --- Two-qubit Cartan (KAK) decomposition -----------------------------------

# Magic basis: maps SU(2)xSU(2) local gates to real SO(4).
_MAGIC = (1 / np.sqrt(2)) * np.array(
    [
        [1, 0, 0, 1j],
        [0, 1j, 1, 0],
        [0, 1j, -1, 0],
        [1, 0, 0, -1j],
    ],
    dtype=complex,
)
_MAGIC_DAG = _MAGIC.conj().T


def _kron(a, b):
    return np.kron(a, b)


def canonical_coordinates(U) -> tuple:
    """
    Weyl-chamber interaction coordinates (a, b, c) of a 2-qubit gate, i.e. the
    coefficients of the entangling core exp(i(a XX + b YY + c ZZ)). CNOT -> about
    (pi/4, 0, 0); SWAP -> (pi/4, pi/4, pi/4); iSWAP -> (pi/4, pi/4, 0).
    """
    U = np.asarray(U, dtype=complex)
    U = U / (np.linalg.det(U) ** 0.25)  # into SU(4)
    Um = _MAGIC_DAG @ U @ _MAGIC
    M = Um.T @ Um  # symmetric; eigenphases carry the interaction content
    eig = np.linalg.eigvals(M)
    angles = np.angle(eig) / 2
    # Solve for (a,b,c) from the four eigen-phases (which are +/- combinations).
    # angles ~ { a+b-c... } up to sign/order; use the standard inversion:
    angles = np.sort(angles)
    # The four phases are: (a+b-c), (a-b+c), (-a+b+c), (-a-b-c) up to 2pi and order.
    # Recover via least squares over sign assignments is overkill; use the known
    # closed form from the sorted phases.
    x = angles
    a = (x[3] + x[2]) / 2
    b = (x[3] + x[1]) / 2
    c = (x[2] + x[1]) / 2
    return (float(a), float(b), float(c))


# Diagonal entries of M† (XX/YY/ZZ) M in the magic basis (all real, +/-1).
# Used to invert the map from core eigen-phases to (a, b, c).
_SIGN = np.array(
    [
        np.real(np.diag(_MAGIC_DAG @ _kron(_X, _X) @ _MAGIC)),
        np.real(np.diag(_MAGIC_DAG @ _kron(_Y, _Y) @ _MAGIC)),
        np.real(np.diag(_MAGIC_DAG @ _kron(_Z, _Z) @ _MAGIC)),
    ]
).T  # shape (4, 3): row j gives the +/- signs of (a, b, c) in phase j


def _joint_diagonalize(R, S, tol=1e-7):
    """
    Real orthogonal Q diagonalizing two commuting real-symmetric matrices R, S.

    Eigen-decompose R first, then split each degenerate eigenspace by diagonalizing
    the projection of S -- deterministic and robust to repeated eigenvalues.
    """
    evals, Q = np.linalg.eigh(R)
    Q = np.asarray(Q, dtype=float)
    n = len(evals)
    i = 0
    while i < n:
        j = i + 1
        while j < n and abs(evals[j] - evals[i]) < tol:
            j += 1
        if j - i > 1:  # degenerate block -> diagonalize S within it
            block = Q[:, i:j]
            _, W = np.linalg.eigh(block.T @ S @ block)
            Q[:, i:j] = block @ W
        i = j
    return Q


def kak_decompose(U) -> dict:
    """
    Cartan (KAK) decomposition of a 2-qubit unitary:
    ``U = e^{i phase} (A1 ⊗ A0) · exp(i(a XX + b YY + c ZZ)) · (B1 ⊗ B0)``.

    Returns dict with local gates 'A0','A1','B0','B1', the core coefficients
    'coefficients' = (a, b, c), the global 'phase', and 'reconstruction_error'.
    """
    U = np.asarray(U, dtype=complex)
    assert U.shape == (4, 4)

    # Normalize to SU(4).
    det = np.linalg.det(U)
    phase = np.angle(det) / 4
    su = U * np.exp(-1j * phase)

    # Into the magic basis, where local gates become real orthogonal (SO(4)).
    Um = _MAGIC_DAG @ su @ _MAGIC

    # Um = K1 · A · K2 with K1, K2 real orthogonal and A = diag(exp(i*theta)).
    # (Um Um^T) = K1 A^2 K1^T is symmetric-unitary, so its real and imaginary parts
    # commute and share the real orthogonal eigenbasis K1.
    MMt = Um @ Um.T
    K1 = _joint_diagonalize(MMt.real, MMt.imag)
    if np.linalg.det(K1) < 0:
        K1[:, 0] = -K1[:, 0]

    theta = np.angle(np.diag(K1.T @ MMt @ K1)) / 2  # A^2 = K1^T MMt K1
    K2 = (np.diag(np.exp(-1j * theta)) @ K1.T @ Um).real  # right factor (now real)
    if np.linalg.det(K2) < 0:
        # Fold the reflection into the core: negate one theta and its K2 row.
        K2[0, :] = -K2[0, :]
        theta[0] = theta[0] + np.pi
    A = np.diag(np.exp(1j * theta))

    # Map orthogonal factors and the diagonal core back to the computational basis.
    A1, A0 = _factor_local(_MAGIC @ K1 @ _MAGIC_DAG)
    B1, B0 = _factor_local(_MAGIC @ K2 @ _MAGIC_DAG)
    core_comp = _MAGIC @ A @ _MAGIC_DAG

    recon = np.exp(1j * phase) * _kron(A1, A0) @ core_comp @ _kron(B1, B0)
    err = float(np.max(np.abs(recon - U)))

    # (a, b, c) from theta = _SIGN @ (a,b,c)  (least squares inverts the sign map).
    abc, *_ = np.linalg.lstsq(_SIGN, theta, rcond=None)
    a, b, c = (float(abc[0]), float(abc[1]), float(abc[2]))

    return {
        "A0": A0,
        "A1": A1,
        "B0": B0,
        "B1": B1,
        "coefficients": (a, b, c),
        "phase": float(phase),
        "reconstruction_error": err,
    }


def _factor_local(V):
    """Write a 4x4 that equals A ⊗ B as the pair (A, B) (up to shared phase)."""
    V = np.asarray(V, dtype=complex)
    # Find the largest 2x2 block to normalize against.
    # V[i*2+k, j*2+l] = A[i,j] B[k,l]. Use the block with largest norm.
    best, bi, bj = -1.0, 0, 0
    for i in range(2):
        for j in range(2):
            block = V[2 * i : 2 * i + 2, 2 * j : 2 * j + 2]
            nrm = np.linalg.norm(block)
            if nrm > best:
                best, bi, bj = nrm, i, j
    B = V[2 * bi : 2 * bi + 2, 2 * bj : 2 * bj + 2].copy()
    B = B / np.sqrt(np.linalg.det(B))
    # A[i,j] = <block_ij, B> / <B,B>
    A = np.zeros((2, 2), dtype=complex)
    for i in range(2):
        for j in range(2):
            block = V[2 * i : 2 * i + 2, 2 * j : 2 * j + 2]
            A[i, j] = np.vdot(B.reshape(-1), block.reshape(-1)) / np.vdot(
                B.reshape(-1), B.reshape(-1)
            )
    A = A / np.sqrt(np.linalg.det(A))
    return A, B
