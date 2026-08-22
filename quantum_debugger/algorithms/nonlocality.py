"""
CHSH nonlocality of mixed states (Horodecki criterion)

For any two-qubit ``rho``, the maximum CHSH value over ALL measurement settings has
a closed form (R. Horodecki, P. Horodecki & M. Horodecki, Phys. Lett. A 200, 340,
1995): with the correlation matrix ``T_ij = Tr[rho sigma_i x sigma_j]``,

    S_max = 2 sqrt(u1 + u2),

where ``u1, u2`` are the two largest eigenvalues of ``T^T T``. The state violates a
Bell inequality (is *nonlocal*) iff ``S_max > 2``; Tsirelson's bound caps it at
``2 sqrt(2)``.

The punchline this module verifies: **entanglement and nonlocality are different
resources**. A Werner state is entangled for ``F > 1/2`` but violates CHSH only for
``F > (1 + 3/sqrt(2))/4 ~ 0.78`` -- in between lies a window of entangled states
whose every CHSH experiment admits a local hidden-variable model.
"""

import numpy as np

from ..density_matrix import DensityMatrix
from .distillation import werner_state

_SX = np.array([[0, 1], [1, 0]], dtype=complex)
_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SZ = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULIS = (_SX, _SY, _SZ)


def correlation_matrix(rho: np.ndarray) -> np.ndarray:
    """``T_ij = Tr[rho sigma_i^{(A)} sigma_j^{(B)}]`` (qubit 0 = A, little-endian)."""
    rho = np.asarray(rho, dtype=complex)
    T = np.zeros((3, 3))
    for i, si in enumerate(_PAULIS):
        for j, sj in enumerate(_PAULIS):
            T[i, j] = float(np.real(np.trace(rho @ np.kron(sj, si))))
    return T


def chsh_maximum(rho: np.ndarray) -> float:
    """
    The Horodecki closed form for the maximal CHSH value of a two-qubit state:
    ``2 sqrt(u1 + u2)`` with ``u1, u2`` the two largest eigenvalues of ``T^T T``.
    ``> 2`` iff the state is nonlocal; at most ``2 sqrt(2)`` (Tsirelson).
    """
    T = correlation_matrix(rho)
    u = np.sort(np.linalg.eigvalsh(T.T @ T))
    return float(2 * np.sqrt(max(0.0, u[-1] + u[-2])))


def chsh_maximum_optimized(rho: np.ndarray, restarts: int = 12, seed: int = 0) -> float:
    """
    The same maximum found the hard way: numerically optimizing the four Bloch
    measurement directions of the CHSH game (Nelder-Mead with random restarts).
    Agrees with :func:`chsh_maximum` -- the closed form is exact.
    """
    from scipy.optimize import minimize

    T = correlation_matrix(rho)

    def nvec(th, ph):
        return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])

    def neg_s(x):
        a, ap = nvec(*x[0:2]), nvec(*x[2:4])
        b, bp = nvec(*x[4:6]), nvec(*x[6:8])
        return -(a @ T @ b + a @ T @ bp + ap @ T @ b - ap @ T @ bp)

    rng = np.random.default_rng(seed)
    best = -np.inf
    for _ in range(restarts):
        x0 = rng.uniform(0, np.pi, 8)
        x0[1::2] *= 2
        res = minimize(
            neg_s,
            x0,
            method="Nelder-Mead",
            options={"xatol": 1e-10, "fatol": 1e-12, "maxiter": 2000},
        )
        best = max(best, -res.fun)
    return float(best)


def werner_nonlocality(F: float) -> dict:
    """
    Where a Werner state of fidelity ``F`` sits in the correlation hierarchy.

    Returns dict with ``negativity``, ``chsh`` (= ``2 sqrt(2) |4F - 1| / 3``,
    matching the closed form), ``entangled`` (``F > 1/2``), ``nonlocal``
    (``chsh > 2``, i.e. ``F > (1 + 3/sqrt(2))/4 ~ 0.7803``), and
    ``entangled_but_local`` -- True inside the window where the state is entangled
    yet every CHSH experiment on it has a local model.
    """
    rho = werner_state(F)
    dm = DensityMatrix(rho=rho)
    neg = dm.negativity([0])
    s = chsh_maximum(rho)
    entangled = neg > 1e-12
    nonlocal_ = s > 2 + 1e-12
    return {
        "negativity": neg,
        "chsh": s,
        "entangled": entangled,
        "nonlocal": nonlocal_,
        "entangled_but_local": entangled and not nonlocal_,
    }
