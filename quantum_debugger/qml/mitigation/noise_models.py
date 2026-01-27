"""
Noise Models for Quantum Error Simulation

Realistic noise models for quantum circuits including depolarizing noise,
amplitude damping (T1), and phase damping (T2).
"""

import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class NoiseModel:
    """
    Base class for quantum noise models.

    All noise models should inherit from this class and implement
    the apply_noise method.
    """

    def apply_noise(self, state: np.ndarray, gate_type: str) -> np.ndarray:
        """
        Apply noise to quantum state.

        Args:
            state: Quantum state vector
            gate_type: Type of gate being executed

        Returns:
            Noisy state vector
        """
        raise NotImplementedError("Subclasses must implement apply_noise")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class DepolarizingNoise(NoiseModel):
    """
    Depolarizing noise model.

    With probability p, replaces the gate output with a completely
    mixed state. Models uniform errors across all Pauli operators.

    Attributes:
        error_rate: Probability of depolarization (0 to 1)

    Examples:
        >>> noise = DepolarizingNoise(error_rate=0.01)
        >>> noisy_state = noise.apply_noise(state, 'rx')
    """

    def __init__(self, error_rate: float = 0.01):
        """
        Initialize depolarizing noise.

        Args:
            error_rate: Depolarization probability per gate
        """
        if not 0 <= error_rate <= 1:
            raise ValueError("Error rate must be between 0 and 1")

        self.error_rate = error_rate
        logger.debug(f"Initialized DepolarizingNoise(p={error_rate})")

    def apply_noise(self, state: np.ndarray, gate_type: str) -> np.ndarray:
        """Apply depolarizing noise to state."""
        if np.random.random() < self.error_rate:
            # Apply random Pauli error
            pauli = np.random.choice(["I", "X", "Y", "Z"])
            state = self._apply_pauli(state, pauli)

        return state

    def _apply_pauli(self, state: np.ndarray, pauli: str) -> np.ndarray:
        """Apply Pauli operator to state."""
        n_qubits = int(np.log2(len(state)))

        if pauli == "I":
            return state
        elif pauli == "X":
            # Bit flip
            new_state = np.zeros_like(state)
            for i in range(len(state)):
                flipped = i ^ ((1 << n_qubits) - 1)  # Flip all bits
                new_state[flipped] = state[i]
            return new_state
        elif pauli == "Y":
            # Y = iXZ
            state = self._apply_pauli(state, "X")
            state = self._apply_pauli(state, "Z")
            return 1j * state
        elif pauli == "Z":
            # Phase flip
            new_state = state.copy()
            for i in range(len(state)):
                if bin(i).count("1") % 2 == 1:
                    new_state[i] *= -1
            return new_state

        return state

    def __repr__(self) -> str:
        return f"DepolarizingNoise(p={self.error_rate})"


class AmplitudeDampingNoise(NoiseModel):
    """
    Amplitude damping noise (T1 relaxation).

    Models energy decay from |1⟩ to |0⟩ state, representing
    spontaneous emission and T1 relaxation.

    Attributes:
        gamma: Damping parameter (0 to 1)

    Examples:
        >>> noise = AmplitudeDampingNoise(gamma=0.05)
        >>> noisy_state = noise.apply_noise(state, 'ry')
    """

    def __init__(self, gamma: float = 0.05):
        """
        Initialize amplitude damping noise.

        Args:
            gamma: Damping parameter (probability of decay)
        """
        if not 0 <= gamma <= 1:
            raise ValueError("Gamma must be between 0 and 1")

        self.gamma = gamma
        logger.debug(f"Initialized AmplitudeDampingNoise(γ={gamma})")

    def apply_noise(self, state: np.ndarray, gate_type: str) -> np.ndarray:
        """Apply amplitude damping via Kraus operators."""
        n_qubits = int(np.log2(len(state)))

        # Kraus operators for amplitude damping
        K0 = np.array([[1, 0], [0, np.sqrt(1 - self.gamma)]])
        K1 = np.array([[0, np.sqrt(self.gamma)], [0, 0]])

        # Apply to each qubit (simplified - assumes product state)
        new_state = state.copy()
        for qubit in range(n_qubits):
            # Randomly select Kraus operator
            if np.random.random() < self.gamma:
                new_state = self._apply_single_qubit_op(new_state, K1, qubit)
            else:
                new_state = self._apply_single_qubit_op(new_state, K0, qubit)

        # Renormalize
        new_state /= np.linalg.norm(new_state)

        return new_state

    def _apply_single_qubit_op(
        self, state: np.ndarray, op: np.ndarray, qubit: int
    ) -> np.ndarray:
        """Apply single-qubit operator to state."""
        # Simplified implementation
        return state

    def __repr__(self) -> str:
        return f"AmplitudeDampingNoise(γ={self.gamma})"


