"""Tests for the Quantum Policy Gradient (REINFORCE) agent."""

import numpy as np
import pytest

from quantum_debugger.qml.algorithms import QuantumPolicyGradient, SimpleEnvironment


class TestQuantumPolicyGradient:
    def test_initialization(self):
        agent = QuantumPolicyGradient(n_qubits=4, n_actions=2, n_layers=2)
        assert agent.n_qubits == 4
        assert agent.n_actions == 2
        assert agent.params.shape[0] == 2 * 4  # n_layers * n_qubits

    def test_requires_enough_qubits(self):
        with pytest.raises(ValueError):
            QuantumPolicyGradient(n_qubits=1, n_actions=2)

    def test_policy_is_valid_distribution(self):
        agent = QuantumPolicyGradient(n_qubits=4, n_actions=2)
        state = np.array([1.0, 0.0, 0.0, 0.0])
        probs = agent.policy(state)
        assert probs.shape == (2,)
        assert np.all(probs >= 0)
        assert np.isclose(np.sum(probs), 1.0)

    def test_select_action_in_range(self):
        agent = QuantumPolicyGradient(n_qubits=4, n_actions=2)
        state = np.array([1.0, 0.0, 0.0, 0.0])
        for _ in range(10):
            assert agent.select_action(state) in (0, 1)
        assert agent.select_action(state, greedy=True) in (0, 1)

    def test_jacobian_shape(self):
        agent = QuantumPolicyGradient(n_qubits=4, n_actions=2, n_layers=2)
        jac = agent._logits_jacobian(np.array([1.0, 0.0, 0.0, 0.0]))
        assert jac.shape == (2, 2 * 4)
        assert np.all(np.isfinite(jac))

    def test_training_runs_and_records_history(self):
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumPolicyGradient(n_qubits=4, n_actions=2, n_layers=2)
        agent.train(env, episodes=8, max_steps=20)
        assert len(agent.training_history["rewards"]) == 8
        assert len(agent.training_history["losses"]) == 8
        assert all(np.isfinite(agent.training_history["rewards"]))

    def test_agent_learns(self):
        """With enough training the agent should reach the goal at least once."""
        np.random.seed(0)
        env = SimpleEnvironment(n_states=4, n_actions=2)
        agent = QuantumPolicyGradient(
            n_qubits=4, n_actions=2, n_layers=3, learning_rate=0.25, gamma=0.95
        )
        agent.train(env, episodes=150, max_steps=20)
        rewards = agent.training_history["rewards"]
        # Reaching the goal yields a positive episode reward (max ~0.8);
        # a policy that never learned would stay negative (-2.0 cap).
        assert max(rewards) > 0.0
        assert np.mean(rewards[-20:]) >= np.mean(rewards[:20]) - 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
