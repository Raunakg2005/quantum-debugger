"""
Zero-Noise Extrapolation (ZNE) Main Implementation

Combines circuit folding with extrapolation to mitigate quantum noise.
"""

import numpy as np
from typing import Optional, Dict, List

from .core.folder import global_fold, local_fold, adaptive_fold
from .core.extrapolator import Extrapolator


def zero_noise_extrapolation(
    circuit,
    scale_factors: Optional[List[float]] = None,
    extrapolation_method: str = "richardson",
    folding_method: str = "global",
    shots: int = 1000,
    **kwargs,
) -> Dict:
    """
    Zero-Noise Extrapolation: run circuit at multiple noise levels and extrapolate to zero.

    Args:
        circuit: QuantumCircuit to mitigate
        scale_factors: Noise scaling factors (e.g., [1.0, 2.0, 3.0])
                      Default: [1.0, 1.5, 2.0, 2.5, 3.0]
        extrapolation_method: 'richardson', 'linear', 'exponential', 'adaptive'
        folding_method: 'global', 'local', or 'adaptive'
        shots: Number of measurement shots per noise level
        **kwargs: Additional arguments for folding/extrapolation

    Returns:
        Dictionary with:
            - mitigated_value: Extrapolated zero-noise expectation
            - unmitigated_value: Original noisy result
            - improvement_factor: Ratio of improvement
            - noise_levels: Scale factors used
            - expectation_values: Measured at each scale
            - method: Extrapolation method used
            - fidelity_unmitigated: Original fidelity (if available)
            - fidelity_mitigated: Estimated mitigated fidelity

    Example:
        >>> from quantum_debugger import QuantumCircuit
        >>> from quantum_debugger.noise import IBM_PERTH_2025
        >>> from quantum_debugger.mitigation import zero_noise_extrapolation
        >>>
        >>> circuit = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
        >>> circuit.h(0).cnot(0, 1)
        >>>
        >>> result = zero_noise_extrapolation(circuit, shots=1000)
        >>> print(f"Mitigated fidelity: {result['fidelity_mitigated']:.4f}")
        >>> print(f"Improvement: {result['improvement_factor']:.2f}x")
    """
    if not circuit.apply_noise:
        raise ValueError(
            "Circuit has no noise model. ZNE requires a noisy circuit. "
            "Set noise_model when creating the circuit."
        )

    # Default scale factors
    if scale_factors is None:
        scale_factors = [1.0, 1.5, 2.0, 2.5, 3.0]

    # Validate scale factors
    if not all(s >= 1.0 for s in scale_factors):
        raise ValueError("All scale factors must be >= 1.0")

    if 1.0 not in scale_factors:
        scale_factors = [1.0] + list(scale_factors)

    # Sort scale factors
    scale_factors = sorted(set(scale_factors))

    # Run circuit at each noise level
    expectation_values = []
    fidelities = []

    print(f"Running ZNE with {len(scale_factors)} noise levels...")

    for i, scale in enumerate(scale_factors):
        # Fold circuit to amplify noise
        if scale == 1.0:
            folded_circuit = circuit
        else:
            if folding_method == "global":
                folded_circuit = global_fold(circuit, scale)
            elif folding_method == "local":
                folded_circuit = local_fold(circuit, scale, **kwargs)
            elif folding_method == "adaptive":
                folded_circuit = adaptive_fold(circuit, scale, **kwargs)
            else:
                raise ValueError(
                    f"Unknown folding method '{folding_method}'. "
                    f"Use 'global', 'local', or 'adaptive'."
                )

        # Execute folded circuit
        result = folded_circuit.run(shots=shots)

        # Extract expectation value (fidelity if available)
        if "fidelity" in result:
            exp_val = result["fidelity"]
            fidelities.append(exp_val)
        else:
            # Fallback: use measurement probability of |00...0⟩
            counts = result.get("counts", {})
            zero_state = "0" * circuit.num_qubits
            prob_zero = counts.get(zero_state, 0) / shots
            exp_val = prob_zero
            fidelities.append(prob_zero)

        expectation_values.append(exp_val)

        print(f"  Scale {scale:.1f}: expectation = {exp_val:.4f}")

    # Convert to numpy arrays
    noise_levels = np.array(scale_factors)
    exp_values = np.array(expectation_values)

    # Extrapolate to zero noise
    if extrapolation_method == "richardson":
        order = kwargs.get("richardson_order", 2)
        mitigated = Extrapolator.richardson(noise_levels, exp_values, order)
    elif extrapolation_method == "linear":
        mitigated = Extrapolator.linear(noise_levels, exp_values)
    elif extrapolation_method == "exponential":
        mitigated, fit_info = Extrapolator.exponential(noise_levels, exp_values)
    elif extrapolation_method == "adaptive":
        mitigated, best_method = Extrapolator.adaptive(noise_levels, exp_values)
        extrapolation_method = f"adaptive({best_method})"
    else:
        raise ValueError(
            f"Unknown extrapolation method '{extrapolation_method}'. "
            f"Use 'richardson', 'linear', 'exponential', or 'adaptive'."
        )

    # Calculate improvement
    unmitigated = expectation_values[0]  # Scale = 1.0
    improvement = abs(mitigated - unmitigated) / max(abs(unmitigated), 1e-10)

    print("\nZNE Results:")
    print(f"  Unmitigated: {unmitigated:.4f}")
    print(f"  Mitigated:   {mitigated:.4f}")
    print(f"  Improvement: {improvement:.2%}")

    return {
        "mitigated_value": float(mitigated),
        "unmitigated_value": float(unmitigated),
        "improvement_factor": float(1.0 + improvement),
        "noise_levels": noise_levels.tolist(),
        "expectation_values": exp_values.tolist(),
        "extrapolation_method": extrapolation_method,
        "folding_method": folding_method,
        "fidelity_unmitigated": fidelities[0] if fidelities else None,
        "fidelity_mitigated": float(mitigated) if fidelities else None,
        "shots_per_level": shots,
        "total_shots": shots * len(scale_factors),
    }


def zne_with_error_bars(
    circuit,
    scale_factors: Optional[List[float]] = None,
    extrapolation_method: str = "richardson",
    shots: int = 1000,
    n_trials: int = 10,
) -> Dict:
    """
    ZNE with error bars via multiple trials.

    Args:
        circuit: QuantumCircuit to mitigate
        scale_factors: Noise scaling factors
        extrapolation_method: Extrapolation method
        shots: Shots per noise level
        n_trials: Number of independent ZNE trials

    Returns:
        Dict with mean, std, and confidence interval
    """
    mitigated_values = []

    for trial in range(n_trials):
        result = zero_noise_extrapolation(
            circuit,
            scale_factors=scale_factors,
            extrapolation_method=extrapolation_method,
            shots=shots,
        )
        mitigated_values.append(result["mitigated_value"])

    mean_val = np.mean(mitigated_values)
    std_val = np.std(mitigated_values)

    # 95% confidence interval
    ci_lower = mean_val - 2 * std_val
    ci_upper = mean_val + 2 * std_val

    return {
        "mean": float(mean_val),
        "std": float(std_val),
        "confidence_interval": (float(ci_lower), float(ci_upper)),
        "trials": mitigated_values,
        "n_trials": n_trials,
    }
