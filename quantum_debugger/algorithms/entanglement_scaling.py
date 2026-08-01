"""
Entanglement-scaling laws.

How the entanglement entropy of a subsystem grows with its size is the fingerprint of a state's
physics -- and of which tensor network can represent it:

* **Area law** ``S ~ const`` (in 1D) -- gapped ground states; representable by an MPS.
* **Logarithmic law** ``S ~ (c/3) log l`` -- 1D critical states; MERA territory.
* **Volume law** ``S ~ l`` -- generic/thermal states; the **Page value** of a random pure state,
  ``<S> ~ n_A`` bits for a subsystem of ``n_A`` qubits.

This module computes the bipartite entanglement entropy, the closed-form Page average for a
random state, and verifies that a random state saturates the Page value (volume law) while a
product state has zero entanglement (extreme area law).
"""

import numpy as np


def bipartite_entropy(state, n_left: int, base: float = 2.0) -> float:
    """
    Entanglement entropy of the first ``n_left`` qubits of a pure ``state`` -- the von Neumann
    entropy of the reduced density matrix, via the Schmidt values of the bipartition.
    """
    psi = np.asarray(state, dtype=complex)
    n = int(round(np.log2(len(psi))))
    m = psi.reshape(2 ** n_left, 2 ** (n - n_left))
    s = np.linalg.svd(m, compute_uv=False)
    p = s ** 2
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)) / np.log(base))


def max_entanglement(n_left: int, n: int) -> float:
    """Maximum possible entanglement of an ``n_left``-qubit subsystem: ``min(n_left, n-n_left)``
    bits -- the volume-law ceiling."""
    return float(min(n_left, n - n_left))


def page_average_entropy(n: int, n_left: int) -> float:
    """
    Page's formula for the *average* entanglement entropy (in nats) of a random pure state over
    ``n`` qubits with an ``n_left``-qubit subsystem:
    ``<S> = sum_{k=d_B+1}^{d_A d_B} 1/k - (d_A - 1)/(2 d_B)`` (``d_A <= d_B``). Close to the maximal
    entanglement -- the volume law.
    """
    dA, dB = 2 ** n_left, 2 ** (n - n_left)
    if dA > dB:
        dA, dB = dB, dA
    harmonic = sum(1.0 / k for k in range(dB + 1, dA * dB + 1))
    return float(harmonic - (dA - 1) / (2 * dB))


def random_state_entropy(n: int, n_left: int, samples: int = 20, seed: int = 0) -> float:
    """
    Mean bipartite entropy (in nats) of Haar-random pure states -- verified to match the Page
    average (a random state is near-maximally entangled, the volume law).
    """
    rng = np.random.default_rng(seed)
    ents = []
    for _ in range(samples):
        psi = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
        psi /= np.linalg.norm(psi)
        ents.append(bipartite_entropy(psi, n_left, base=np.e))
    return float(np.mean(ents))


def entanglement_spectrum(state, n_left: int) -> np.ndarray:
    """The entanglement spectrum: the squared Schmidt coefficients (reduced-density-matrix
    eigenvalues) of the bipartition, sorted descending. Sums to 1."""
    psi = np.asarray(state, dtype=complex)
    n = int(round(np.log2(len(psi))))
    s = np.linalg.svd(psi.reshape(2 ** n_left, 2 ** (n - n_left)), compute_uv=False)
    return np.sort(s ** 2)[::-1]


def renyi2_entropy(state, n_left: int) -> float:
    """Rényi-2 entanglement entropy ``-log2 sum lambda_i^2`` (``= -log2 Tr rho_A^2``) -- the
    measurable second Rényi entropy, a lower bound on the von Neumann entropy."""
    p = entanglement_spectrum(state, n_left)
    return float(-np.log2(np.sum(p ** 2)))


def is_area_law(entropies, atol: float = 1e-6) -> bool:
    """True iff the entanglement entropy is (nearly) constant across cut positions -- the 1D area
    law of a gapped state. ``entropies`` is the list of ``S`` vs. cut."""
    e = np.asarray(entropies, dtype=float)
    return bool(np.max(e) - np.min(e) < atol)


def volume_law_slope(n: int, seed: int = 0) -> float:
    """
    Slope of the random-state entropy versus subsystem size (for small subsystems) -- approximately
    ``1`` bit per qubit, the signature of a volume law.
    """
    sizes = list(range(1, n // 2 + 1))
    ents = [random_state_entropy(n, k, samples=10, seed=seed) / np.log(2) for k in sizes]
    return float(np.polyfit(sizes, ents, 1)[0])
