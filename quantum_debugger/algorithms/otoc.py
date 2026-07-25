"""
Out-of-time-order correlators (quantum information scrambling)

How fast does local information spread across a many-body system? The out-of-time-
order correlator measures the growth of the commutator between a time-evolved
operator ``W(t) = e^{iHt} W e^{-iHt}`` and a spatially-separated operator ``V``:

    C(t) = <[W(t), V]-dagger [W(t), V]>.

At infinite temperature (the trace average), for unitary ``W, V`` this equals

    C(t) = 2 (1 - Re F(t)),      F(t) = (1/d) Tr[ W(t)-dagger V-dagger W(t) V ],

where ``F(t)`` is the OTOC proper. Initially ``W`` and ``V`` commute (they act on
different qubits), so ``C(0) = 0``; as the dynamics scrambles ``W`` across the
lattice the commutator grows -- the "butterfly effect" of quantum chaos. This module
computes both, verifying the exact identity and the growth.
"""

import numpy as np
from scipy.linalg import expm

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def _embed(op, qubit, n):
    mats = [op if i == qubit else np.eye(2, dtype=complex) for i in range(n)]
    out = np.array([[1]], dtype=complex)
    for m in reversed(mats):
        out = np.kron(out, m)
    return out


def otoc(hamiltonian, w_op, v_op, times) -> dict:
    """
    Infinite-temperature OTOC of operators ``w_op`` and ``v_op`` under ``hamiltonian``,
    sampled at each ``t`` in ``times``.

    Returns dict with:
      * ``F``          -- the OTOC ``F(t) = (1/d) Tr[W(t)-dag V-dag W(t) V]`` (complex)
      * ``C``          -- the commutator-squared ``C(t) = <|[W(t), V]|^2>`` (real, >= 0)
      * ``identity_ok``-- whether ``C = 2(1 - Re F)`` holds (exact for unitary W, V)
    """
    H = np.asarray(hamiltonian, dtype=complex)
    W = np.asarray(w_op, dtype=complex)
    V = np.asarray(v_op, dtype=complex)
    d = H.shape[0]

    F_vals, C_vals = [], []
    for t in times:
        U = expm(-1j * H * t)
        Wt = U.conj().T @ W @ U
        comm = Wt @ V - V @ Wt
        C_vals.append(float(np.real(np.trace(comm.conj().T @ comm)) / d))
        F_vals.append(complex(np.trace(Wt.conj().T @ V.conj().T @ Wt @ V) / d))

    F = np.array(F_vals)
    C = np.array(C_vals)
    identity_ok = bool(np.allclose(C, 2 * (1 - np.real(F)), atol=1e-9))
    return {"F": F, "C": C, "identity_ok": identity_ok}


def scrambling_time(hamiltonian, n_qubits: int, t_max: float = 8.0, points: int = 100,
                    threshold: float = 1.0) -> dict:
    """
    Measure how a local ``X`` perturbation on qubit 0 scrambles to the far edge
    (qubit ``n-1``): compute the OTOC of ``X_0`` with ``X_{n-1}`` and find the first
    time the commutator ``C(t)`` exceeds ``threshold``.

    Returns dict with ``times``, ``C`` (the growth curve), ``scrambling_time`` (first
    crossing, or ``None``), and ``max_C``.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    W = _embed(_X, 0, n_qubits)
    V = _embed(_X, n_qubits - 1, n_qubits)
    times = np.linspace(0, t_max, points)
    C = otoc(H, W, V, times)["C"]

    crossing = np.where(C > threshold)[0]
    t_scr = float(times[crossing[0]]) if len(crossing) else None
    return {
        "times": times,
        "C": C,
        "scrambling_time": t_scr,
        "max_C": float(C.max()),
    }
