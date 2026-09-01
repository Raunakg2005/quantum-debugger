"""
Decoherence-Free Subspaces (collective dephasing)

When noise hits every qubit *identically* -- e.g. a fluctuating global field adds the
same random Z phase to each qubit -- symmetry, not redundancy, can protect quantum
information. Under the collective unitary ``U(phi) = exp(-i phi/2 sum_q Z_q)`` every
basis state acquires a phase set only by its excitation number, so the equal-excitation
subspace ``span{|01>, |10>}`` picks up a single *global* phase: a logical qubit encoded
there is untouched by the noise for ANY strength -- a decoherence-free subspace (DFS).

Contrast (exact closed forms, ``phi ~ N(0, sigma^2)``):

  * bare qubit ``|+>``:            coherence shrinks by ``exp(-sigma^2 / 2)``
  * anti-DFS ``a|00> + b|11>``:    coherence shrinks by ``exp(-2 sigma^2)`` (worse!)
  * DFS ``a|01> + b|10>``:         fidelity exactly 1

The channel here is a genuine ensemble average of unitaries, computed with
Gauss-Hermite quadrature (exact for the Gaussian phase distribution to quadrature
precision), applied on the density-matrix engine.

Reference: Lidar, Chuang & Whaley, "Decoherence-Free Subspaces for Quantum
Computation" (Phys. Rev. Lett. 81, 2594, 1998).
"""

import numpy as np
from numpy.polynomial.hermite import hermgauss

from ..density_matrix import DensityMatrix


def collective_dephasing(
    dm: DensityMatrix, sigma: float, nodes: int = 41
) -> DensityMatrix:
    """
    Apply collective Gaussian dephasing to a density matrix: average
    ``U(phi) rho U(phi)-dagger`` over ``phi ~ N(0, sigma^2)`` with
    ``U(phi) = exp(-i phi/2 sum_q Z_q)``, via ``nodes``-point Gauss-Hermite
    quadrature. Returns a new DensityMatrix.
    """
    xs, ws = hermgauss(nodes)
    phis = np.sqrt(2) * sigma * xs
    weights = ws / np.sqrt(np.pi)

    n = dm.n
    z_sum = np.array(
        [sum(1 if ((k >> q) & 1) == 0 else -1 for q in range(n)) for k in range(2**n)]
    )
    out = np.zeros_like(dm.rho)
    for phi, w in zip(phis, weights):
        diag = np.exp(-1j * phi / 2 * z_sum)
        out += w * (diag[:, None] * dm.rho * diag.conj()[None, :])
    return DensityMatrix(rho=out)


def dfs_encode(alpha=1.0, beta=0.0) -> np.ndarray:
    """
    Encode a logical qubit into the collective-dephasing DFS:
    ``|0_L> = |01>``, ``|1_L> = |10>`` (equal excitation number). Returns the
    normalized 2-qubit state vector ``alpha|01> + beta|10>``.
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    sv = np.zeros(4, dtype=complex)
    sv[0b01], sv[0b10] = alpha / norm, beta / norm
    return sv


def dfs_protection(sigma: float, alpha=1.0, beta=1.0) -> dict:
    """
    Demonstrate DFS protection at noise strength ``sigma``, exactly.

    Returns dict with:
      * ``dfs_fidelity``       -- encoded ``alpha|01> + beta|10>`` after the noise
                                  (1.0 for any sigma)
      * ``bare_coherence``     -- a bare ``|+>`` qubit's surviving coherence fraction
      * ``bare_analytic``      -- ``exp(-sigma^2 / 2)``
      * ``antidfs_coherence``  -- an ``a|00> + b|11>`` qubit's surviving coherence
      * ``antidfs_analytic``   -- ``exp(-2 sigma^2)`` (twice the phase, 4x the decay rate)
    """
    dfs_sv = dfs_encode(alpha, beta)
    dfs_out = collective_dephasing(DensityMatrix(state_vector=dfs_sv), sigma)

    bare = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
    bare_out = collective_dephasing(bare, sigma)

    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    a, b = alpha / norm, beta / norm
    anti_sv = np.zeros(4, dtype=complex)
    anti_sv[0b00], anti_sv[0b11] = a, b
    anti_out = collective_dephasing(DensityMatrix(state_vector=anti_sv), sigma)

    return {
        "dfs_fidelity": dfs_out.fidelity(dfs_sv),
        "bare_coherence": float(2 * abs(bare_out.rho[0, 1])),
        "bare_analytic": float(np.exp(-(sigma**2) / 2)),
        "antidfs_coherence": float(abs(anti_out.rho[0, 3]) / (abs(a) * abs(b))),
        "antidfs_analytic": float(np.exp(-2 * sigma**2)),
    }
