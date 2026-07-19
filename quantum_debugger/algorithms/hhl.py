"""
HHL Algorithm -- Quantum Linear Systems

Solves ``A x = b`` for a Hermitian ``A`` (Harrow-Hassidim-Lloyd 2009). The
algorithm loads the eigenvalues of ``A`` into a clock register with Quantum Phase
Estimation, rotates an ancilla by an angle proportional to ``1 / lambda``,
uncomputes the clock with inverse QPE, and post-selects the ancilla on ``|1>`` --
leaving the solution register in the state ``|x> proportional to A^{-1} |b>``.

This is a didactic, exact simulation for small, well-conditioned systems whose
eigenvalues are exactly representable in the clock register (so QPE is exact).

Register order (most to least significant qubit): ancilla, clock, b.
"""

import numpy as np
from scipy.linalg import expm

from .qft import qft_matrix


def _ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def hhl(A, b, n_clock: int = 4, C: float = None) -> dict:
    """
    Solve A x = b with the HHL algorithm (exact-simulation demo).

    Args:
        A: Hermitian matrix (2**n_b x 2**n_b)
        b: right-hand side vector (length 2**n_b)
        n_clock: number of clock qubits for eigenvalue estimation
        C: rotation constant (default: below the smallest |eigenvalue|)

    Returns:
        dict with 'solution' (normalized |x>), 'classical' (normalized A^{-1} b),
        'fidelity' between them, and 'success_probability' of the ancilla.
    """
    A = np.asarray(A, dtype=complex)
    b = np.asarray(b, dtype=complex)
    b = b / np.linalg.norm(b)
    dim_b = A.shape[0]
    n_b = int(round(np.log2(dim_b)))
    T = 2**n_clock

    eigvals = np.linalg.eigvalsh(A)
    if C is None:
        C = 0.5 * np.min(np.abs(eigvals[np.abs(eigvals) > 1e-9]))

    # Evolution time so that eigenvalue lambda maps to clock integer lambda.
    t0 = 2 * np.pi / T
    U = expm(1j * A * t0)  # e^{i A t0}; U^k has eigenphase 2*pi*k*lambda/T

    dim = 2 * T * dim_b  # ancilla (2) x clock (T) x b (dim_b)

    # --- Initial state |0>_anc |0>_clock |b> ---
    state = np.zeros(dim, dtype=complex)
    for j in range(dim_b):
        state[j] = b[j]  # ancilla=0, clock=0

    def kron3(anc, clock, bmat):
        return np.kron(anc, np.kron(clock, bmat))

    I_b = np.eye(dim_b, dtype=complex)
    I_anc = np.eye(2, dtype=complex)
    H1 = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

    # --- Hadamard on the clock register ---
    Hc = np.array([[1.0]], dtype=complex)
    for _ in range(n_clock):
        Hc = np.kron(Hc, H1)
    state = kron3(I_anc, Hc, I_b) @ state

    # --- QPE phase kickback: for clock value k, apply U^k to b ---
    phase_clock = np.zeros((T * dim_b, T * dim_b), dtype=complex)
    Uk = np.eye(dim_b, dtype=complex)
    for k in range(T):
        phase_clock[k * dim_b : (k + 1) * dim_b, k * dim_b : (k + 1) * dim_b] = Uk
        Uk = Uk @ U
    state = np.kron(I_anc, phase_clock) @ state

    # --- Inverse QFT on the clock register ---
    iqft = qft_matrix(n_clock).conj().T
    state = kron3(I_anc, iqft, I_b) @ state

    # --- Controlled ancilla rotation: RY(2 arcsin(C/lambda(k))) for clock value k ---
    rot = np.eye(dim, dtype=complex)
    for k in range(T):
        lam = k  # eigenvalue encoded by clock integer k (t0 chosen so lambda=k)
        if lam == 0:
            continue
        ratio = np.clip(C / lam, -1.0, 1.0)
        Rk = _ry(2 * np.arcsin(ratio))
        for bj in range(dim_b):
            # basis indices for (ancilla in {0,1}, clock=k, b=bj)
            i0 = 0 * (T * dim_b) + k * dim_b + bj
            i1 = 1 * (T * dim_b) + k * dim_b + bj
            rot[i0, i0] = Rk[0, 0]
            rot[i0, i1] = Rk[0, 1]
            rot[i1, i0] = Rk[1, 0]
            rot[i1, i1] = Rk[1, 1]
    state = rot @ state

    # --- Inverse QPE (uncompute the clock) ---
    state = kron3(I_anc, qft_matrix(n_clock), I_b) @ state
    phase_clock_inv = phase_clock.conj().T
    state = np.kron(I_anc, phase_clock_inv) @ state
    state = kron3(I_anc, Hc, I_b) @ state

    # --- Post-select ancilla = |1> and read the b-register ---
    solution = np.zeros(dim_b, dtype=complex)
    for bj in range(dim_b):
        solution[bj] = state[1 * (T * dim_b) + 0 * dim_b + bj]  # ancilla=1, clock=0
    success = float(np.sum(np.abs(solution) ** 2))
    if success > 1e-12:
        solution = solution / np.linalg.norm(solution)

    classical = np.linalg.solve(A, b)
    classical = classical / np.linalg.norm(classical)
    fidelity = float(np.abs(np.vdot(classical, solution)) ** 2)

    return {
        "solution": solution,
        "classical": classical,
        "fidelity": fidelity,
        "success_probability": success,
    }
