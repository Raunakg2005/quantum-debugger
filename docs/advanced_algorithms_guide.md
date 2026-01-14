# Advanced Algorithms Guide

Documentation for Quantum GANs and Quantum Reinforcement Learning.

## Quantum Generative Adversarial Networks (QGANs)

### Overview

Quantum GANs use quantum circuits to generate quantum states through adversarial training.

**Applications:**
- Generate quantum states
- Data augmentation
- Anomaly detection
- Quantum state preparation

### Quick Start

```python
from quantum_debugger.qml.algorithms import QuantumGAN
import numpy as np

# Create QGAN
qgan = QuantumGAN(n_qubits=4, n_layers=3)

# Prepare real quantum states (training data)
real_states = np.random.randn(100, 2**4) + 1j * np.random.randn(100, 2**4)
for i in range(len(real_states)):
    real_states[i] /= np.linalg.norm(real_states[i])

# Train
qgan.train(real_states, epochs=50, batch_size=16)

# Generate new quantum states
generated_states = qgan.generate(n_samples=10)
```

### Parameters

**QuantumGAN(n_qubits, n_layers, discriminator_type)**

- `n_qubits`: Number of qubits in generator circuit
- `n_layers`: Number of variational layers
- `discriminator_type`: 'classical' or 'quantum'

### Training

```python
qgan.train(
    real_data,           # Real quantum states
    epochs=50,           # Training epochs
    batch_size=16,       # Batch size
    learning_rate=0.01   # Learning rate
)

# Monitor training
history = qgan.get_training_history()
print(f"Generator loss: {history['generator_loss']}")
print(f"Discriminator loss: {history['discriminator_loss']}")
```

### Generation

```python
# Generate fake quantum states
fake_states = qgan.generate(n_samples=50)

# Each state is normalized
assert all(np.isclose(np.linalg.norm(s), 1.0) for s in fake_states)
```

---

## Quantum Reinforcement Learning

### Overview

Uses quantum circuits to approximate Q-functions for reinforcement learning.

**Applications:**
- Game playing
- Robot control
- Optimization problems
- Decision making

### Quick Start

```python
from quantum_debugger.qml.algorithms import QuantumQLearning, SimpleEnvironment

# Create agent
agent = QuantumQLearning(
    n_qubits=4,
    n_actions=2,
    learning_rate=0.01,
    gamma=0.99
)

# Create environment
env = SimpleEnvironment(n_states=4, n_actions=2)

# Train
agent.train(env, episodes=100)

# Use trained agent
state = env.reset()
action = agent.choose_action(state, epsilon=0.1)
```

### Parameters

**QuantumQLearning(n_qubits, n_actions, n_layers, learning_rate, gamma)**

- `n_qubits`: Number of qubits for state encoding
- `n_actions`: Number of possible actions
- `n_layers`: Variational layers in Q-circuit
- `learning_rate`: Learning rate for updates
- `gamma`: Discount factor (0-1)

### Training

```python
agent.train(
    env,                     # Environment
    episodes=100,            # Number of episodes
    max_steps=200,           # Max steps per episode
    epsilon_start=1.0,       # Initial exploration
    epsilon_end=0.01,        # Final exploration
    epsilon_decay=0.995      # Decay rate
)

# Monitor progress
history = agent.get_training_history()
print(f"Rewards: {history['rewards']}")
print(f"Losses: {history['losses']}")
```

### Action Selection

```python
# Epsilon-greedy policy
action = agent.choose_action(state, epsilon=0.1)

# Greedy (exploit only)
action = agent.choose_action(state, epsilon=0.0)

# Get Q-values for all actions
q_values = agent.get_q_values(state)
best_action = np.argmax(q_values)
```

### Custom Environment

```python
class MyEnvironment:
    def reset(self):
        """Reset environment, return initial state."""
        return np.zeros(4)
    
    def step(self, action):
        """
        Take action, return (next_state, reward, done, info).
        """
        next_state = self.state + action
        reward = -np.linalg.norm(next_state)  # Minimize distance
        done = reward > -0.1
        return next_state, reward, done, {}
```

---

## Performance Tips

### QGANs

1. **Start small** - Use 2-4 qubits initially
2. **Batch size** - 8-32 works well
3. **Epochs** - 50-100 for convergence
4. **Monitor losses** - Both should stabilize

### Quantum RL

1. **State encoding** - Keep states normalized
2. **Epsilon decay** - Start high (1.0), end low (0.01)
3. **Episodes** - 100-500 for simple tasks
4. **Learning rate** - 0.001-0.01

---

## Examples

### QGAN: State Preparation

```python
# Target: Create specific quantum state
target_state = np.array([1, 0, 0, 1]) / np.sqrt(2)

# Train QGAN
qgan = QuantumGAN(n_qubits=2, n_layers=2)
qgan.train([target_state] * 50, epochs=30)

# Generate similar states
generated = qgan.generate(n_samples=10)
```

### Quantum RL: Grid Navigation

```python
class GridWorld:
    def __init__(self, size=4):
        self.size = size
        self.reset()
    
    def reset(self):
        self.pos = 0
        state = np.zeros(self.size)
        state[0] = 1
        return state
    
    def step(self, action):
        # 0: left, 1: right
        if action == 1 and self.pos < self.size - 1:
            self.pos += 1
        elif action == 0 and self.pos > 0:
            self.pos -= 1
        
        state = np.zeros(self.size)
        state[self.pos] = 1
        
        # Reward for reaching goal
        reward = 1.0 if self.pos == self.size - 1 else -0.1
        done = self.pos == self.size - 1
        
        return state, reward, done, {}

# Train agent
agent = QuantumQLearning(n_qubits=4, n_actions=2)
env = GridWorld()
agent.train(env, episodes=200)
```

---

## References

- **QGANs:** Generative adversarial networks for quantum state preparation
- **Quantum RL:** Quantum approximate optimization for reinforcement learning

## See Also

- [QNN Guide](qnn_guide.md) - Quantum Neural Networks
- [VQE Guide](vqe_guide.md) - Variational Quantum Eigensolver
- [QAOA Guide](qaoa_guide.md) - Quantum Approximate Optimization
