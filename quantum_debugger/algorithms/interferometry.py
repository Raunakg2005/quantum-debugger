"""
Quantum interferometry -- entangled probe states for phase estimation.

In an interferometer a phase ``theta`` is imprinted by ``e^{-i theta J_z}`` (with ``J_z`` the
collective spin) and read out. The choice of probe state sets the precision:

* An ``n``-qubit **product** probe (``|+>^n``) gives QFI ``n`` -- the standard quantum limit.
* A **GHZ** probe ``(|0...0> + |1...1>)/sqrt2`` gives QFI ``n^2`` -- the Heisenberg limit.
* A **NOON** state ``(|N,0> + |0,N>)/sqrt2`` accumulates phase ``N`` times as fast, again QFI
  ``N^2``.

This module builds the probe states and computes their QFI under the phase generator,
verifying the ``n`` (SQL) and ``n^2`` (Heisenberg) scalings exactly.
"""

import numpy as np

from .quantum_metrology import qfi_pure


def collective_jz(n: int) -> np.ndarray:
    """Collective spin ``J_z = (1/2) sum_i Z_i`` on ``n`` qubits (diagonal) -- the phase
    generator of an interferometer."""
    diag = np.zeros(2 ** n)
    for b in range(2 ** n):
        diag[b] = 0.5 * sum(1 - 2 * ((b >> i) & 1) for i in range(n))
    return np.diag(diag)


def product_probe(n: int) -> np.ndarray:
    """The uncorrelated probe ``|+>^n`` -- the standard-quantum-limit reference (QFI = ``n``)."""
    return np.ones(2 ** n, dtype=complex) / np.sqrt(2 ** n)


def ghz_probe(n: int) -> np.ndarray:
    """The GHZ probe ``(|0...0> + |1...1>)/sqrt2`` -- reaches the Heisenberg limit (QFI =
    ``n^2``)."""
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = psi[-1] = 1 / np.sqrt(2)
    return psi


def probe_qfi(state, n: int) -> float:
    """QFI of an interferometric probe under the collective ``J_z`` phase generator -- ``n`` for
    a product state, ``n^2`` for GHZ."""
    return qfi_pure(state, collective_jz(n))


def product_probe_qfi(n: int) -> float:
    """QFI of the ``n``-qubit product probe, verified equal to ``n`` (the standard quantum
    limit)."""
    return probe_qfi(product_probe(n), n)


def ghz_probe_qfi(n: int) -> float:
    """QFI of the ``n``-qubit GHZ probe, verified equal to ``n^2`` (the Heisenberg limit)."""
    return probe_qfi(ghz_probe(n), n)


def noon_phase_qfi(N: int) -> float:
    """
    QFI of a NOON state ``(|N,0> + |0,N>)/sqrt2`` under a single-arm phase (accumulating ``N``
    times faster): ``N^2`` -- Heisenberg scaling in the photon number.
    """
    # In the two-mode Fock basis the phase generator is the number difference /2 with
    # eigenvalues +/- N/2, giving variance (N/2)^2 and QFI 4 (N/2)^2 = N^2.
    return float(N ** 2)


def ramsey_signal(theta: float, n: int, ghz: bool = False) -> float:
    """
    Ramsey interference signal ``<cos(n theta)>`` for a GHZ probe (oscillating ``n`` times
    faster) or ``<cos(theta)>`` for a single probe -- the fringe whose steeper slope gives the
    Heisenberg precision.
    """
    return float(np.cos(n * theta)) if ghz else float(np.cos(theta))
