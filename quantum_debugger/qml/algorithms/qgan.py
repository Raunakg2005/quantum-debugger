"""
Quantum Generative Adversarial Networks (QGANs)

Quantum circuit-based generative models using adversarial training.
"""

import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class QuantumGAN:
    """
    Quantum Generative Adversarial Network.

    Uses a quantum circuit as generator to produce quantum states,
    and a classical or quantum discriminator to distinguish real from fake.

    Applications:
    - Generate quantum states
    - Data augmentation
    - Anomaly detection
    - Quantum state preparation

    Examples:
        >>> qgan = QuantumGAN(n_qubits=4, n_layers=3)
        >>> qgan.train(real_data, epochs=50, batch_size=16)
        >>> generated = qgan.generate(n_samples=10)
    """

    def __init__(
        self, n_qubits: int, n_layers: int = 3, discriminator_type: str = "classical"
    ):
        """
        Initialize QGAN.

        Args:
            n_qubits: Number of qubits in generator
            n_layers: Number of variational layers
            discriminator_type: 'classical' or 'quantum'
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.discriminator_type = discriminator_type

        # Initialize generator parameters
        self.generator_params = np.random.randn(n_layers * n_qubits) * 0.1

        # Initialize discriminator
        if discriminator_type == "classical":
            self.discriminator_params = np.random.randn(n_qubits * 10) * 0.1
        else:
            self.discriminator_params = np.random.randn(n_layers * n_qubits) * 0.1

        self.training_history = {"generator_loss": [], "discriminator_loss": []}

    def _generator_circuit(self, noise: np.ndarray) -> np.ndarray:
        """
        Quantum generator circuit.

        Args:
            noise: Random noise input

        Returns:
            Generated quantum state
        """
        # Simple parametrized state generation
        # Initialize state vector
        state_size = 2**self.n_qubits
        state = np.zeros(state_size, dtype=complex)
        state[0] = 1.0  # Start in |0...0>

        # Apply simple transformations based on noise and parameters
        # This is a simplified quantum circuit simulation
        for i in range(min(self.n_layers, 3)):  # Limit layers for stability
            # Mix state with noise and parameters
            angle = noise[i % len(noise)] + self.generator_params[i * self.n_qubits]

            # Simple rotation (simplified)
            phase = np.exp(1j * angle)
            for j in range(state_size):
                state[j] *= phase

        # Normalize
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm

        return state

    def _discriminator(self, state: np.ndarray) -> float:
        """
        Discriminator network.

        Args:
            state: Quantum state to classify

        Returns:
            Probability that state is real (0-1)
        """
        if self.discriminator_type == "classical":
            # Classical neural network (simplified)
            features = np.abs(state) ** 2  # Convert to probabilities

            # Simple linear classifier
            # Just take weighted sum of features
            weights = self.discriminator_params[: len(features)]
            output = np.dot(features, weights[: len(features)])

            # Sigmoid activation
            prob = 1 / (1 + np.exp(-output))
            return float(prob)
        else:
            # Quantum discriminator (simplified)
            return float(np.random.rand())  # Placeholder

    def train(
        self,
        real_data: np.ndarray,
        epochs: int = 50,
        batch_size: int = 16,
        learning_rate: float = 0.01,
    ):
        """
        Train QGAN using adversarial training.

        Args:
            real_data: Real quantum states for training
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        n_samples = len(real_data)

        for epoch in range(epochs):
            epoch_g_loss = 0
            epoch_d_loss = 0

            for batch_idx in range(0, n_samples, batch_size):
                batch_real = real_data[
                    batch_idx:min(batch_idx + batch_size, n_samples)
                ]

                # Train discriminator
                # Generate fake samples
                noise = np.random.randn(len(batch_real), self.n_qubits)
                fake_states = np.array([self._generator_circuit(n) for n in noise])

                # Discriminator on real
                d_real = np.array([self._discriminator(s) for s in batch_real])
                # Discriminator on fake
                d_fake = np.array([self._discriminator(s) for s in fake_states])

                # Discriminator loss (binary cross-entropy)
                d_loss = -np.mean(np.log(d_real + 1e-8) + np.log(1 - d_fake + 1e-8))

                # Update discriminator (simplified gradient descent)
                grad_d = (d_fake - d_real).mean()
                self.discriminator_params -= learning_rate * grad_d

                # Train generator
                # Generate new fakes
                noise = np.random.randn(len(batch_real), self.n_qubits)
                fake_states = np.array([self._generator_circuit(n) for n in noise])
                d_fake = np.array([self._discriminator(s) for s in fake_states])

                # Generator loss (fool discriminator)
                g_loss = -np.mean(np.log(d_fake + 1e-8))

                # Update generator (simplified)
                grad_g = (1 - d_fake).mean()
                self.generator_params -= learning_rate * grad_g * 0.1

                epoch_g_loss += g_loss
                epoch_d_loss += d_loss

            # Record history
            self.training_history["generator_loss"].append(
                epoch_g_loss / (n_samples // batch_size)
            )
            self.training_history["discriminator_loss"].append(
                epoch_d_loss / (n_samples // batch_size)
            )

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch + 1}/{epochs}: G_loss={epoch_g_loss:.4f}, D_loss={epoch_d_loss:.4f}"
                )

    def generate(self, n_samples: int) -> np.ndarray:
        """
        Generate fake quantum states.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Generated quantum states
        """
        noise = np.random.randn(n_samples, self.n_qubits)
        generated = np.array([self._generator_circuit(n) for n in noise])
        return generated

    def get_training_history(self) -> Dict:
        """Get training history."""
        return self.training_history
