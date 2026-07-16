"""
Quantum Generative Adversarial Networks (QGANs)

Quantum circuit-based generative models using adversarial training.

The generator is a genuine variational quantum circuit simulated on the
state-vector backend; the discriminator is a real (trainable) classifier over
measurable features of a state. Training is a real adversarial loop: the
discriminator is updated with exact gradients of the binary cross-entropy, and
the generator is updated with finite-difference gradients of the discriminator
score through the actual generator circuit.
"""

import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class QuantumGAN:
    """
    Quantum Generative Adversarial Network.

    A variational quantum generator produces quantum states; a discriminator
    learns to tell generated states from real ones. Adversarial training drives
    the generator's output distribution toward the real-data distribution.

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
            n_qubits: Number of qubits in the generator
            n_layers: Number of variational layers
            discriminator_type: 'classical' (features = measurement
                probabilities) or 'quantum' (features = per-qubit <Z>)
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.discriminator_type = discriminator_type

        # Generator: one RY angle per qubit per layer.
        self.generator_params = np.random.randn(n_layers * n_qubits) * 0.1

        # Discriminator: linear-in-features classifier (weights + bias).
        n_features = self._n_features()
        self.discriminator_params = np.random.randn(n_features + 1) * 0.1

        self.training_history = {"generator_loss": [], "discriminator_loss": []}

    def _n_features(self) -> int:
        return self.n_qubits if self.discriminator_type == "quantum" else 2**self.n_qubits

    def _generator_circuit(self, noise: np.ndarray) -> np.ndarray:
        """
        Genuine variational generator circuit.

        Encodes the noise as single-qubit RY rotations, then applies
        ``n_layers`` of (RY rotations + a CNOT entangling chain) parameterized by
        ``generator_params``, and returns the simulated state vector.

        Args:
            noise: Random noise input (length >= 1)

        Returns:
            Generated (normalized) quantum state vector of size 2**n_qubits
        """
        from ...core.circuit import QuantumCircuit

        noise = np.asarray(noise, dtype=float).ravel()
        if noise.size == 0:
            noise = np.zeros(1)

        circuit = QuantumCircuit(self.n_qubits)

        # Noise encoding
        for q in range(self.n_qubits):
            circuit.ry(float(noise[q % noise.size]), q)

        # Variational layers with entanglement
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(self.generator_params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)

        return circuit.get_statevector().state_vector

    def _features(self, state: np.ndarray) -> np.ndarray:
        """Real, measurable features of a state used by the discriminator."""
        state = np.asarray(state)
        probs = np.abs(state) ** 2
        if self.discriminator_type == "quantum":
            # Per-qubit Pauli-Z expectation values.
            indices = np.arange(state.shape[0])
            return np.array(
                [np.dot(probs, 1.0 - 2.0 * ((indices >> q) & 1)) for q in range(self.n_qubits)]
            )
        return probs

    def _discriminator(self, state: np.ndarray) -> float:
        """
        Discriminator: probability that ``state`` is real.

        A logistic classifier over measurable features of the state:
        D(state) = sigmoid(w . features(state) + b).

        Returns:
            Probability in [0, 1]
        """
        features = self._features(state)
        weights = self.discriminator_params[:-1]
        bias = self.discriminator_params[-1]
        z = float(np.dot(features, weights) + bias)
        return 1.0 / (1.0 + np.exp(-z))

    def _discriminator_loss(self, d_real: np.ndarray, d_fake: np.ndarray) -> float:
        return float(
            -np.mean(np.log(d_real + 1e-8) + np.log(1.0 - d_fake + 1e-8))
        )

    def _generator_loss(self, d_fake: np.ndarray) -> float:
        return float(-np.mean(np.log(d_fake + 1e-8)))

    def train(
        self,
        real_data: np.ndarray,
        epochs: int = 50,
        batch_size: int = 16,
        learning_rate: float = 0.05,
    ):
        """
        Train the QGAN with a real adversarial loop.

        Args:
            real_data: Real quantum states (n_samples, 2**n_qubits)
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        real_data = np.asarray(real_data)
        n_samples = len(real_data)
        n_batches = max(1, n_samples // batch_size)

        for epoch in range(epochs):
            epoch_g_loss = 0.0
            epoch_d_loss = 0.0

            for batch_idx in range(0, n_samples, batch_size):
                batch_real = real_data[batch_idx : batch_idx + batch_size]
                m = len(batch_real)
                if m == 0:
                    continue

                # ---- Discriminator step (exact BCE gradient) ----
                noise = np.random.randn(m, self.n_qubits)
                fake_states = np.array([self._generator_circuit(z) for z in noise])

                real_feats = np.array([self._features(s) for s in batch_real])
                fake_feats = np.array([self._features(s) for s in fake_states])
                d_real = np.array([self._discriminator(s) for s in batch_real])
                d_fake = np.array([self._discriminator(s) for s in fake_states])

                # d(-log D_real)/dz = D_real - 1 ; d(-log(1-D_fake))/dz = D_fake
                grad_w = np.mean(
                    (d_real - 1.0)[:, None] * real_feats + d_fake[:, None] * fake_feats,
                    axis=0,
                )
                grad_b = float(np.mean((d_real - 1.0) + d_fake))
                self.discriminator_params[:-1] -= learning_rate * grad_w
                self.discriminator_params[-1] -= learning_rate * grad_b

                d_loss = self._discriminator_loss(d_real, d_fake)

                # ---- Generator step (finite-diff through the real circuit) ----
                gen_noise = np.random.randn(m, self.n_qubits)
                g_loss, grad_g = self._generator_gradient(gen_noise)
                self.generator_params -= learning_rate * grad_g

                epoch_g_loss += g_loss
                epoch_d_loss += d_loss

            self.training_history["generator_loss"].append(epoch_g_loss / n_batches)
            self.training_history["discriminator_loss"].append(epoch_d_loss / n_batches)

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch + 1}/{epochs}: "
                    f"G_loss={epoch_g_loss / n_batches:.4f}, "
                    f"D_loss={epoch_d_loss / n_batches:.4f}"
                )

    def _generator_gradient(self, noise_batch: np.ndarray, epsilon: float = 1e-3):
        """
        Central finite-difference gradient of the generator loss w.r.t. the
        generator parameters, holding the noise batch fixed. This is a genuine
        numerical gradient of ``-mean log D(G(theta, noise))`` obtained by
        re-simulating the real generator circuit.
        """
        base_params = self.generator_params.copy()

        def loss_for(params):
            self.generator_params = params
            fakes = np.array([self._generator_circuit(z) for z in noise_batch])
            d_fake = np.array([self._discriminator(s) for s in fakes])
            return self._generator_loss(d_fake)

        base_loss = loss_for(base_params)
        grad = np.zeros_like(base_params)
        for k in range(base_params.shape[0]):
            p_plus = base_params.copy()
            p_plus[k] += epsilon
            p_minus = base_params.copy()
            p_minus[k] -= epsilon
            grad[k] = (loss_for(p_plus) - loss_for(p_minus)) / (2 * epsilon)

        self.generator_params = base_params  # restore
        return base_loss, grad

    def generate(self, n_samples: int) -> np.ndarray:
        """
        Generate quantum states from the trained generator.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Generated states (n_samples, 2**n_qubits)
        """
        noise = np.random.randn(n_samples, self.n_qubits)
        return np.array([self._generator_circuit(z) for z in noise])

    def get_training_history(self) -> Dict:
        """Get training history."""
        return self.training_history
