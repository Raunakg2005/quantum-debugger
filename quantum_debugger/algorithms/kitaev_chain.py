"""
The Kitaev chain (topological superconductor & Majorana modes)

A 1D chain of spinless fermions with p-wave pairing,

    H = -mu sum_j n_j - t sum_j (c_j-dagger c_{j+1} + h.c.)
        + Delta sum_j (c_j c_{j+1} + h.c.),

is the simplest model with topological order. Built here on the Jordan-Wigner
operators. For ``|mu| < 2t`` the chain is in its **topological phase**: unpaired
Majorana zero modes localize at the two ends, producing a ground-state degeneracy
whose splitting is *exponentially small* in the chain length (the modes cannot talk
to each other across the bulk). For ``|mu| > 2t`` the chain is trivial, with a
unique, gapped ground state.

This nonlocal ground-state degeneracy -- robust because no local operator connects
the two Majoranas -- is the storage mechanism behind topological qubits.
"""

import numpy as np

from .jordan_wigner import jw_annihilation, jw_creation


def kitaev_chain_hamiltonian(n: int, mu: float = 0.0, t: float = 1.0,
                             delta: float = 1.0) -> np.ndarray:
    """
    Kitaev-chain Hamiltonian on ``n`` sites: chemical potential ``mu``, hopping ``t``,
    p-wave pairing ``delta``. Returns the dense ``2**n x 2**n`` matrix.
    """
    dim = 2**n
    H = np.zeros((dim, dim), dtype=complex)
    a = [jw_annihilation(j, n) for j in range(n)]
    ad = [jw_creation(j, n) for j in range(n)]

    for j in range(n):
        H += -mu * (ad[j] @ a[j])
    for j in range(n - 1):
        H += -t * (ad[j] @ a[j + 1] + ad[j + 1] @ a[j])
        H += delta * (a[j] @ a[j + 1] + ad[j + 1] @ ad[j])
    return H


def kitaev_ground_degeneracy(n: int, mu: float = 0.0, t: float = 1.0,
                             delta: float = 1.0) -> dict:
    """
    Diagnose the topological phase of an ``n``-site Kitaev chain via its ground-state
    degeneracy.

    Returns dict with:
      * ``splitting``      -- energy gap between the two lowest states (``~0`` in the
                             topological phase, ``O(1)`` in the trivial phase)
      * ``bulk_gap``       -- gap to the third state (the true excitation gap)
      * ``topological``    -- whether ``|mu| < 2t`` (the phase boundary)
      * ``nearly_degenerate`` -- whether the splitting is far below the bulk gap
                             (the operational signature of Majorana edge modes)
    """
    H = kitaev_chain_hamiltonian(n, mu, t, delta)
    ev = np.sort(np.linalg.eigvalsh(H).real)
    splitting = float(ev[1] - ev[0])
    bulk_gap = float(ev[2] - ev[0])
    return {
        "splitting": splitting,
        "bulk_gap": bulk_gap,
        "topological": abs(mu) < 2 * t,
        "nearly_degenerate": bulk_gap > 1e-9 and splitting < 0.1 * bulk_gap,
    }
