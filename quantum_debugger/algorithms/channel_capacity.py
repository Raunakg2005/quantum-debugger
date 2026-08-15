"""
Quantum channel capacity (coherent information)

How many qubits per use can a noisy channel transmit *quantumly*? The one-shot
answer is the coherent information

    I_c(rho, N) = S(N(rho)) - S(E),

where ``S(E)`` -- the entropy leaked to the environment -- is computed by purifying
``rho`` with a reference, sending the system half through the channel, and taking
the entropy of the joint output. Maximized over inputs (and regularized), this is
the quantum capacity ``Q`` (Lloyd-Shor-Devetak).

For the amplitude-damping channel the diagonal-input coherent information has the
known closed form (single-letter for ``gamma <= 1/2``, where the channel is
degradable):

    I_c(p, gamma) = h((1 - gamma) p) - h(gamma p),

with ``h`` the binary entropy. At ``gamma = 1/2`` the channel becomes
*antidegradable* -- the environment receives as much as the receiver -- and the
capacity is exactly zero (else cloning would be possible). This module computes
``I_c`` from first principles (purification + Kraus evolution, no formulas) and
verifies the closed form.
"""

import numpy as np

from ..density_matrix import DensityMatrix, amplitude_damping


def _binary_entropy(x: float) -> float:
    if x <= 0 or x >= 1:
        return 0.0
    return float(-x * np.log2(x) - (1 - x) * np.log2(1 - x))


def coherent_information(kraus_ops, rho) -> float:
    """
    Coherent information ``I_c(rho, N) = S(N(rho)) - S(E)`` of a single-qubit channel
    ``N`` (given as Kraus operators) at input ``rho``, in bits.

    Computed genuinely: ``rho`` is purified with a reference qubit, the system half
    is sent through the channel, and ``S(E)`` is read off as the entropy of the joint
    (system + reference) output. Positive ``I_c`` certifies the channel can protect
    quantum information at this input.
    """
    rho = np.asarray(rho, dtype=complex)
    vals, vecs = np.linalg.eigh(rho)
    vals = np.clip(vals.real, 0, None)

    # |psi> = sum_i sqrt(l_i) |e_i>_S |i>_R  (system = qubit 0, reference = qubit 1).
    psi = np.zeros(4, dtype=complex)
    for i in range(2):
        for s in range(2):
            psi[s + 2 * i] += np.sqrt(vals[i]) * vecs[s, i]

    joint = DensityMatrix(state_vector=psi)
    joint.apply_channel(kraus_ops, [0])
    s_env = joint.von_neumann_entropy()  # = S(E) by purification

    out = DensityMatrix(rho=rho)
    out.apply_channel(kraus_ops, [0])
    return out.von_neumann_entropy() - s_env


def amplitude_damping_capacity(gamma: float) -> dict:
    """
    Quantum capacity of the amplitude-damping channel of strength ``gamma``,
    maximizing the coherent information over diagonal inputs ``diag(1-p, p)``
    (optimal for this channel; single-letter in the degradable regime
    ``gamma <= 1/2``).

    Returns dict with ``capacity`` (0 for ``gamma >= 1/2`` -- the channel is then
    antidegradable), ``optimal_input`` (the maximizing ``p``), and ``analytic``
    (the closed form ``h((1-gamma) p*) - h(gamma p*)``, equal to ``capacity``).
    """
    from scipy.optimize import minimize_scalar

    kraus = amplitude_damping(gamma)

    def neg_ic(p):
        return -coherent_information(kraus, np.diag([1 - p, p]).astype(complex))

    res = minimize_scalar(neg_ic, bounds=(1e-9, 1 - 1e-9), method="bounded",
                          options={"xatol": 1e-10})
    p_star = float(res.x)
    ic = -float(res.fun)
    capacity = max(0.0, ic)
    if capacity < 1e-12:  # antidegradable regime: exactly zero
        capacity = 0.0
        p_star = 0.0

    analytic = max(
        0.0,
        _binary_entropy((1 - gamma) * p_star) - _binary_entropy(gamma * p_star),
    )
    return {"capacity": capacity, "optimal_input": p_star, "analytic": analytic}
