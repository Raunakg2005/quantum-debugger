"""
Optimal universal quantum cloning (Buzek-Hillery)

The no-cloning theorem forbids perfect copies of an unknown state -- but how close
can a machine get? The Buzek-Hillery 1 -> 2 universal cloner (Phys. Rev. A 54,
1844, 1996) is the exact optimum: BOTH clones of ANY input qubit have fidelity

    F = 5/6,

independent of the state (universality), proven optimal by Gisin & Massar / Bruss
et al. For comparison, the best *classical* strategy -- measure the qubit and
prepare copies of the estimate -- reaches only ``F = 2/3``.

The cloner is the isometry (clones on qubits 0, 1; ancilla on qubit 2):

    |0> -> sqrt(2/3) |00>|0>_a + sqrt(1/6) (|01> + |10>) |1>_a
    |1> -> sqrt(2/3) |11>|1>_a + sqrt(1/6) (|01> + |10>) |0>_a

after which each clone's reduced state is ``5/6 |psi><psi| + 1/6 |psi_perp><psi_perp|``.
"""

import numpy as np

from ..density_matrix import DensityMatrix


def _bh_isometry() -> np.ndarray:
    """The 8x2 Buzek-Hillery isometry (little-endian: clones = qubits 0,1; ancilla = 2)."""
    V = np.zeros((8, 2), dtype=complex)
    s23, s16 = np.sqrt(2 / 3), np.sqrt(1 / 6)
    # |0> branch: sqrt(2/3)|00>|0>a + sqrt(1/6)(|01> + |10>)|1>a
    V[0b000, 0] = s23        # clones 00, ancilla 0
    V[0b101, 0] = s16        # clones 01 (qubit0=1), ancilla 1
    V[0b110, 0] = s16        # clones 10 (qubit1=1), ancilla 1
    # |1> branch: sqrt(2/3)|11>|1>a + sqrt(1/6)(|01> + |10>)|0>a
    V[0b111, 1] = s23
    V[0b001, 1] = s16
    V[0b010, 1] = s16
    return V


def universal_clone(alpha=1.0, beta=0.0) -> dict:
    """
    Clone the unknown qubit ``alpha|0> + beta|1>`` with the optimal universal
    (Buzek-Hillery) cloning machine.

    Returns dict with ``clone1_fidelity`` and ``clone2_fidelity`` (each exactly 5/6
    for every input -- universality), ``analytic`` (5/6), ``classical_limit`` (2/3,
    the best measure-and-prepare strategy), and ``clones_identical``.
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    psi = np.array([alpha / norm, beta / norm], dtype=complex)

    out = _bh_isometry() @ psi  # 3-qubit pure output
    dm = DensityMatrix(state_vector=out)

    clone1 = dm.partial_trace([0])
    clone2 = dm.partial_trace([1])
    f1 = float(np.real(psi.conj() @ clone1.rho @ psi))
    f2 = float(np.real(psi.conj() @ clone2.rho @ psi))

    return {
        "clone1_fidelity": f1,
        "clone2_fidelity": f2,
        "analytic": 5 / 6,
        "classical_limit": 2 / 3,
        "clones_identical": bool(np.allclose(clone1.rho, clone2.rho, atol=1e-12)),
    }
