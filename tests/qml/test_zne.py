"""
Tests for Zero-Noise Extrapolation
"""

import pytest
import numpy as np
from quantum_debugger.qml.error_mitigation import (
    ZeroNoiseExtrapolation,
    richardson_extrapolation,
)


class TestZNE:
    """Test Zero-Noise Extrapolation"""

    def test_initialization(self):
        """Test ZNE initialization"""
        zne = ZeroNoiseExtrapolation(scale_factors=[1, 2, 3], extrapolator="linear")

        assert zne.scale_factors == [1, 2, 3]
        assert zne.extrapolator == "linear"

    def test_linear_extrapolation(self):
        """Test linear extrapolation"""
        zne = ZeroNoiseExtrapolation(extrapolator="linear")

        # Synthetic data: E(λ) = 1 - 0.1*λ (true value at λ=0 is 1.0)
        scales = [1.0, 2.0, 3.0]
        values = [0.9, 0.8, 0.7]

        result = zne._extrapolate(scales, values)

        # Should extrapolate to ~1.0
        assert abs(result - 1.0) < 0.01

    def test_polynomial_extrapolation(self):
        """Test polynomial extrapolation"""
        zne = ZeroNoiseExtrapolation(extrapolator="polynomial")

        # Quadratic decay
        scales = [1.0, 2.0, 3.0, 4.0]
        values = [0.95, 0.80, 0.55, 0.20]

        result = zne._extrapolate(scales, values)

        # Should return a value
        assert np.isfinite(result)

    def test_simple_circuit_execution(self):
        """Test ZNE with simple circuit function"""

        def mock_circuit(noise_scale=1.0, shots=1000):
            # Simulate noisy measurement
            # True value = 1.0, noise reduces it by 0.1 * scale
            return 1.0 - 0.1 * noise_scale

        zne = ZeroNoiseExtrapolation(
            scale_factors=[1.0, 2.0, 3.0], extrapolator="linear"
        )

        result = zne.execute(mock_circuit)

        # Should extrapolate close to 1.0
        assert abs(result - 1.0) < 0.1

    def test_improvement_tracking(self):
        """Test improvement calculation"""

        def mock_circuit(noise_scale=1.0, shots=1000):
            return 0.9 - 0.05 * noise_scale

        zne = ZeroNoiseExtrapolation(scale_factors=[1, 2, 3])
        zne.execute(mock_circuit)

        improvement = zne.get_improvement()

        assert improvement is not None
        assert improvement >= 0


class TestRichardsonExtrapolation:
    """Test Richardson extrapolation"""

    def test_first_order(self):
        """Test first-order Richardson"""
        scales = [1.0, 2.0]
        values = [0.9, 0.8]

        result = richardson_extrapolation(scales, values, order=1)

        # Linear extrapolation to λ=0
        assert abs(result - 1.0) < 0.01

    def test_higher_order(self):
        """Test higher-order Richardson"""
        scales = [1.0, 2.0, 3.0, 4.0]
        values = [1.0, 0.9, 0.7, 0.4]

        result = richardson_extrapolation(scales, values, order=2)

        assert np.isfinite(result)


class TestIntegration:
    """Integration tests for ZNE"""

    def test_multiple_runs(self):
        """Test running ZNE multiple times"""

        def circuit_fn(noise_scale=1.0, shots=1000):
            return 1.0 - 0.08 * noise_scale

        zne = ZeroNoiseExtrapolation(scale_factors=[1, 2, 3])

        # Run multiple times
        result1 = zne.execute(circuit_fn)
        result2 = zne.execute(circuit_fn)

        assert len(zne.results_history) == 2
        assert np.isfinite(result1)
        assert np.isfinite(result2)

    def test_statevector_input(self):
        """Test with statevector input"""

        def circuit_fn(noise_scale=1.0, shots=1000):
            # Return statevector
            state = np.array([0.9, 0.1j, 0.0, 0.0])
            state = state / np.linalg.norm(state)
            return {"statevector": state}

        zne = ZeroNoiseExtrapolation(scale_factors=[1, 2])
        result = zne.execute(circuit_fn)

        assert np.isfinite(result)

    def test_counts_input(self):
        """Test with measurement counts"""

        def circuit_fn(noise_scale=1.0, shots=1000):
            # Return counts dictionary
            return {"counts": {"00": 900, "11": 100}}

        zne = ZeroNoiseExtrapolation(scale_factors=[1, 2])
        result = zne.execute(circuit_fn)

        assert np.isfinite(result)
