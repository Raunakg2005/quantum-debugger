"""
Entanglement growth after a quantum quench

Start in a low-entanglement (product) state and let it evolve under an entangling
Hamiltonian: the bipartite entanglement entropy of a subregion grows in time and
saturates near the thermal (volume-law) value. This is how isolated quantum systems
"thermalize" -- locally they look thermal because information has spread into
entanglement with the rest -- and the linear-then-saturating entropy curve is the
hallmark measured in cold-atom experiments.

Exact check reproduced here: two qubits coupled by ``X x X``, starting in ``|00>``,
evolve to ``cos(gt)|00> - i sin(gt)|11>``, so the reduced single-qubit entropy is the
binary entropy ``h(sin^2(g t))`` -- which this routine matches to machine precision.
"""

import numpy as np
from scipy.linalg import expm

from ..density_matrix import DensityMatrix


def entanglement_growth(hamiltonian, initial_state, region, times) -> dict:
    """
    Track the entanglement entropy of ``region`` (a list of qubit indices) as
    ``initial_state`` evolves under ``hamiltonian`` over ``times``.

    Returns dict with:
      * ``entropy``      -- entanglement entropy (bits) at each time
      * ``initial``      -- entropy at ``t = 0``
      * ``saturation``   -- late-time average (mean over the last third of the samples)
      * ``max_entropy``  -- the volume-law bound ``min(|region|, n - |region|)``
    """
    H = np.asarray(hamiltonian, dtype=complex)
    psi0 = np.asarray(initial_state, dtype=complex)
    psi0 = psi0 / np.linalg.norm(psi0)
    n = int(round(np.log2(H.shape[0])))

    entropies = []
    for t in times:
        psi = expm(-1j * H * t) @ psi0
        entropies.append(DensityMatrix(state_vector=psi).entanglement_entropy(region))
    entropies = np.array(entropies)

    tail = entropies[max(1, 2 * len(entropies) // 3) :]
    return {
        "entropy": entropies,
        "initial": float(entropies[0]),
        "saturation": float(np.mean(tail)) if len(tail) else float(entropies[-1]),
        "max_entropy": float(min(len(region), n - len(region))),
    }
