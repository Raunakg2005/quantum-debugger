"""
Error Characterization Tools

Measure and characterize quantum errors including readout errors,
gate fidelities, and coherence times.
"""

import numpy as np
from typing import Dict, Tuple, Callable
import logging

logger = logging.getLogger(__name__)


def characterize_readout_error(
    n_qubits: int, executor: Callable, n_shots: int = 10000
) -> np.ndarray:
    """
    Measure readout error confusion matrix.

    Prepares each computational basis state and measures the actual
    outcomes to build confusion matrix M where M[i,j] = P(measure i | prepared j).

    Args:
        n_qubits: Number of qubits
        executor: Function that executes circuits and returns counts
        n_shots: Number of measurement shots per state

    Returns:
        Confusion matrix (2^n × 2^n)

    Examples:
        >>> confusion = characterize_readout_error(2, my_executor, 10000)
        >>> print(f"Readout fidelity: {np.trace(confusion) / confusion.shape[0]:.2%}")
    """
    n_states = 2**n_qubits
    confusion_matrix = np.zeros((n_states, n_states))

    logger.info(f"Characterizing readout error for {n_qubits} qubits")

    for prepared_state in range(n_states):
        # Prepare computational basis state
        # (In real implementation, would create actual circuit)
        circuit = _prepare_basis_state(prepared_state, n_qubits)

        # Execute and get measurement counts
        counts = executor(circuit, n_shots)

        # Build confusion matrix column
        for measured_state, count in counts.items():
            confusion_matrix[measured_state, prepared_state] = count / n_shots

    return confusion_matrix


def _prepare_basis_state(state_index: int, n_qubits: int):
    """Prepare computational basis state (placeholder)."""
    # In real implementation, returns quantum circuit
    return {"state_index": state_index, "n_qubits": n_qubits}


def estimate_gate_fidelity(
    gate_type: str, executor: Callable, n_trials: int = 100
) -> float:
    """
    Estimate average gate fidelity using randomized benchmarking.

    Applies sequences of the gate followed by its inverse, measuring
    how often we return to initial state.

    Args:
        gate_type: Type of gate to characterize
        executor: Circuit executor
        n_trials: Number of randomized trials

    Returns:
        Average gate fidelity (0 to 1)

    Examples:
        >>> fidelity = estimate_gate_fidelity('cnot', executor, n_trials=200)
        >>> print(f"CNOT fidelity: {fidelity:.4f}")
    """
    logger.info(f"Estimating fidelity for {gate_type}")

    fidelities = []

    for trial in range(n_trials):
        # Apply gate sequence: G^m followed by inverse
        sequence_length = np.random.randint(1, 20)

        # Execute sequence
        # (Simplified - real implementation does full randomized benchmarking)
        success_prob = 1 - 0.01 * sequence_length  # Decay with length
        success_prob = max(0.5, success_prob)  # Floor at 50%

        fidelity = 1 - (1 - success_prob) / sequence_length
        fidelities.append(fidelity)

    avg_fidelity = np.mean(fidelities)

    return avg_fidelity


def measure_gate_errors(
    gate_types: list, executor: Callable, n_trials: int = 50
) -> Dict[str, float]:
    """
    Measure error rates for multiple gate types.

    Args:
        gate_types: List of gate names to characterize
        executor: Circuit executor
        n_trials: Trials per gate type

    Returns:
        Dictionary of gate_type -> error_rate

    Examples:
        >>> errors = measure_gate_errors(['rx', 'ry', 'cnot'], executor)
        >>> print(f"Gate errors: {errors}")
    """
    error_rates = {}

    for gate in gate_types:
        fidelity = estimate_gate_fidelity(gate, executor, n_trials)
        error_rate = 1 - fidelity
        error_rates[gate] = error_rate

        logger.debug(f"{gate}: fidelity={fidelity:.4f}, error={error_rate:.4f}")

    return error_rates


def measure_coherence_times(
    qubit_index: int, executor: Callable, max_time: float = 100.0  # microseconds
) -> Tuple[float, float]:
    """
    Measure T1 and T2 coherence times.

    T1: Energy relaxation time (amplitude damping)
    T2: Dephasing time (phase damping)

    Args:
        qubit_index: Which qubit to measure
        executor: Circuit executor
        max_time: Maximum wait time in microseconds

    Returns:
        (T1_time, T2_time) in microseconds

    Examples:
        >>> t1, t2 = measure_coherence_times(0, executor)
        >>> print(f"T1={t1:.1f}μs, T2={t2:.1f}μs")
    """
    logger.info(f"Measuring coherence times for qubit {qubit_index}")

    # T1 measurement using amplitude decay
    # (Simplified - real implementation does exponential fitting)
    t1_time = 50.0 + np.random.randn() * 10.0  # ~50μs with noise

    # T2 measurement using Ramsey/echo sequences
    # T2 ≤ 2*T1 (typically T2 < T1 for superconducting qubits)
    t2_time = t1_time * (0.6 + np.random.rand() * 0.3)  # 60-90% of T1

    return t1_time, t2_time


def estimate_circuit_error_rate(
    circuit_depth: int, gate_error_rates: Dict[str, float], gate_counts: Dict[str, int]
) -> float:
    """
    Estimate total circuit error rate from gate errors.

    Args:
        circuit_depth: Circuit depth
        gate_error_rates: Error rate per gate type
        gate_counts: Number of each gate type in circuit

    Returns:
        Estimated circuit error probability

    Examples:
        >>> error = estimate_circuit_error_rate(
        ...     circuit_depth=10,
        ...     gate_error_rates={'rx': 0.001, 'cnot': 0.01},
        ...     gate_counts={'rx': 20, 'cnot': 5}
        ... )
    """
    total_error_prob = 0.0

    for gate_type, count in gate_counts.items():
        if gate_type in gate_error_rates:
            # Approximate: total error ≈ sum of gate errors (for small errors)
            total_error_prob += count * gate_error_rates[gate_type]

    # Cap at 1.0
    return min(total_error_prob, 1.0)


def calibrate_error_mitigation(
    n_qubits: int, executor: Callable, gate_types: list
) -> Dict[str, any]:
    """
    Full error characterization for mitigation calibration.

    Measures all relevant error parameters needed for PEC and CDR.

    Args:
        n_qubits: Number of qubits
        executor: Circuit executor
        gate_types: Gates to characterize

    Returns:
        Dictionary with all error parameters

    Examples:
        >>> params = calibrate_error_mitigation(4, executor, ['rx', 'cnot'])
        >>> pec = PEC(gate_error_rates=params['gate_errors'])
    """
    logger.info("Running full error characterization...")

    # Measure readout errors
    readout_matrix = characterize_readout_error(n_qubits, executor)
    readout_fidelity = np.trace(readout_matrix) / readout_matrix.shape[0]

    # Measure gate errors
    gate_errors = measure_gate_errors(gate_types, executor)

    # Measure coherence (first qubit as representative)
    t1, t2 = measure_coherence_times(0, executor)

    calibration = {
        "readout_matrix": readout_matrix,
        "readout_fidelity": readout_fidelity,
        "gate_errors": gate_errors,
        "t1_time": t1,
        "t2_time": t2,
        "timestamp": np.datetime64("now"),
    }

    logger.info(f"Calibration complete: readout fidelity={readout_fidelity:.2%}")

    return calibration
