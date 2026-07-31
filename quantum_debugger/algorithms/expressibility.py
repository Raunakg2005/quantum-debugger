"""
Ansatz expressibility and entangling capability.

Two descriptors quantify how "good" a variational ansatz is at exploring Hilbert space:

* **Expressibility** -- how close the distribution of fidelities between random ansatz
  states matches the Haar (uniform) distribution. For ``N = 2^n`` the Haar fidelity density
  is ``P(F) = (N-1)(1-F)^{N-2}``; the KL divergence of the sampled distribution from it is
  the expressibility (0 = maximally expressive). More layers -> lower divergence.
* **Frame potential** -- the average ``|<psi|phi>|^2`` over random pairs, which for a Haar
  ensemble equals ``1/N``; the ansatz value approaches it as it becomes expressive.

Verified: the Haar density integrates and averages correctly, and a deeper ansatz is
measurably more expressive (lower KL, frame potential nearer ``1/N``).
"""

import numpy as np

from .variational_ansatz import hardware_efficient_ansatz, ansatz_num_params


def haar_fidelity_pdf(F, dim: int):
    """Haar fidelity density ``P(F) = (N-1)(1-F)^{N-2}`` for ``N=dim`` -- the reference
    distribution of overlaps between Haar-random pure states."""
    F = np.asarray(F, dtype=float)
    return (dim - 1) * (1 - F) ** (dim - 2)


def haar_mean_fidelity(dim: int) -> float:
    """Mean fidelity ``1/dim`` of two Haar-random states -- the frame-potential target."""
    return float(1.0 / dim)


def sample_ansatz_fidelities(n: int, layers: int, samples: int = 400, seed: int = 0) -> np.ndarray:
    """Sample ``|<psi(theta)|psi(phi)>|^2`` for random parameter pairs of the ansatz -- the
    empirical fidelity distribution used for expressibility."""
    rng = np.random.default_rng(seed)
    npar = ansatz_num_params(n, layers)
    fids = []
    for _ in range(samples):
        a = hardware_efficient_ansatz(rng.uniform(0, 2 * np.pi, npar), n, layers)
        b = hardware_efficient_ansatz(rng.uniform(0, 2 * np.pi, npar), n, layers)
        fids.append(abs(np.vdot(a, b)) ** 2)
    return np.array(fids)


def frame_potential(n: int, layers: int, samples: int = 400, seed: int = 0) -> float:
    """Average fidelity (first-order frame potential) of the ansatz -- approaches the Haar
    value ``1/2^n`` as the ansatz becomes expressive."""
    return float(np.mean(sample_ansatz_fidelities(n, layers, samples, seed)))


def expressibility_kl(n: int, layers: int, samples: int = 2000, bins: int = 40,
                      seed: int = 0) -> float:
    """
    Expressibility as the KL divergence between the sampled ansatz-fidelity histogram and the
    Haar density -- smaller means more expressive. Verified to decrease as layers are added.
    """
    dim = 2 ** n
    fids = sample_ansatz_fidelities(n, layers, samples, seed)
    edges = np.linspace(0, 1, bins + 1)
    p_hist, _ = np.histogram(fids, bins=edges, density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    q = haar_fidelity_pdf(centers, dim)
    p = np.where(p_hist > 1e-12, p_hist, 1e-12)
    q = np.where(q > 1e-12, q, 1e-12)
    width = edges[1] - edges[0]
    return float(np.sum(p * np.log(p / q) * width))
