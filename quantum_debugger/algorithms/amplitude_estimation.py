"""
Maximum-Likelihood Quantum Amplitude Estimation (MLQAE)

Estimates the amplitude ``a`` of the "good" subspace of a state A|0> =
sqrt(a)|good> + sqrt(1-a)|bad>, without Quantum Phase Estimation (Suzuki et al.
2020). Grover's operator is applied m_k times for a schedule of powers; the
probability of measuring a "good" outcome is sin^2((2 m_k + 1) theta) with
sin^2(theta) = a. A maximum-likelihood fit over the observed good-counts recovers
theta (and hence a) with a precision that improves with the Grover depth.

Here the demonstration uses A = H^n over a search register with a set of marked
"good" states, so a = M / N -- but the estimator only ever sees measurement
counts, never M.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary


def _good_probability(n_qubits: int, marked, power: int) -> float:
    """Exact probability of measuring a good (marked) state after `power` Grover iterates."""
    from .quantum_counting import _grover_iterate

    state = QuantumState(n_qubits)
    H = GateLibrary.H
    for q in range(n_qubits):
        state.apply_gate(H, [q])  # A|0> = uniform

    if power > 0:
        G = _grover_iterate(n_qubits, marked)
        Gp = np.linalg.matrix_power(G, power)
        state.state_vector = Gp @ state.state_vector

    probs = np.abs(state.state_vector) ** 2
    return float(sum(probs[m] for m in marked))


def amplitude_estimation(
    n_qubits: int,
    marked,
    powers=(0, 1, 2, 4, 8),
    shots: int = 2000,
    n_grid: int = 400,
    seed: int = 0,
) -> dict:
    """
    Estimate a = M/N by maximum likelihood over Grover-amplified measurements.

    Args:
        n_qubits: Search qubits (N = 2**n_qubits)
        marked: Iterable of good/marked basis states
        powers: Grover application counts m_k in the schedule
        shots: Measurement shots per power
        n_grid: Grid resolution for the theta maximum-likelihood search
        seed: RNG seed for the simulated measurements

    Returns:
        dict with 'estimated_amplitude', 'true_amplitude', 'estimated_count'.
    """
    marked = [int(m) for m in marked]
    N = 2**n_qubits
    rng = np.random.default_rng(seed)

    # Simulate good-outcome counts for each Grover power.
    good_counts = []
    for m in powers:
        p_good = _good_probability(n_qubits, marked, m)
        good_counts.append(int(rng.binomial(shots, min(max(p_good, 0.0), 1.0))))

    # Maximum-likelihood over theta in (0, pi/2): p_k(theta) = sin^2((2 m_k + 1) theta).
    thetas = np.linspace(1e-6, np.pi / 2 - 1e-6, n_grid)
    log_like = np.zeros_like(thetas)
    for m, h in zip(powers, good_counts):
        pk = np.sin((2 * m + 1) * thetas) ** 2
        pk = np.clip(pk, 1e-9, 1 - 1e-9)
        log_like += h * np.log(pk) + (shots - h) * np.log(1 - pk)

    theta_hat = thetas[int(np.argmax(log_like))]
    a_hat = float(np.sin(theta_hat) ** 2)

    return {
        "estimated_amplitude": a_hat,
        "true_amplitude": len(marked) / N,
        "estimated_count": a_hat * N,
        "true_count": len(marked),
        "theta": float(theta_hat),
    }