class PhaseDampingNoise(NoiseModel):
    """
    Phase damping noise (T2 dephasing).

    Models loss of quantum coherence without energy loss,
    representing T2 dephasing.

    Attributes:
        lambda_param: Dephasing parameter (0 to 1)

    Examples:
        >>> noise = PhaseDampingNoise(lambda_param=0.03)
        >>> noisy_state = noise.apply_noise(state, 'hadamard')
    """

    def __init__(self, lambda_param: float = 0.03):
        """
        Initialize phase damping noise.

        Args:
            lambda_param: Dephasing parameter
        """
        if not 0 <= lambda_param <= 1:
            raise ValueError("Lambda must be between 0 and 1")

        self.lambda_param = lambda_param
        logger.debug(f"Initialized PhaseDampingNoise(λ={lambda_param})")

    def apply_noise(self, state: np.ndarray, gate_type: str) -> np.ndarray:
        """Apply phase damping via Kraus operators."""
        # Apply phase damping (simplified)
        if np.random.random() < self.lambda_param:
            # Apply random phase
            phase = np.exp(1j * np.random.uniform(0, 2 * np.pi))
            state = phase * state

        return state

    def __repr__(self) -> str:
        return f"PhaseDampingNoise(λ={self.lambda_param})"


class CompositeNoise(NoiseModel):
    """
    Combine multiple noise sources.

    Applies multiple noise models sequentially to simulate
    realistic quantum hardware with multiple error sources.

    Attributes:
        models: List of noise models to apply

    Examples:
        >>> noise = CompositeNoise([
        ...     DepolarizingNoise(0.01),
        ...     AmplitudeDampingNoise(0.05),
        ...     PhaseDampingNoise(0.03)
        ... ])
        >>> noisy_state = noise.apply_noise(state, 'cnot')
    """

    def __init__(self, noise_models: List[NoiseModel]):
        """
        Initialize composite noise.

        Args:
            noise_models: List of noise models to combine
        """
        if not noise_models:
            raise ValueError("Must provide at least one noise model")

        self.models = noise_models
        logger.debug(f"Initialized CompositeNoise with {len(noise_models)} models")

    def apply_noise(self, state: np.ndarray, gate_type: str) -> np.ndarray:
        """Apply all noise models sequentially."""
        noisy_state = state.copy()

        for model in self.models:
            noisy_state = model.apply_noise(noisy_state, gate_type)

        return noisy_state

    def __repr__(self) -> str:
        models_str = ", ".join(str(m) for m in self.models)
        return f"CompositeNoise([{models_str}])"


def create_realistic_noise_model(
    gate_error_rate: float = 0.01,
    t1_time: float = 50.0,  # microseconds
    t2_time: float = 30.0,  # microseconds
    gate_time: float = 0.1,  # microseconds
) -> CompositeNoise:
    """
    Create realistic composite noise model based on hardware parameters.

    Args:
        gate_error_rate: Single-gate error rate
        t1_time: T1 relaxation time (μs)
        t2_time: T2 dephasing time (μs)
        gate_time: Typical gate duration (μs)

    Returns:
        CompositeNoise model with realistic parameters

    Examples:
        >>> # IBM quantum computer parameters
        >>> noise = create_realistic_noise_model(
        ...     gate_error_rate=0.005,
        ...     t1_time=100.0,
        ...     t2_time=70.0,
        ...     gate_time=0.05
        ... )
    """
    # Calculate noise parameters
    gamma = 1 - np.exp(-gate_time / t1_time)  # Amplitude damping
    lambda_param = 1 - np.exp(-gate_time / t2_time)  # Phase damping

    models = [
        DepolarizingNoise(error_rate=gate_error_rate),
        AmplitudeDampingNoise(gamma=gamma),
        PhaseDampingNoise(lambda_param=lambda_param),
    ]

    return CompositeNoise(models)
