"""
TEBD -- Time-Evolving Block Decimation (dynamics on a matrix product state)

Real-time evolution of a many-body state under a nearest-neighbour Hamiltonian, done
directly on a matrix product state. Trotterize ``e^{-i H t}`` into two-site gates
``e^{-i h_{j,j+1} dt}``, apply them to the MPS (even bonds, then odd bonds), and let
the built-in SVD truncation keep the bond dimension bounded. As long as the state
stays lightly entangled, this simulates the dynamics of far more qubits than the dense
state-vector engine can hold.

This module provides TEBD for the transverse-field Ising model; the same pattern works
for any nearest-neighbour Hamiltonian by supplying its two-site gates.
"""

import numpy as np
from scipy.linalg import expm

from ..mps import MPS

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def tfim_bond_gate(n: int, i: int, dt: float, j_coupling: float, field: float) -> np.ndarray:
    """
    Two-site Trotter gate ``exp(-i h_{i,i+1} dt)`` for the transverse-field Ising model
    ``H = -J sum Z Z - h sum X`` on a chain of ``n`` sites. The single-site field is
    split evenly between the bonds it belongs to (full weight at the two chain ends).
    """
    hx_i = field * (0.5 if i > 0 else 1.0)
    hx_j = field * (0.5 if i < n - 2 else 1.0)
    h_local = (
        -j_coupling * np.kron(_Z, _Z)
        - hx_i * np.kron(_I, _X)
        - hx_j * np.kron(_X, _I)
    )
    return expm(-1j * h_local * dt)


def tebd_tfim(n: int, time: float, steps: int = 100, j_coupling: float = 1.0,
              field: float = 1.0, max_bond: int = 16, initial: "MPS" = None) -> "MPS":
    """
    Evolve a TFIM chain of ``n`` sites for total ``time`` with ``steps`` Trotter steps,
    on an MPS truncated to ``max_bond``. Starts from ``|0...0>`` unless an ``initial``
    MPS is supplied. Returns the evolved MPS.
    """
    mps = initial if initial is not None else MPS.zero_state(n, max_bond=max_bond)
    mps.max_bond = max_bond
    dt = time / steps
    even = [tfim_bond_gate(n, i, dt, j_coupling, field) for i in range(0, n - 1, 2)]
    odd = [tfim_bond_gate(n, i, dt, j_coupling, field) for i in range(1, n - 1, 2)]
    for _ in range(steps):
        for idx, i in enumerate(range(0, n - 1, 2)):
            mps.apply_two(even[idx], i)
        for idx, i in enumerate(range(1, n - 1, 2)):
            mps.apply_two(odd[idx], i)
    return mps


def tebd_magnetization(n: int, time: float, steps: int = 100, j_coupling: float = 1.0,
                       field: float = 1.0, max_bond: int = 16) -> dict:
    """
    Quench a TFIM chain from the all-up state and read out the transverse magnetization.

    Returns dict with ``z_profile`` (``<Z_i>`` on each site), ``mean_z``, and
    ``max_bond`` (the bond dimension reached -- the cost of the entanglement generated).
    """
    mps = tebd_tfim(n, time, steps, j_coupling, field, max_bond)
    z_profile = [mps.expectation(_Z, q) for q in range(n)]
    return {
        "z_profile": z_profile,
        "mean_z": float(np.mean(z_profile)),
        "max_bond": mps.max_bond_dimension(),
    }
