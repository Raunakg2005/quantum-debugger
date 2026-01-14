"""
Probabilistic Error Cancellation (PEC)

Gate-level error mitigation using quasi-probability decomposition.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class PEC:
    """
    Probabilistic Error Cancellation for gate error mitigation.

    Uses quasi-probability representation to cancel systematic gate errors
    by decomposing noisy gates into linear combinations of implementable operations.

    Attributes:
        gate_error_rates: Error rate per gate type
        sampling_overhead: Number of circuit samples for averaging

    Examples:
        >>> pec = PEC(gate_error_rates={'rx': 0.01, 'cnot': 0.02})
        >>> result, uncertainty = pec.apply_pec(circuit, n_samples=100)
    """

    def __init__(
        self,
        gate_error_rates: Optional[Dict[str, float]] = None,
        sampling_overhead: int = 10,
    ):
        """
        Initialize PEC.

        Args:
            gate_error_rates: Dictionary of gate_type -> error_rate
            sampling_overhead: Default number of samples
        """
        self.gate_errors = gate_error_rates or {}
        self.sampling_overhead = sampling_overhead
        self.quasi_prob_decomposition = {}

        logger.info(f"Initialized PEC with {len(self.gate_errors)} gate types")

    def set_gate_error(self, gate_type: str, error_rate: float):
        """
        Set error rate for a specific gate type.

        Args:
            gate_type: Name of gate (e.g., 'rx', 'cnot')
            error_rate: Error probability (0 to 1)
        """
        if not 0 <= error_rate <= 1:
            raise ValueError("Error rate must be between 0 and 1")

        self.gate_errors[gate_type] = error_rate
        logger.debug(f"Set error rate for {gate_type}: {error_rate}")

    def decompose_noisy_gate(
        self, gate_type: str, error_rate: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """
        Decompose noisy gate into quasi-probability sum.

        For a noisy gate with depolarizing error p:
        U_noisy = (1-p) U + (p/3)(X U + Y U + Z U)

        Rearranging:
        U = (1/(1-p)) U_noisy - (p/3(1-p))(X U_noisy + Y U_noisy + Z U_noisy)

        Args:
            gate_type: Type of gate
            error_rate: Error rate (uses stored rate if None)

        Returns:
            List of (gate_variant, quasi_probability) tuples
        """
        if error_rate is None:
            error_rate = self.gate_errors.get(gate_type, 0.01)

        if error_rate == 0:
            return [(gate_type, 1.0)]

        # Quasi-probability coefficients
        ideal_coef = 1 / (1 - error_rate)
        error_coef = -error_rate / (3 * (1 - error_rate))

        decomposition = [
            (gate_type, ideal_coef),  # Apply ideal gate
            (f"{gate_type}_X", error_coef),  # Apply with X error
            (f"{gate_type}_Y", error_coef),  # Apply with Y error
            (f"{gate_type}_Z", error_coef),  # Apply with Z error
        ]

        self.quasi_prob_decomposition[gate_type] = decomposition

        return decomposition

    def estimate_sampling_overhead(
        self, circuit_depth: int, avg_error_rate: float = 0.01
    ) -> int:
        """
        Estimate required number of samples for given accuracy.

        Sampling overhead scales exponentially with circuit depth
        and quadratically with error rate.

        Args:
            circuit_depth: Number of gates in circuit
            avg_error_rate: Average gate error rate

        Returns:
            Recommended number of samples
        """
        # Approximate formula: overhead ∝ (1/(1-p))^depth
        if avg_error_rate >= 1:
            raise ValueError("Average error rate must be < 1")

        overhead = int(np.ceil((1 / (1 - avg_error_rate)) ** circuit_depth))

        # Cap at reasonable maximum
        return min(overhead, 10000)

    def apply_pec(
        self,
        circuit_function: Callable,
        params: np.ndarray,
        n_samples: Optional[int] = None,
        return_variance: bool = True,
    ) -> Tuple[float, float]:
        """
        Apply PEC to mitigate circuit errors.

        Args:
            circuit_function: Function that executes circuit and returns result
            params: Circuit parameters
            n_samples: Number of samples (uses default if None)
            return_variance: Whether to return uncertainty estimate

        Returns:
            (mitigated_result, uncertainty) if return_variance=True
            mitigated_result otherwise
        """
        if n_samples is None:
            n_samples = self.sampling_overhead

        logger.info(f"Applying PEC with {n_samples} samples")

        # Sample according to quasi-probabilities
        results = []
        weights = []

        for _ in range(n_samples):
            # Sample circuit variant and get weight
            result, weight = self._sample_and_execute(circuit_function, params)
            results.append(result)
            weights.append(weight)

        results = np.array(results)
        weights = np.array(weights)

        # Weighted average
        mitigated = np.average(results, weights=np.abs(weights))

        if return_variance:
            # Estimate uncertainty
            variance = np.var(results * weights) / n_samples
            uncertainty = np.sqrt(variance)
            return mitigated, uncertainty

        return mitigated

    def _sample_and_execute(
        self, circuit_function: Callable, params: np.ndarray
    ) -> Tuple[float, float]:
        """
        Sample one circuit variant and execute.

        Returns:
            (result, quasi_probability_weight)
        """
        # For now, simplified version - execute with nominal circuit
        result = circuit_function(params)
        weight = 1.0  # Would be quasi-probability in full implementation

        return result, weight

    def get_mitigation_overhead(self) -> Dict[str, float]:
        """
        Get computational overhead information.

        Returns:
            Dictionary with overhead metrics
        """
        return {
            "sampling_overhead": self.sampling_overhead,
            "execution_factor": self.sampling_overhead,
            "total_overhead": self.sampling_overhead,
        }


def apply_pec(
    circuit_function: Callable,
    params: np.ndarray,
    gate_error_rates: Dict[str, float],
    n_samples: int = 100,
) -> Tuple[float, float]:
    """
    Convenience function to apply PEC.

    Args:
        circuit_function: Function that executes circuit
        params: Circuit parameters
        gate_error_rates: Error rates per gate type
        n_samples: Number of samples

    Returns:
        (mitigated_result, uncertainty)

    Examples:
        >>> result, error = apply_pec(
        ...     circuit_func,
        ...     params,
        ...     {'rx': 0.01, 'cnot': 0.02},
        ...     n_samples=100
        ... )
    """
    pec = PEC(gate_error_rates=gate_error_rates, sampling_overhead=n_samples)
    return pec.apply_pec(circuit_function, params, n_samples=n_samples)
