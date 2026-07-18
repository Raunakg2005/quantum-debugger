"""
Ansatz Analysis Toolkit

Quantitative diagnostics for variational quantum circuits (ansatze):

- **Expressibility** (Sim et al. 2019): how uniformly the ansatz covers the
  Hilbert space, measured as the KL divergence between its output-state fidelity
  distribution and the Haar-random distribution. Smaller = more expressible.
- **Entangling capability** (Meyer-Wallach Q measure): the average entanglement
  the ansatz produces, in [0, 1]. Larger = more entangling.
- **Gradient variance / barren plateaus** (McClean et al. 2018): the variance of
  a cost-function partial derivative over random parameters. In a barren
  plateau this variance vanishes exponentially with the qubit count.

All three are computed on the real state-vector simulator with a hardware-
efficient ansatz (RY rotations + a CNOT entangling chain per layer).
"""

import numpy as np


def n_params(n_qubits: int, n_layers: int) -> int:
    """Number of trainable parameters in the hardware-efficient ansatz."""
    return n_layers * n_qubits


def _hea_state(n_qubits: int, n_layers: int, params: np.ndarray) -> np.ndarray:
    """State vector of a hardware-efficient ansatz for the given parameters."""
    from ...core.circuit import QuantumCircuit

    circuit = QuantumCircuit(n_qubits)
    p = 0
    for _ in range(n_layers):
        for q in range(n_qubits):
            circuit.ry(float(params[p]), q)
            p += 1
        for q in range(n_qubits - 1):
            circuit.cnot(q, q + 1)
    return circuit.get_statevector().state_vector


def expressibility(
    n_qubits: int,
    n_layers: int,
    n_samples: int = 300,
    n_bins: int = 75,
    seed: int = 0,
) -> float:
    """
    Expressibility as KL(P_ansatz || P_Haar) over the fidelity distribution.

    Draws random parameter pairs, computes the state fidelities
    |<psi(theta)|psi(phi)>|^2, histograms them, and compares to the analytic
    Haar fidelity distribution P(F) = (N-1)(1-F)^(N-2), N = 2**n_qubits.

    Returns:
        KL divergence >= 0. Smaller means closer to Haar, i.e. more expressible.
    """
    rng = np.random.default_rng(seed)
    d = n_params(n_qubits, n_layers)
    N = 2**n_qubits

    fidelities = np.empty(n_samples)
    for i in range(n_samples):
        s1 = _hea_state(n_qubits, n_layers, rng.uniform(0, 2 * np.pi, d))
        s2 = _hea_state(n_qubits, n_layers, rng.uniform(0, 2 * np.pi, d))
        fidelities[i] = np.abs(np.vdot(s1, s2)) ** 2

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    p_ansatz, _ = np.histogram(fidelities, bins=bins)
    p_ansatz = p_ansatz / p_ansatz.sum()

    # Analytic Haar probability mass per bin: integral of (N-1)(1-F)^(N-2) is
    # (1-a)^(N-1) - (1-b)^(N-1) over [a, b].
    p_haar = (1.0 - bins[:-1]) ** (N - 1) - (1.0 - bins[1:]) ** (N - 1)
    p_haar = p_haar / p_haar.sum()

    mask = p_ansatz > 0
    kl = np.sum(p_ansatz[mask] * np.log(p_ansatz[mask] / (p_haar[mask] + 1e-12)))
    return float(kl)


def entangling_capability(
    n_qubits: int,
    n_layers: int,
    n_samples: int = 300,
    seed: int = 0,
) -> float:
    """
    Meyer-Wallach entangling capability, averaged over random parameters.

    Q = 1 - (1/n) sum_q |r_q|^2, where r_q is the Bloch vector of qubit q's
    reduced state (|r_q| = 1 for a product state -> Q = 0; |r_q| = 0 for a
    maximally mixed qubit -> Q = 1).

    Returns:
        Mean Q in [0, 1]. Larger means more entangling.
    """
    from ...core.quantum_state import QuantumState

    rng = np.random.default_rng(seed)
    d = n_params(n_qubits, n_layers)

    q_values = np.empty(n_samples)
    for i in range(n_samples):
        sv = _hea_state(n_qubits, n_layers, rng.uniform(0, 2 * np.pi, d))
        state = QuantumState(n_qubits, state_vector=sv)
        purity_sum = 0.0
        for q in range(n_qubits):
            r = np.array(state.bloch_vector(q))
            purity_sum += float(np.dot(r, r))  # |r_q|^2
        q_values[i] = 1.0 - purity_sum / n_qubits
    return float(np.mean(q_values))


def gradient_variance(
    n_qubits: int,
    n_layers: int,
    n_samples: int = 150,
    param_index: int = 0,
    seed: int = 0,
) -> float:
    """
    Variance of d<Z_0>/d(theta) over random parameters (barren-plateau probe).

    A vanishing variance that shrinks exponentially with n_qubits is the barren
    plateau signature (McClean et al.).

    Returns:
        Variance of the cost-function partial derivative.
    """
    rng = np.random.default_rng(seed)
    d = n_params(n_qubits, n_layers)
    shift = np.pi / 2

    def cost(params):
        sv = _hea_state(n_qubits, n_layers, params)
        probs = np.abs(sv) ** 2
        indices = np.arange(sv.shape[0])
        return float(np.dot(probs, 1.0 - 2.0 * (indices & 1)))  # <Z_0>

    grads = np.empty(n_samples)
    for i in range(n_samples):
        params = rng.uniform(0, 2 * np.pi, d)
        p_plus = params.copy()
        p_plus[param_index] += shift
        p_minus = params.copy()
        p_minus[param_index] -= shift
        grads[i] = 0.5 * (cost(p_plus) - cost(p_minus))
    return float(np.var(grads))
