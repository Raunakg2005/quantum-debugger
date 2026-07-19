"""
Amplitude Amplification

The generalization of Grover's search (Brassard et al.): given any state
preparation A with A|0> = sqrt(a)|good> + sqrt(1-a)|bad>, the operator
Q = D_A * O_f -- where O_f phase-flips the good states and D_A = 2|psi_A><psi_A| - I
reflects about A|0> -- rotates amplitude toward |good>, boosting the success
probability to ~1 in about (pi / 4) / arcsin(sqrt(a)) iterations. Grover's
algorithm is the special case A = H^n.
"""

import numpy as np

from ..core.circuit import QuantumCircuit


def optimal_amplification_iterations(initial_amplitude: float) -> int:
    """Iterations to rotate an initial good-amplitude probability toward 1."""
    a = min(max(initial_amplitude, 1e-12), 1.0)
    theta = np.arcsin(np.sqrt(a))
    return max(1, int(round((np.pi / 2 - theta) / (2 * theta))))


def amplitude_amplification(
    state_prep: QuantumCircuit,
    marked,
    iterations: int = None,
) -> dict:
    """
    Amplify the marked ("good") states of a prepared state.

    Args:
        state_prep: Circuit implementing A (its output A|0> is the start state)
        marked: Iterable of good/marked basis-state indices
        iterations: Number of amplification rounds (default: the optimal count)

    Returns:
        dict with 'probabilities', 'initial_probability', 'success_probability',
        and 'iterations'.
    """
    marked = [int(m) for m in marked]
    psi = state_prep.get_statevector().state_vector.astype(complex)
    dim = psi.shape[0]

    initial_prob = float(sum(np.abs(psi[m]) ** 2 for m in marked))
    if iterations is None:
        iterations = optimal_amplification_iterations(initial_prob)

    # Oracle O_f: phase-flip marked states.
    O = np.eye(dim, dtype=complex)
    for m in marked:
        O[m, m] = -1.0
    # Reflection about A|0>.
    D = 2.0 * np.outer(psi, psi.conj()) - np.eye(dim, dtype=complex)
    Q = D @ O

    state = psi.copy()
    for _ in range(iterations):
        state = Q @ state

    probs = np.abs(state) ** 2
    return {
        "probabilities": probs,
        "initial_probability": initial_prob,
        "success_probability": float(sum(probs[m] for m in marked)),
        "iterations": iterations,
    }
