# Ansätze Library

## Overview

The ansatz module provides variational circuit templates for quantum machine learning applications. These pre-built circuits serve as parameterized trial wavefunctions for algorithms such as VQE (Variational Quantum Eigensolver) and QAOA (Quantum Approximate Optimization Algorithm).

## Available Ansätze

### RealAmplitudes

A hardware-efficient ansatz using only RY rotations, producing quantum states with real-valued amplitudes.

**Features:**
- Uses only RY rotation gates
- Configurable entanglement patterns
- Efficient for near-term quantum hardware
- Produces real-valued state vectors

**Parameters:**
- `num_qubits` (int): Number of qubits in the circuit
- `reps` (int): Number of repetitions of the ansatz structure
- `entanglement` (str): Pattern of CNOT gates ('linear', 'full', 'circular')

**Example:**
```python
from quantum_debugger.qml.ansatz import real_amplitudes
import numpy as np

# Create ansatz for 4 qubits with 2 repetitions
ansatz = real_amplitudes(num_qubits=4, reps=2, entanglement='linear')

# Generate random parameters
params = np.random.uniform(0, 2*np.pi, ansatz.num_parameters)

# Build circuit
circuit = ansatz(params)
```

**Parameter Count:** `(reps + 1) × num_qubits`

---

### TwoLocal

Highly customizable ansatz with alternating rotation and entanglement layers.

**Features:**
- Customizable single-qubit rotation gates
- Configurable two-qubit entanglement gates
- Flexible entanglement topology
- Supports mixed rotation types

**Parameters:**
- `num_qubits` (int): Number of qubits
- `rotation_blocks` (str or list): Single-qubit gates ('ry', 'rz', 'rx', or list)
- `entanglement_blocks` (str): Two-qubit gates ('cnot', 'cz', 'swap')
- `entanglement` (str): Connection pattern
- `reps` (int): Number of repetitions

**Example:**
```python
from quantum_debugger.qml.ansatz import two_local

# Create with mixed rotations
ansatz = two_local(
    num_qubits=3,
    rotation_blocks=['ry', 'rz'],  # Alternates between RY and RZ
    entanglement_blocks='cnot',
    entanglement='full',
    reps=2
)

params = np.random.uniform(0, 2*np.pi, ansatz.num_parameters)
circuit = ansatz(params)
```

**Parameter Count:** `(reps + 1) × num_qubits`

---

### ExcitationPreserving

Chemistry-focused ansatz that preserves the number of excitations (particle number).

**Features:**
- Conserves total number of |1⟩ states
- Designed for molecular simulations
- Uses RZ rotations and special two-qubit gates
- Ideal for fermionic systems

**Parameters:**
- `num_qubits` (int): Number of qubits
- `reps` (int): Number of repetitions
- `entanglement` (str): Connection pattern
- `skip_final_rotation` (bool): Whether to skip last rotation layer

**Example:**
```python
from quantum_debugger.qml.ansatz import excitation_preserving

# For H2 molecule (2 electrons, 4 orbitals)
ansatz = excitation_preserving(
    num_qubits=4,
    reps=2,
    entanglement='linear'
)

params = np.random.uniform(0, 2*np.pi, ansatz.num_parameters)
circuit = ansatz(params)
```

**Use Cases:**
- Molecular ground state calculations
- VQE for chemistry
- Systems with conserved quantities

---

### StronglyEntangling

Generates highly entangled states through arbitrary rotations and circular entanglement.

**Features:**
- Three rotations per qubit per layer (RZ-RY-RZ)
- Circular CNOT connectivity
- High expressiveness
- Large parameter space

**Parameters:**
- `num_qubits` (int): Number of qubits
- `reps` (int): Number of layers

**Example:**
```python
from quantum_debugger.qml.ansatz import strongly_entangling

ansatz = strongly_entangling(num_qubits=5, reps=3)
params = np.random.uniform(0, 2*np.pi, ansatz.num_parameters)
circuit = ansatz(params)
```

**Parameter Count:** `reps × num_qubits × 3`

---

## Entanglement Patterns

All ansätze support three entanglement patterns:

**Linear:**
```
0 --CNOT-- 1 --CNOT-- 2 --CNOT-- 3
```

**Full:**
```
All-to-all connectivity between qubits
```

**Circular:**
```
0 --CNOT-- 1 --CNOT-- 2 --CNOT-- 3 --CNOT-- 0
```

---

## Choosing an Ansatz

| Ansatz | Best For | Advantage | Limitation |
|--------|----------|-----------|------------|
| RealAmplitudes | General purpose | Simple, hardware-efficient | Real amplitudes only |
| TwoLocal | Flexible applications | Highly customizable | May overparameterize |
| ExcitationPreserving | Chemistry | Conserves particle number | Specific to fermionic systems |
| StronglyEntangling | Complex problems | Maximum expressiveness | Large parameter count |

---

## Integration with VQE

```python
from quantum_debugger.qml.algorithms import VQE
from quantum_debugger.qml.ansatz import excitation_preserving
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian

# Load Hamiltonian
H, E_nuc = h2_hamiltonian()

# Create ansatz
ansatz = excitation_preserving(num_qubits=2, reps=2)

# Run VQE
vqe = VQE(
    hamiltonian=H,
    ansatz=ansatz,
    optimizer='adam',
    max_iterations=100
)

result = vqe.run()
print(f"Ground state energy: {result['energy'] + E_nuc}")
```

---

## Performance Considerations

**Parameter Count:**
- Fewer parameters: Faster optimization, less expressiveness
- More parameters: Slower optimization, more expressiveness

**Circuit Depth:**
- Linear entanglement: Shallowest, best for NISQ devices
- Full entanglement: Deepest, requires high-fidelity gates
- Circular entanglement: Moderate depth

**Recommendations:**
- Start with RealAmplitudes for initial experiments
- Use ExcitationPreserving for chemistry applications
- Use TwoLocal for hardware-specific optimization
- Use StronglyEntangling for complex optimization landscapes

---

## API Reference

### Common Methods

All ansatz builder functions return a callable with these attributes:

```python
ansatz = real_amplitudes(num_qubits=3, reps=2)

# Attributes
ansatz.num_parameters  # Total number of parameters required
ansatz.num_qubits     # Number of qubits
ansatz.reps           # Number of repetitions
ansatz.entanglement   # Entanglement pattern

# Callable
circuit = ansatz(params)  # Build circuit with parameters
```

### Helper Functions

```python
from quantum_debugger.qml.ansatz.real_amplitudes import count_parameters

# Calculate parameter count without building ansatz
n_params = count_parameters(num_qubits=5, reps=3)
```

---

## Testing

Run tests for the ansatz library:

```bash
pytest tests/qml/test_ansatz_library.py -v
```

Expected: 27 tests passing

---

## References

1. Kandala et al., "Hardware-efficient variational quantum eigensolver for small molecules" (2017)
2. Sim et al., "Expressibility and entangling capability of parameterized quantum circuits" (2019)
3. Romero et al., "Strategies for quantum computing molecular energies" (2018)
