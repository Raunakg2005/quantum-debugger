"""
Quantum Policy Gradient (REINFORCE)

A policy-based quantum reinforcement learning algorithm. The policy is a
parameterized quantum circuit: the state is angle-encoded, a variational ansatz
is applied, and the per-action Pauli-Z expectation values are turned into action
probabilities with a softmax. The policy is trained with the REINFORCE estimator
using exact parameter-shift gradients of the circuit outputs -- no finite
differences, no classical surrogate.
"""

import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class QuantumPolicyGradient:
    """
    REINFORCE with a parameterized-quantum-circuit policy.

    Examples:
        >>> from quantum_debugger.qml.algorithms import SimpleEnvironment
        >>> env = SimpleEnvironment(n_states=4, n_actions=2)
        >>> agent = QuantumPolicyGradient(n_qubits=4, n_actions=2, n_layers=2)
        >>> agent.train(env, episodes=100)
        >>> action = agent.select_action(env.reset(), greedy=True)
    """

    def __init__(
        self,
        n_qubits: int,
        n_actions: int,
        n_layers: int = 2,
        learning_rate: float = 0.1,
        gamma: float = 0.99,
    ):
        if n_actions > n_qubits:
            raise ValueError(
                "n_actions must be <= n_qubits (one readout qubit per action)"
            )
        self.n_qubits = n_qubits
        self.n_actions = n_actions
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self.gamma = gamma

        self.params = np.random.uniform(0, 2 * np.pi, n_layers * n_qubits)
        self.training_history = {"rewards": [], "losses": []}

    # ------------------------------------------------------------------
    # Policy circuit
    # ------------------------------------------------------------------
    def _logits(self, state: np.ndarray, params: np.ndarray) -> np.ndarray:
        """Per-action Pauli-Z expectations <Z_a> from the policy circuit."""
        from ...core.circuit import QuantumCircuit

        state = np.asarray(state, dtype=float).ravel()
        circuit = QuantumCircuit(self.n_qubits)

        # Angle-encode the state (one feature per qubit).
        for q in range(self.n_qubits):
            angle = np.pi * state[q] if q < state.shape[0] else 0.0
            circuit.ry(float(angle), q)

        # Variational ansatz.
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)

        sv = circuit.get_statevector().state_vector
        probs = np.abs(sv) ** 2
        indices = np.arange(sv.shape[0])
        return np.array(
            [
                np.dot(probs, 1.0 - 2.0 * ((indices >> a) & 1))
                for a in range(self.n_actions)
            ]
        )

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        z = logits - np.max(logits)
        e = np.exp(z)
        return e / np.sum(e)

    def policy(self, state: np.ndarray) -> np.ndarray:
        """Action probability distribution pi(.|state)."""
        return self._softmax(self._logits(state, self.params))

    def select_action(self, state: np.ndarray, greedy: bool = False) -> int:
        probs = self.policy(state)
        if greedy:
            return int(np.argmax(probs))
        return int(np.random.choice(self.n_actions, p=probs))

    def _logits_jacobian(self, state: np.ndarray) -> np.ndarray:
        """d<Z_a>/d theta_j via parameter-shift. Shape (n_actions, n_params)."""
        shift = np.pi / 2
        n_params = self.params.shape[0]
        jac = np.zeros((self.n_actions, n_params))
        for j in range(n_params):
            p_plus = self.params.copy()
            p_plus[j] += shift
            p_minus = self.params.copy()
            p_minus[j] -= shift
            jac[:, j] = 0.5 * (
                self._logits(state, p_plus) - self._logits(state, p_minus)
            )
        return jac

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def _run_episode(self, env, max_steps: int) -> Tuple[List, float]:
        state = env.reset()
        trajectory = []
        total_reward = 0.0
        for _ in range(max_steps):
            probs = self.policy(state)
            action = int(np.random.choice(self.n_actions, p=probs))
            next_state, reward, done, _ = env.step(action)
            trajectory.append((np.asarray(state, dtype=float), action, reward, probs))
            total_reward += reward
            state = next_state
            if done:
                break
        return trajectory, total_reward

    def _returns(self, rewards: List[float]) -> np.ndarray:
        """Discounted returns G_t, then standardized as a baseline."""
        g = 0.0
        out = np.zeros(len(rewards))
        for t in reversed(range(len(rewards))):
            g = rewards[t] + self.gamma * g
            out[t] = g
        if len(out) > 1 and out.std() > 1e-8:
            out = (out - out.mean()) / (out.std() + 1e-8)
        return out

    def train(
        self,
        env,
        episodes: int = 100,
        max_steps: int = 20,
    ):
        """
        Train the policy with REINFORCE.

        For each episode the gradient of the expected return w.r.t. the circuit
        parameters is grad J = sum_t G_t * grad log pi(a_t|s_t), where
        grad log pi(a|s) = sum_k (onehot(a)_k - pi_k) * d<Z_k>/d theta, and the
        d<Z_k>/d theta are exact parameter-shift derivatives. Parameters are
        updated by gradient ascent.
        """
        for episode in range(episodes):
            trajectory, total_reward = self._run_episode(env, max_steps)
            rewards = [r for (_, _, r, _) in trajectory]
            returns = self._returns(rewards)

            grad = np.zeros_like(self.params)
            loss = 0.0
            for (state, action, _, probs), g_t in zip(trajectory, returns):
                jac = self._logits_jacobian(state)  # (n_actions, n_params)
                onehot = np.zeros(self.n_actions)
                onehot[action] = 1.0
                # d log pi_a / d theta = (onehot - pi) . d logits / d theta
                dlogp = (onehot - probs) @ jac
                grad += g_t * dlogp
                loss -= g_t * np.log(probs[action] + 1e-8)

            # Gradient ascent on expected return.
            self.params += self.learning_rate * grad

            self.training_history["rewards"].append(total_reward)
            self.training_history["losses"].append(float(loss))

            if (episode + 1) % 10 == 0:
                avg = np.mean(self.training_history["rewards"][-10:])
                logger.info(f"Episode {episode + 1}/{episodes}: avg reward={avg:.2f}")

        return self

    def get_training_history(self) -> dict:
        return self.training_history
