# Quantum Reinforcement Learning

`quantum_debugger.qml.algorithms` provides quantum RL agents whose policies /
value functions are parameterized quantum circuits, trained with exact
parameter-shift gradients. All work with the bundled `SimpleEnvironment` (a
gridworld) or any environment exposing `reset()` and `step(action)`.

```python
from quantum_debugger.qml.algorithms import (
    SimpleEnvironment, QuantumQLearning, QuantumDQN, QuantumPolicyGradient,
)

env = SimpleEnvironment(n_states=4, n_actions=2)
```

## Quantum Q-Learning

Tabular-style Q-learning with a PQC Q-function.

```python
agent = QuantumQLearning(n_qubits=4, n_actions=2, n_layers=2)
agent.train(env, episodes=60)
action = agent.choose_action(env.reset(), epsilon=0.0)
```

## Quantum DQN

Adds the two ingredients that stabilise deep Q-learning: an **experience replay**
buffer and a periodically-synced **target network**. Converges faster and more
stably than plain Q-learning.

```python
agent = QuantumDQN(
    n_qubits=4, n_actions=2, n_layers=2,
    batch_size=16, target_update_freq=10,
)
agent.train(env, episodes=80)
agent.select_action(env.reset(), epsilon=0.0)   # greedy
```

## Quantum Policy Gradient (REINFORCE)

A policy-based agent: the PQC outputs per-action `<Z>` values which are softmaxed
into action probabilities and trained with the REINFORCE estimator using exact
parameter-shift policy gradients.

```python
agent = QuantumPolicyGradient(n_qubits=4, n_actions=2, n_layers=3, learning_rate=0.25)
agent.train(env, episodes=150)
agent.select_action(env.reset(), greedy=True)
agent.policy(env.reset())        # action probability distribution
```

## Excited States: VQD

Variational Quantum Deflation finds excited states (not just the ground state) of
a Hamiltonian by penalising overlap with previously found eigenstates.

```python
import numpy as np
from quantum_debugger.qml.algorithms import VQD

H = np.diag([0.0, 1.0, 2.0, 3.0]).astype(complex)
vqd = VQD(H, num_qubits=2, n_states=3)
result = vqd.run()
result["energies"]               # ~[0, 1, 2]
vqd.exact_spectrum()             # exact eigenvalues for comparison
```
