"""Tests for the Quantum DQN (experience replay + target network)."""

import numpy as np
import pytest

from quantum_debugger.qml.algorithms import QuantumDQN, SimpleEnvironment


class TestQuantumDQN:
    def test_initialization(self):
        agent = QuantumDQN(n_qubits=4, n_actions=2, n_layers=2)
        assert agent.params.shape[0] == 2 * (2 * 4)  # n_actions * n_layers * n_qubits
        assert np.array_equal(agent.params, agent.target_params)

    def test_q_values_shape(self):
        agent = QuantumDQN(n_qubits=4, n_actions=2)
        q = agent.get_q_values(np.array([1.0, 0.0, 0.0, 0.0]))
        assert q.shape == (2,)
        assert np.all(np.isfinite(q))

    def test_select_action_in_range(self):
        agent = QuantumDQN(n_qubits=4, n_actions=2)
        s = np.array([1.0, 0.0, 0.0, 0.0])
        assert agent.select_action(s, epsilon=0.0) in (0, 1)
        assert agent.select_action(s, epsilon=1.0) in (0, 1)

    def test_replay_needs_enough_samples(self):
        agent = QuantumDQN(n_qubits=4, n_actions=2, batch_size=16)
        # Empty buffer -> no update, zero loss.
        assert agent.replay() == 0.0

    def test_remember_and_buffer(self):
        agent = QuantumDQN(n_qubits=4, n_actions=2)
        s = np.zeros(4)
        agent.remember(s, 1, 0.5, s, False)
        assert len(agent.buffer) == 1

    def test_target_network_syncs(self):
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumDQN(n_qubits=4, n_actions=2, batch_size=4, target_update_freq=5)
        agent.train(env, episodes=6, max_steps=20)
        assert len(agent.training_history["rewards"]) == 6

    def test_agent_learns(self):
        np.random.seed(0)
        import random

        random.seed(0)
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumDQN(
            n_qubits=4, n_actions=2, n_layers=2, learning_rate=0.15, gamma=0.95
        )
        agent.train(env, episodes=80, max_steps=20)
        rewards = agent.training_history["rewards"]
        assert max(rewards) > 0.0
        assert np.mean(rewards[-15:]) >= np.mean(rewards[:15])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
