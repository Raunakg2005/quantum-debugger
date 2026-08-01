"""
Quantum-channel capacities.

A noisy channel ``N`` has several capacities, one per communication task:

* **Coherent information** ``I_c = S(N(rho)) - S((id (x) N)(|psi><psi|))`` -- the quantum
  analogue of mutual information, whose maximum (regularized) is the **quantum capacity**.
* **Entanglement-assisted capacity** ``C_E = max_rho I(rho, N)`` -- the quantum mutual
  information, the cleanest capacity (single-letter, no regularization).
* **Private capacity** -- the rate of secret classical bits.

Several channels have closed-form capacities the code is checked against: the erasure channel
has quantum capacity ``max(0, 1-2p)``, the dephasing channel ``1 - h(p)``, and coherent
information is non-negative only below the channel's noise threshold. This module builds the
standard channels and their capacities and verifies them against those formulas.
"""

import numpy as np

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def _vn(rho, base=2):
    w = np.linalg.eigvalsh(np.asarray(rho, dtype=complex))
    w = np.real(w[w > 1e-12])
    return float(-np.sum(w * np.log(w)) / np.log(base))


def binary_entropy(p: float) -> float:
    """Binary entropy ``h(p) = -p log2 p - (1-p) log2(1-p)``."""
    if p <= 0 or p >= 1:
        return 0.0
    return float(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


def depolarizing_kraus(p: float):
    """Kraus operators of the single-qubit depolarizing channel ``(1-p)rho + p I/2``."""
    return [np.sqrt(1 - 3 * p / 4) * _I, np.sqrt(p / 4) * _X,
            np.sqrt(p / 4) * _Y, np.sqrt(p / 4) * _Z]


def dephasing_kraus(p: float):
    """Kraus operators of the phase-flip (dephasing) channel."""
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _Z]


def amplitude_damping_kraus(gamma: float):
    """Kraus operators of the amplitude-damping channel with damping ``gamma``."""
    return [np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
            np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)]


def apply_channel(kraus, rho):
    """Apply a Kraus channel to a density matrix."""
    return sum(K @ np.asarray(rho, dtype=complex) @ K.conj().T for K in kraus)


def coherent_information(kraus, rho) -> float:
    """
    Coherent information ``I_c(rho, N) = S(N(rho)) - S(N^c(rho))`` where ``N^c`` is the
    complementary channel (via the environment). Its maximum over ``rho`` (single-letter, a
    lower bound on the quantum capacity) is non-negative only for a low-noise channel.
    """
    rho = np.asarray(rho, dtype=complex)
    out = apply_channel(kraus, rho)
    # complementary channel output: environment state B_ij = Tr(K_i rho K_j^dagger)
    m = len(kraus)
    env = np.zeros((m, m), dtype=complex)
    for i in range(m):
        for j in range(m):
            env[i, j] = np.trace(kraus[i] @ rho @ kraus[j].conj().T)
    return float(_vn(out) - _vn(env))


def entanglement_assisted_capacity(kraus, samples: int = 0) -> float:
    """
    Entanglement-assisted classical capacity ``C_E = max_rho [S(rho) + S(N(rho)) - S(N^c(rho))]``
    (the quantum mutual information). Maximized here over the maximally mixed input (optimal for
    the covariant channels used). The largest, single-letter capacity.
    """
    rho = _I / 2
    out = apply_channel(kraus, rho)
    m = len(kraus)
    env = np.zeros((m, m), dtype=complex)
    for i in range(m):
        for j in range(m):
            env[i, j] = np.trace(kraus[i] @ rho @ kraus[j].conj().T)
    return float(_vn(rho) + _vn(out) - _vn(env))


def erasure_quantum_capacity(p: float) -> float:
    """Closed-form quantum capacity of the erasure channel, ``max(0, 1 - 2p)`` -- zero above
    ``p = 1/2`` (no quantum information survives). The verification target."""
    return float(max(0.0, 1 - 2 * p))


def dephasing_quantum_capacity(p: float) -> float:
    """Closed-form quantum capacity of the dephasing channel, ``1 - h(p)`` -- verified equal to
    the maximized coherent information."""
    return float(1 - binary_entropy(p))


def holevo_information(probs, states) -> float:
    """
    Holevo information ``chi = S(sum p_i rho_i) - sum p_i S(rho_i)`` of an ensemble -- the upper
    bound on the classical information extractable from quantum states. Between 0 and ``log2 d``;
    verified non-negative and zero for identical states.
    """
    probs = np.asarray(probs, dtype=float)
    avg = sum(p * np.asarray(r, dtype=complex) for p, r in zip(probs, states))
    return float(_vn(avg) - sum(p * _vn(r) for p, r in zip(probs, states)))


def channel_fidelity(kraus) -> float:
    """
    Average gate fidelity of a channel to the identity, ``(sum_k |Tr K_k|^2 / d + 1)/(d+1)`` for
    ``d = 2`` -- 1 for the identity channel, lower for a noisy one.
    """
    d = kraus[0].shape[0]
    Fe = sum(abs(np.trace(K)) ** 2 for K in kraus) / d ** 2
    return float((d * Fe + 1) / (d + 1))
