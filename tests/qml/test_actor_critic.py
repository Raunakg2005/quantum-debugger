"""Tests for the Quantum Actor-Critic (A2C) agent."""

import numpy as np
import pytest

from quantum_debugger.qml.algorithms import QuantumActorCritic, SimpleEnvironment


class TestQuantumActorCritic:
    def test_initialization(self):
        agent = QuantumActorCritic(n_qubits=4, n_actions=2, n_layers=2)
        assert agent.actor_params.shape[0] == 2 * 4
        assert agent.critic_params.shape[0] == 2 * 4

    def test_requires_enough_qubits(self):
        with pytest.raises(ValueError):
            QuantumActorCritic(n_qubits=1, n_actions=2)

    def test_policy_and_value(self):
        agent = QuantumActorCritic(n_qubits=4, n_actions=2)
        s = np.array([1.0, 0.0, 0.0, 0.0])
        probs = agent.policy(s)
        assert np.isclose(probs.sum(), 1.0)
        assert isinstance(agent._value(s, agent.critic_params), float)
        assert agent.select_action(s) in (0, 1)

    def test_training_runs(self):
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumActorCritic(n_qubits=4, n_actions=2, n_layers=2)
        agent.train(env, episodes=8, max_steps=20)
        assert len(agent.training_history["rewards"]) == 8
        assert len(agent.training_history["critic_loss"]) == 8

    def test_learns(self):
        np.random.seed(0)
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumActorCritic(
            n_qubits=4, n_actions=2, n_layers=3, actor_lr=0.2, critic_lr=0.2
        )
        agent.train(env, episodes=150, max_steps=20)
        rewards = agent.training_history["rewards"]
        assert max(rewards) > 0.0
        assert np.mean(rewards[-20:]) >= np.mean(rewards[:20]) - 0.15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
