"""
Zero-Noise Extrapolation (ZNE) for Error Mitigation

Implements ZNE to estimate noise-free expectation values by running circuits
at multiple scaled noise levels and extrapolating to zero noise.
"""

import numpy as np
from typing import List, Optional, Callable
from scipy.optimize import curve_fit


class ZeroNoiseExtrapolation:
    """
    Zero-Noise Extrapolation for quantum error mitigation.

    ZNE works by:
    1. Running the circuit at multiple noise levels (scale factors)
    2. Fitting a model to the noise vs. expectation value relationship
    3. Extrapolating to zero noise to estimate the ideal result
    """

    def __init__(self, scale_factors: List[float] = None, extrapolator: str = "linear"):
        """
        Initialize ZNE.

        Args:
            scale_factors: Noise scaling factors (e.g., [1, 2, 3])
            extrapolator: Extrapolation method ('linear', 'polynomial', 'exponential')
        """
        self.scale_factors = scale_factors or [1.0, 2.0, 3.0]
        self.extrapolator = extrapolator
        self.results_history = []

    def execute(
        self,
        circuit_fn: Callable,
        observable: Optional[np.ndarray] = None,
        shots: int = 1000,
    ) -> float:
        """
        Execute ZNE on a quantum circuit.

        Args:
            circuit_fn: Function that builds and runs the circuit
            observable: Observable to measure (defaults to Z on all qubits)
            shots: Number of measurement shots per scale factor

        Returns:
            Extrapolated zero-noise expectation value
        """
        # Run circuit at each noise scale
        expectations = []

        for scale in self.scale_factors:
            # Run circuit with scaled noise
            result = circuit_fn(noise_scale=scale, shots=shots)

            # Compute expectation value
            if isinstance(result, dict) and "statevector" in result:
                # Statevector result
                expectation = self._compute_expectation(
                    result["statevector"], observable
                )
            elif isinstance(result, dict) and "counts" in result:
                # Measurement counts result
                expectation = self._expectation_from_counts(
                    result["counts"], observable
                )
            else:
                # Assume result is the expectation value directly
                expectation = float(result)

            expectations.append(expectation)

        # Extrapolate to zero noise
        mitigated_value = self._extrapolate(self.scale_factors, expectations)

        # Store results
        self.results_history.append(
            {
                "scale_factors": self.scale_factors.copy(),
                "expectations": expectations,
                "mitigated": mitigated_value,
            }
        )

        return mitigated_value

    def _extrapolate(self, scales: List[float], values: List[float]) -> float:
        """
        Extrapolate to zero noise.

        Args:
            scales: Noise scale factors
            values: Measured expectation values

        Returns:
            Extrapolated zero-noise value
        """
        scales = np.array(scales)
        values = np.array(values)

        if self.extrapolator == "linear":
            # Linear fit: E(λ) = a + b*λ, extrapolate to λ=0
            coeffs = np.polyfit(scales, values, deg=1)
            return coeffs[1]  # Intercept (value at λ=0)

        elif self.extrapolator == "polynomial":
            # Polynomial fit (degree 2)
            coeffs = np.polyfit(scales, values, deg=2)
            return np.polyval(coeffs, 0)

        elif self.extrapolator == "exponential":
            # Exponential fit: E(λ) = a + b*exp(-c*λ)
            def exp_model(x, a, b, c):
                return a + b * np.exp(-c * x)

            try:
                popt, _ = curve_fit(
                    exp_model,
                    scales,
                    values,
                    p0=[values[-1], values[0] - values[-1], 1.0],
                )
                return exp_model(0, *popt)
            except Exception:
                # Fallback to linear if exponential fit fails
                coeffs = np.polyfit(scales, values, deg=1)
                return coeffs[1]

        else:
            raise ValueError(f"Unknown extrapolator: {self.extrapolator}")

    def _compute_expectation(
        self, statevector: np.ndarray, observable: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute expectation value from statevector.

        Args:
            statevector: Quantum state vector
            observable: Observable matrix (defaults to Z⊗...⊗Z)

        Returns:
            Expectation value
        """
        if observable is None:
            # Default: Z measurement on all qubits
            return np.abs(statevector[0]) ** 2 - np.abs(statevector[-1]) ** 2

        # Compute <ψ|O|ψ>
        expectation = np.conj(statevector) @ observable @ statevector
        return expectation.real

    def _expectation_from_counts(
        self, counts: dict, observable: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute expectation value from measurement counts.

        Args:
            counts: Measurement outcome counts
            observable: Observable (not used for simple Z measurement)

        Returns:
            Expectation value
        """
        # Simple Z measurement: +1 for |0⟩, -1 for |1⟩
        total = sum(counts.values())
        expectation = 0.0

        for bitstring, count in counts.items():
            # Count number of 1s (odd parity = -1, even = +1)
            parity = sum(int(b) for b in bitstring) % 2
            sign = 1 if parity == 0 else -1
            expectation += sign * count / total

        return expectation

    def get_improvement(self) -> Optional[float]:
        """
        Calculate improvement from ZNE.

        Returns:
            Relative improvement (%)
        """
        if not self.results_history:
            return None

        last_result = self.results_history[-1]
        noisy_value = last_result["expectations"][0]  # Value at scale=1
        mitigated_value = last_result["mitigated"]

        if noisy_value == 0:
            return 0.0

        improvement = abs((mitigated_value - noisy_value) / noisy_value) * 100
        return improvement


def scale_circuit_noise(circuit, scale_factor: float):
    """
    Scale the noise in a quantum circuit.

    Implementation note: This is a placeholder. Actual noise scaling
    would require modifying the noise model or using unitary folding.

    Args:
        circuit: Quantum circuit
        scale_factor: Noise scaling factor (>= 1.0)

    Returns:
        Circuit with scaled noise
    """
    # For now, return the original circuit
    # In practice, this would insert identity operations (G G†)
    # or scale noise parameters in the noise model
    return circuit


def richardson_extrapolation(
    scale_factors: List[float], values: List[float], order: int = 1
) -> float:
    """
    Richardson extrapolation for ZNE.

    Args:
        scale_factors: Noise scale factors
        values: Measured expectation values
        order: Extract order

    Returns:
        Extrapolated value
    """
    scales = np.array(scale_factors)
    vals = np.array(values)

    if order == 1:
        # First-order: E(0) = (λ₂E₁ - λ₁E₂) / (λ₂ - λ₁)
        if len(scales) < 2:
            return vals[0]

        return (scales[1] * vals[0] - scales[0] * vals[1]) / (scales[1] - scales[0])

    else:
        # Higher-order fit
        # Use polynomial extrapolation
        coeffs = np.polyfit(scales, vals, deg=min(order, len(scales) - 1))
        return np.polyval(coeffs, 0)
