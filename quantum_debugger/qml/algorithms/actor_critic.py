"""
Quantum Actor-Critic (A2C)

An online advantage actor-critic agent with two parameterized quantum circuits:

- the **actor** is a PQC policy (per-action <Z> -> softmax), and
- the **critic** is a PQC state-value function V(s) = <Z_0>.

At each step the TD error delta = r + gamma * V(s') - V(s) serves both as the
critic's regression signal and as the advantage that weights the actor's policy
gradient. All gradients are exact parameter-shift derivatives.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class QuantumActorCritic:
    """
    Advantage actor-critic with PQC actor and critic.

    Examples:
        >>> from quantum_debugger.qml.algorithms import SimpleEnvironment
        >>> env = SimpleEnvironment(n_states=4, n_actions=2)
        >>> agent = QuantumActorCritic(n_qubits=4, n_actions=2, n_layers=2)
        >>> agent.train(env, episodes=150)
    """

    def __init__(
        self,
        n_qubits: int,
        n_actions: int,
        n_layers: int = 2,
        actor_lr: float = 0.1,
        critic_lr: float = 0.1,
        gamma: float = 0.95,
    ):
        if n_actions > n_qubits:
            raise ValueError("n_actions must be <= n_qubits")
        self.n_qubits = n_qubits
        self.n_actions = n_actions
        self.n_layers = n_layers
        self.actor_lr = actor_lr
        self.critic_lr = critic_lr
        self.gamma = gamma

        n = n_layers * n_qubits
        self.actor_params = np.random.uniform(0, 2 * np.pi, n)
        self.critic_params = np.random.uniform(0, 2 * np.pi, n)
        self.training_history = {"rewards": [], "critic_loss": []}

    def _circuit_state(self, state, params):
        from ...core.circuit import QuantumCircuit

        state = np.asarray(state, dtype=float).ravel()
        circuit = QuantumCircuit(self.n_qubits)
        for q in range(self.n_qubits):
            angle = np.pi * state[q] if q < state.shape[0] else 0.0
            circuit.ry(float(angle), q)
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)
        return circuit.get_statevector().state_vector

    def _z_expectations(self, sv, n_out):
        probs = np.abs(sv) ** 2
        idx = np.arange(sv.shape[0])
        return np.array(
            [np.dot(probs, 1.0 - 2.0 * ((idx >> a) & 1)) for a in range(n_out)]
        )

    def _logits(self, state, params):
        return self._z_expectations(self._circuit_state(state, params), self.n_actions)

    def _value(self, state, params):
        return float(self._z_expectations(self._circuit_state(state, params), 1)[0])

    @staticmethod
    def _softmax(x):
        e = np.exp(x - np.max(x))
        return e / np.sum(e)

    def policy(self, state):
        return self._softmax(self._logits(state, self.actor_params))

    def select_action(self, state, greedy=False):
        probs = self.policy(state)
        return (
            int(np.argmax(probs))
            if greedy
            else int(np.random.choice(self.n_actions, p=probs))
        )

    def _logits_jacobian(self, state):
        shift = np.pi / 2
        n = self.actor_params.shape[0]
        jac = np.zeros((self.n_actions, n))
        for j in range(n):
            pp = self.actor_params.copy()
            pp[j] += shift
            pm = self.actor_params.copy()
            pm[j] -= shift
            jac[:, j] = 0.5 * (self._logits(state, pp) - self._logits(state, pm))
        return jac

    def _value_gradient(self, state):
        shift = np.pi / 2
        n = self.critic_params.shape[0]
        grad = np.zeros(n)
        for j in range(n):
            pp = self.critic_params.copy()
            pp[j] += shift
            pm = self.critic_params.copy()
            pm[j] -= shift
            grad[j] = 0.5 * (self._value(state, pp) - self._value(state, pm))
        return grad

    def train(self, env, episodes: int = 150, max_steps: int = 20):
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0.0
            critic_loss = 0.0

            for _ in range(max_steps):
                probs = self.policy(state)
                action = int(np.random.choice(self.n_actions, p=probs))
                next_state, reward, done, _ = env.step(action)

                v_s = self._value(state, self.critic_params)
                v_next = 0.0 if done else self._value(next_state, self.critic_params)
                delta = reward + self.gamma * v_next - v_s  # advantage / TD error
                critic_loss += delta**2

                # Critic: move V(s) toward (reward + gamma V(s')).
                self.critic_params += (
                    self.critic_lr * delta * self._value_gradient(state)
                )

                # Actor: advantage-weighted policy gradient.
                onehot = np.zeros(self.n_actions)
                onehot[action] = 1.0
                dlogp = (onehot - probs) @ self._logits_jacobian(state)
                self.actor_params += self.actor_lr * delta * dlogp

                total_reward += reward
                state = next_state
                if done:
                    break

            self.training_history["rewards"].append(total_reward)
            self.training_history["critic_loss"].append(critic_loss)
            if (episode + 1) % 10 == 0:
                avg = np.mean(self.training_history["rewards"][-10:])
                logger.info(f"Episode {episode + 1}/{episodes}: avg reward={avg:.2f}")

        return self

    def get_training_history(self) -> dict:
        return self.training_history
