"""
Quantum Reinforcement Learning

Q-Learning with quantum circuits for function approximation.
"""

import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class QuantumQLearning:
    """
    Quantum Q-Learning for reinforcement learning.

    Uses quantum circuit to approximate Q-function for state-action values.

    Applications:
    - Game playing
    - Robot control
    - Optimization problems
    - Decision making

    Examples:
        >>> qrl = QuantumQLearning(n_qubits=4, n_actions=2)
        >>> qrl.train(env, episodes=100)
        >>> action = qrl.choose_action(state, epsilon=0.1)
    """

    def __init__(
        self,
        n_qubits: int,
        n_actions: int,
        n_layers: int = 3,
        learning_rate: float = 0.01,
        gamma: float = 0.99,
    ):
        """
        Initialize Quantum Q-Learning.

        Args:
            n_qubits: Number of qubits for state encoding
            n_actions: Number of possible actions
            n_layers: Number of variational layers
            learning_rate: Learning rate
            gamma: Discount factor
        """
        self.n_qubits = n_qubits
        self.n_actions = n_actions
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self.gamma = gamma

        # Initialize quantum circuit parameters
        self.params = np.random.randn(n_layers * n_qubits * n_actions) * 0.1

        self.training_history = {"rewards": [], "losses": []}

    def _encode_state(self, state: np.ndarray) -> np.ndarray:
        """
        Encode classical state into quantum circuit.

        Args:
            state: Classical state vector

        Returns:
            Encoded angles for quantum gates
        """
        # Normalize state
        state_norm = state / (np.linalg.norm(state) + 1e-8)

        # Simple encoding: state values as rotation angles
        angles = np.arctan(state_norm)
        return angles

    def _q_value(self, state: np.ndarray, action: int, params: np.ndarray) -> float:
        """
        Evaluate Q(state, action) with an explicit parameter vector.

        Builds and simulates a real circuit: the state is angle-encoded, a
        per-action variational ansatz (RY rotations + CNOT entanglers) is
        applied, and Q is read out as the Pauli-Z expectation of qubit 0.
        """
        from ...core.circuit import QuantumCircuit

        angles = self._encode_state(state)
        circuit = QuantumCircuit(self.n_qubits)
        for q in range(self.n_qubits):
            circuit.ry(float(angles[q % len(angles)]), q)  # ry(theta, qubit)

        p = action * self.n_layers * self.n_qubits
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)

        state_vector = circuit.get_statevector().state_vector
        probs = np.abs(state_vector) ** 2
        indices = np.arange(state_vector.shape[0])
        return float(np.dot(probs, 1.0 - 2.0 * (indices & 1)))  # <Z_0> in [-1, 1]

    def _q_circuit(self, state: np.ndarray, action: int) -> float:
        """
        Quantum circuit computing Q(state, action).

        Args:
            state: State vector
            action: Action index

        Returns:
            Q-value estimate in [-1, 1]
        """
        return self._q_value(state, action, self.params)

    def _q_gradient(self, state: np.ndarray, action: int) -> np.ndarray:
        """
        Exact gradient of Q(state, action) w.r.t. the action's parameters via
        the parameter-shift rule (each parameter enters through an RY gate).
        """
        block = action * self.n_layers * self.n_qubits
        n_block = self.n_layers * self.n_qubits
        shift = np.pi / 2
        grad = np.zeros(n_block)
        for k in range(n_block):
            p_plus = self.params.copy()
            p_plus[block + k] += shift
            p_minus = self.params.copy()
            p_minus[block + k] -= shift
            grad[k] = 0.5 * (
                self._q_value(state, action, p_plus)
                - self._q_value(state, action, p_minus)
            )
        return grad

    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """
        Get Q-values for all actions.

        Args:
            state: Current state

        Returns:
            Q-values for each action
        """
        q_values = np.array([self._q_circuit(state, a) for a in range(self.n_actions)])
        return q_values

    def choose_action(self, state: np.ndarray, epsilon: float = 0.1) -> int:
        """
        Choose action using epsilon-greedy policy.

        Args:
            state: Current state
            epsilon: Exploration probability

        Returns:
            Selected action
        """
        if np.random.rand() < epsilon:
            # Explore: random action
            return np.random.randint(self.n_actions)
        else:
            # Exploit: best action
            q_values = self.get_q_values(state)
            return int(np.argmax(q_values))

    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """
        Q-learning update step.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        # Current Q-value
        q_current = self._q_circuit(state, action)

        # Target Q-value
        if done:
            q_target = reward
        else:
            next_q_values = self.get_q_values(next_state)
            q_target = reward + self.gamma * np.max(next_q_values)

        # TD error
        td_error = q_target - q_current

        # Semi-gradient Q-learning update: theta_a += lr * td_error * dQ/dtheta_a,
        # with dQ/dtheta_a computed by the parameter-shift rule (was a constant
        # nudge that ignored the actual gradient).
        start_idx = action * self.n_layers * self.n_qubits
        end_idx = start_idx + self.n_layers * self.n_qubits
        grad = self._q_gradient(state, action)
        self.params[start_idx:end_idx] += self.learning_rate * td_error * grad

        return float(td_error)

    def train(
        self,
        env,  # type: SimpleEnvironment or similar with reset(), step()
        episodes: int = 100,
        max_steps: int = 200,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
    ):
        """
        Train agent in environment.

        Args:
            env: Environment with reset(), step() methods
            episodes: Number of episodes
            max_steps: Max steps per episode
            epsilon_start: Initial exploration
            epsilon_end: Final exploration
            epsilon_decay: Decay rate
        """
        epsilon = epsilon_start

        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            episode_loss = 0

            for step in range(max_steps):
                # Choose action
                action = self.choose_action(state, epsilon)

                # Take action
                next_state, reward, done, _ = env.step(action)

                # Update Q-function
                td_error = self.update(state, action, reward, next_state, done)

                episode_loss += abs(td_error)
                total_reward += reward
                state = next_state

                if done:
                    break

            # Decay epsilon
            epsilon = max(epsilon_end, epsilon * epsilon_decay)

            # Record
            self.training_history["rewards"].append(total_reward)
            self.training_history["losses"].append(episode_loss / (step + 1))

            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.training_history["rewards"][-10:])
                logger.info(
                    f"Episode {episode + 1}/{episodes}: Avg Reward={avg_reward:.2f}, Epsilon={epsilon:.3f}"
                )

    def get_training_history(self) -> dict:
        """Get training history."""
        return self.training_history


class SimpleEnvironment:
    """
    Simple test environment for quantum RL.

    Goal: Reach target state by taking actions.
    """

    def __init__(self, n_states: int = 4, n_actions: int = 2):
        """Initialize environment."""
        self.n_states = n_states
        self.n_actions = n_actions
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset environment."""
        self.state = np.zeros(self.n_states)
        self.state[0] = 1.0  # Start at first position
        self.steps = 0
        return self.state.copy()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Take action in environment.

        Returns:
            next_state, reward, done, info
        """
        self.steps += 1

        # Move state based on action
        current_pos = np.argmax(self.state)

        if action == 0 and current_pos > 0:
            # Move left
            self.state[current_pos] = 0
            self.state[current_pos - 1] = 1
        elif action == 1 and current_pos < self.n_states - 1:
            # Move right
            self.state[current_pos] = 0
            self.state[current_pos + 1] = 1

        # Reward: +1 for reaching goal (last state), -0.1 per step
        reward = -0.1
        done = False

        if np.argmax(self.state) == self.n_states - 1:
            reward = 1.0
            done = True

        if self.steps >= 20:
            done = True

        return self.state.copy(), reward, done, {}
