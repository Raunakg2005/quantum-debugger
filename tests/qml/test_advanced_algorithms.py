"""
Tests for advanced algorithms: QGANs and Quantum RL
"""

import pytest
import numpy as np

from quantum_debugger.qml.algorithms import (
    QuantumGAN,
    QuantumQLearning,
    SimpleEnvironment,
)


class TestQuantumGAN:
    """Test Quantum Generative Adversarial Networks"""

    def test_qgan_initialization(self):
        """Test QGAN initialization"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2)

        assert qgan.n_qubits == 4
        assert qgan.n_layers == 2
        assert qgan.generator_params.shape[0] == 8  # layers * qubits

    def test_qgan_generator_circuit(self):
        """Test generator produces quantum states"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2)

        noise = np.random.randn(4)
        state = qgan._generator_circuit(noise)

        assert state.shape[0] == 2**4  # State vector size
        assert np.isclose(np.sum(np.abs(state) ** 2), 1.0)  # Normalized

    def test_qgan_discriminator(self):
        """Test discriminator output"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2, discriminator_type="classical")

        state = np.random.randn(2**4) + 1j * np.random.randn(2**4)
        state /= np.linalg.norm(state)

        prob = qgan._discriminator(state)

        assert 0 <= prob <= 1  # Valid probability

    def test_qgan_generate(self):
        """Test generating samples"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2)

        samples = qgan.generate(n_samples=5)

        assert samples.shape == (5, 2**4)
        for sample in samples:
            assert np.isclose(np.sum(np.abs(sample) ** 2), 1.0)

    def test_qgan_training(self):
        """Test QGAN training"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2)

        # Create fake real data
        real_data = np.random.randn(20, 2**4) + 1j * np.random.randn(20, 2**4)
        for i in range(len(real_data)):
            real_data[i] /= np.linalg.norm(real_data[i])

        # Train
        qgan.train(real_data, epochs=3, batch_size=5)

        # Check history
        assert len(qgan.training_history["generator_loss"]) == 3
        assert len(qgan.training_history["discriminator_loss"]) == 3

    def test_qgan_get_history(self):
        """Test getting training history"""
        qgan = QuantumGAN(n_qubits=4, n_layers=2)

        history = qgan.get_training_history()

        assert "generator_loss" in history
        assert "discriminator_loss" in history


class TestQuantumQLearning:
    """Test Quantum Q-Learning"""

    def test_qrl_initialization(self):
        """Test Q-Learning initialization"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2, n_layers=2)

        assert qrl.n_qubits == 4
        assert qrl.n_actions == 2
        assert qrl.n_layers == 2
        assert qrl.params.shape[0] == 16  # actions * layers * qubits

    def test_qrl_encode_state(self):
        """Test state encoding"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2)

        state = np.array([1.0, 0.5, -0.3, 0.2])
        angles = qrl._encode_state(state)

        assert len(angles) == len(state)
        assert all(np.isfinite(angles))

    def test_qrl_q_circuit(self):
        """Test Q-value circuit"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2)

        state = np.array([1.0, 0.5, -0.3, 0.2])
        q_value = qrl._q_circuit(state, action=0)

        assert isinstance(q_value, (int, float))
        assert np.isfinite(q_value)

    def test_qrl_get_q_values(self):
        """Test getting Q-values for all actions"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=3)

        state = np.random.randn(4)
        q_values = qrl.get_q_values(state)

        assert len(q_values) == 3
        assert all(np.isfinite(q_values))

    def test_qrl_choose_action(self):
        """Test action selection"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2)

        state = np.random.randn(4)

        # Greedy (epsilon=0)
        action = qrl.choose_action(state, epsilon=0.0)
        assert action in [0, 1]

        # Random (epsilon=1)
        action = qrl.choose_action(state, epsilon=1.0)
        assert action in [0, 1]

    def test_qrl_update(self):
        """Test Q-learning update"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2, learning_rate=0.01)

        state = np.random.randn(4)
        next_state = np.random.randn(4)

        td_error = qrl.update(
            state, action=0, reward=1.0, next_state=next_state, done=False
        )

        assert isinstance(td_error, (int, float))
        assert np.isfinite(td_error)

    def test_qrl_training(self):
        """Test training in environment"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2, learning_rate=0.01)
        env = SimpleEnvironment(n_states=4, n_actions=2)

        # Train for few episodes
        qrl.train(env, episodes=5, max_steps=20)

        # Check history
        assert len(qrl.training_history["rewards"]) == 5
        assert len(qrl.training_history["losses"]) == 5

    def test_qrl_get_history(self):
        """Test getting training history"""
        qrl = QuantumQLearning(n_qubits=4, n_actions=2)

        history = qrl.get_training_history()

        assert "rewards" in history
        assert "losses" in history


class TestSimpleEnvironment:
    """Test Simple RL Environment"""

    def test_env_initialization(self):
        """Test environment initialization"""
        env = SimpleEnvironment(n_states=4, n_actions=2)

        assert env.n_states == 4
        assert env.n_actions == 2

    def test_env_reset(self):
        """Test environment reset"""
        env = SimpleEnvironment(n_states=4, n_actions=2)

        state = env.reset()

        assert len(state) == 4
        assert np.isclose(state[0], 1.0)  # Start at first position
        assert np.isclose(np.sum(state), 1.0)

    def test_env_step(self):
        """Test environment step"""
        env = SimpleEnvironment(n_states=4, n_actions=2)
        env.reset()

        next_state, reward, done, info = env.step(action=1)  # Move right

        assert len(next_state) == 4
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_env_goal_reaching(self):
        """Test reaching goal gives reward"""
        env = SimpleEnvironment(n_states=4, n_actions=2)
        env.reset()

        # Move to goal (last state)
        for _ in range(3):
            next_state, reward, done, _ = env.step(action=1)

        # Should reach goal
        assert np.argmax(next_state) == 3
        assert reward == 1.0
        assert done == True

    def test_env_max_steps(self):
        """Test max steps terminates episode"""
        env = SimpleEnvironment(n_states=4, n_actions=2)
        env.reset()

        # Take many steps
        for _ in range(25):
            next_state, reward, done, _ = env.step(action=0)
            if done:
                break

        assert done == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
