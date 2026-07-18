"""
Quantum Deep Q-Network (DQN)

A value-based quantum RL agent that upgrades plain quantum Q-learning with the
two ingredients that make DQN stable:

- an **experience replay** buffer (decorrelates consecutive transitions), and
- a **target network** (a periodically-synced copy of the parameters used to
  compute the TD target, which stops the target from chasing the online net).

The Q-function is a genuine parameterized quantum circuit (state angle-encoding
+ a per-action variational ansatz + a Pauli-Z readout), trained with exact
parameter-shift gradients.
"""

import random
from collections import deque
from typing import Optional

import numpy as np
import logging

logger = logging.getLogger(__name__)


class QuantumDQN:
    """
    Quantum DQN with experience replay and a target network.

    Examples:
        >>> from quantum_debugger.qml.algorithms import SimpleEnvironment
        >>> env = SimpleEnvironment(n_states=4, n_actions=2)
        >>> agent = QuantumDQN(n_qubits=4, n_actions=2, n_layers=2)
        >>> agent.train(env, episodes=100)
    """

    def __init__(
        self,
        n_qubits: int,
        n_actions: int,
        n_layers: int = 2,
        learning_rate: float = 0.1,
        gamma: float = 0.95,
        buffer_size: int = 2000,
        batch_size: int = 16,
        target_update_freq: int = 10,
    ):
        self.n_qubits = n_qubits
        self.n_actions = n_actions
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.block_size = n_layers * n_qubits
        self.params = np.random.uniform(0, 2 * np.pi, n_actions * self.block_size)
        self.target_params = self.params.copy()

        self.buffer = deque(maxlen=buffer_size)
        self.training_history = {"rewards": [], "losses": []}

    # ------------------------------------------------------------------
    # Q-function circuit
    # ------------------------------------------------------------------
    def _encode_state(self, state: np.ndarray) -> np.ndarray:
        state = np.asarray(state, dtype=float).ravel()
        norm = np.linalg.norm(state) + 1e-8
        return np.arctan(state / norm)

    def _q_value(self, state: np.ndarray, action: int, params: np.ndarray) -> float:
        from ...core.circuit import QuantumCircuit

        angles = self._encode_state(state)
        circuit = QuantumCircuit(self.n_qubits)
        for q in range(self.n_qubits):
            circuit.ry(float(angles[q % len(angles)]), q)

        p = action * self.block_size
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)

        sv = circuit.get_statevector().state_vector
        probs = np.abs(sv) ** 2
        indices = np.arange(sv.shape[0])
        return float(np.dot(probs, 1.0 - 2.0 * (indices & 1)))  # <Z_0>

    def get_q_values(
        self, state: np.ndarray, params: Optional[np.ndarray] = None
    ) -> np.ndarray:
        params = self.params if params is None else params
        return np.array(
            [self._q_value(state, a, params) for a in range(self.n_actions)]
        )

    def _q_gradient(self, state: np.ndarray, action: int) -> np.ndarray:
        """d Q(s,a)/d theta for the action's parameter block (parameter-shift)."""
        shift = np.pi / 2
        block = action * self.block_size
        grad = np.zeros(self.block_size)
        for k in range(self.block_size):
            p_plus = self.params.copy()
            p_plus[block + k] += shift
            p_minus = self.params.copy()
            p_minus[block + k] -= shift
            grad[k] = 0.5 * (
                self._q_value(state, action, p_plus)
                - self._q_value(state, action, p_minus)
            )
        return grad

    # ------------------------------------------------------------------
    # Agent API
    # ------------------------------------------------------------------
    def select_action(self, state: np.ndarray, epsilon: float = 0.0) -> int:
        if np.random.rand() < epsilon:
            return np.random.randint(self.n_actions)
        return int(np.argmax(self.get_q_values(state)))

    def remember(self, state, action, reward, next_state, done):
        self.buffer.append(
            (
                np.asarray(state, dtype=float),
                int(action),
                float(reward),
                np.asarray(next_state, dtype=float),
                bool(done),
            )
        )

    def replay(self) -> float:
        """One minibatch update. TD target uses the target network."""
        if len(self.buffer) < self.batch_size:
            return 0.0

        batch = random.sample(self.buffer, self.batch_size)
        grad = np.zeros_like(self.params)
        total_loss = 0.0

        for state, action, reward, next_state, done in batch:
            if done:
                target = reward
            else:
                # Target Q from the frozen target network.
                next_q = self.get_q_values(next_state, self.target_params)
                target = reward + self.gamma * np.max(next_q)

            q_sa = self._q_value(state, action, self.params)
            td_error = target - q_sa
            total_loss += td_error**2

            block = action * self.block_size
            grad[block : block + self.block_size] += td_error * self._q_gradient(
                state, action
            )

        # Semi-gradient step: theta += lr * mean(td_error * dQ/dtheta).
        self.params += self.learning_rate * grad / self.batch_size
        return total_loss / self.batch_size

    def train(
        self,
        env,
        episodes: int = 100,
        max_steps: int = 20,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.95,
    ):
        """Standard DQN training loop with replay and periodic target sync."""
        epsilon = epsilon_start
        step_count = 0

        for episode in range(episodes):
            state = env.reset()
            total_reward = 0.0
            episode_loss = 0.0

            for _ in range(max_steps):
                action = self.select_action(state, epsilon)
                next_state, reward, done, _ = env.step(action)
                self.remember(state, action, reward, next_state, done)

                episode_loss += self.replay()
                step_count += 1
                if step_count % self.target_update_freq == 0:
                    self.target_params = self.params.copy()

                total_reward += reward
                state = next_state
                if done:
                    break

            epsilon = max(epsilon_end, epsilon * epsilon_decay)
            self.training_history["rewards"].append(total_reward)
            self.training_history["losses"].append(episode_loss)

            if (episode + 1) % 10 == 0:
                avg = np.mean(self.training_history["rewards"][-10:])
                logger.info(
                    f"Episode {episode + 1}/{episodes}: avg reward={avg:.2f}, eps={epsilon:.3f}"
                )

        return self

    def get_training_history(self) -> dict:
        return self.training_history
