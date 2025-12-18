# Parameterized Quantum Gates Tutorial

## Introduction

Parameterized quantum gates are the foundation of **Variational Quantum Algorithms** (VQAs). Unlike fixed gates (H, X, CNOT), parameterized gates have continuous parameters (usually rotation angles) that can be optimized to solve problems.

**Use Cases:**
- **VQE** (Variational Quantum Eigensolver) - Finding molecular ground states
- **QAOA** (Quantum Approximate Optimization Algorithm) - Solving combinatorial problems
- **Quantum Neural Networks** - Machine learning with quantum circuits

---

## Installation

```bash
pip install quantum-debugger
```

Or for development:
```bash
cd quantum-debugger
pip install -e .
```

---

## Basic Usage

### Importing Gates

```python
from quantum_debugger.qml import RXGate, RYGate, RZGate
import numpy as np
```

### Creating Parameterized Gates

```python
# RX gate - Rotation around X-axis
rx = RXGate(target=0, parameter=np.pi/4)

# RY gate - Rotation around Y-axis  
ry = RYGate(target=1, parameter=np.pi/3)

# RZ gate - Rotation around Z-axis (phase rotation)
rz = RZGate(target=2, parameter=np.pi/6)
```

### Getting the Unitary Matrix

```python
# Compute the 2×2 unitary matrix
U = rx.matrix()

print("RX(π/4) matrix:")
print(U)

# Output:
# [[0.92387953+0.j         0.        -0.38268343j]
#  [0.        -0.38268343j 0.92387953+0.j        ]]
```

### Updating Parameters

```python
# Change the rotation angle
rx.parameter = np.pi/2

# Matrix is automatically recomputed
U_new = rx.matrix()
```

---

## Understanding

 the Gates

### RX Gate - X-axis Rotation

The RX gate rotates a qubit around the X-axis of the Bloch sphere.

**Matrix:**
```
RX(θ) = [[ cos(θ/2),    -i*sin(θ/2) ]
         [ -i*sin(θ/2),  cos(θ/2)   ]]
```

**Effect:**
- RX(0) = Identity (no rotation)
- RX(π) = -iX (Pauli-X with phase)
- RX(π/2) = √X gate

**Example:**
```python
rx_zero = RXGate(target=0, parameter=0)
rx_pi = RXGate(target=0, parameter=np.pi)

# Verify RX(π) ≈ -iX
X = np.array([[0, 1], [1, 0]])
np.allclose(rx_pi.matrix(), -1j * X)  # True
```

### RY Gate - Y-axis Rotation

The RY gate rotates around the Y-axis, creating superpositions without complex phases.

**Matrix:**
```
RY(θ) = [[ cos(θ/2),  -sin(θ/2) ]
         [ sin(θ/2),   cos(θ/2) ]]
```

**Common Uses:**
- RY(π/2) creates |+⟩ = (|0⟩ + |1⟩)/√2
- RY(π) flips |0⟩ ↔ |1⟩

**Example:**
```python
# Create superposition
ry = RYGate(target=0, parameter=np.pi/2)
state_0 = np.array([1, 0])  # |0⟩
state_plus = ry.matrix() @ state_0

# Result: [1/√2, 1/√2]
print(state_plus)
```

### RZ Gate - Z-axis Rotation (Phase)

The RZ gate adds relative phase between |0⟩ and |1⟩ states.

**Matrix:**
```
RZ(θ) = [[ e^(-iθ/2),  0         ]
         [ 0,          e^(iθ/2)  ]]
```

**Special Cases:**
- RZ(π/2) = S gate
- RZ(π/4) = T gate
- RZ(π) = Z gate (with global phase)

**Example:**
```python
s_gate = RZGate(target=0, parameter=np.pi/2)
t_gate = RZGate(target=0, parameter=np.pi/4)
```

---

## Trainable Parameters

Mark gates as trainable for optimization:

```python
# Create trainable gate
rx_trainable = RXGate(target=0, parameter=0.5, trainable=True)

# Non-trainable (fixed) gate
rx_fixed = RXGate(target=1, parameter=np.pi/4, trainable=False)

# Check trainability
print(rx_trainable.trainable)  # True
print(rx_fixed.trainable)      # False
```

### Storing Gradients

```python
# Optimizer computes gradient
gradient = 0.123  # From parameter shift rule

# Store in gate
rx_trainable.gradient = gradient

# Use for parameter update
learning_rate = 0.1
rx_trainable.parameter -= learning_rate * gradient
```

---

## Building Variational Circuits

### Single Layer

```python
def single_layer(params):
    """Single layer: RY rotations + entanglement"""
    from quantum_debugger.circuit import QuantumCircuit
    
    circuit = QuantumCircuit(2)
    
    # Single-qubit rotations
    circuit.add(RYGate(0, params[0]))
    circuit.add(RYGate(1, params[1]))
    
    # Entanglement
    circuit.cnot(0, 1)
    
    return circuit

# Use with 2 parameters
params = np.array([0.5, 0.8])
circuit = single_layer(params)
```

### Multi-Layer Ansatz

```python
def hardware_efficient_ansatz(params, n_qubits=2, depth=2):
    """Hardware-efficient ansatz for VQE"""
    circuit = QuantumCircuit(n_qubits)
    param_idx = 0
    
    for layer in range(depth):
        # Layer of single-qubit rotations
        for q in range(n_qubits):
            circuit.add(RYGate(q, params[param_idx]))
            param_idx += 1
        
        # Entangling layer
        for q in range(n_qubits - 1):
            circuit.cnot(q, q + 1)
    
    return circuit

# 2 qubits, 2 layers = 4 parameters
params = np.random.rand(4)
circuit = hardware_efficient_ansatz(params)
```

---

## Common Patterns

### 1. Universal Single-Qubit Rotation

Any single-qubit gate can be decomposed as RZ-RY-RZ:

```python
def arbitrary_rotation(alpha, beta, gamma):
    """U = RZ(γ) RY(β) RZ(α)"""
    rz1 = RZGate(0, alpha)
    ry = RYGate(0, beta)
    rz2 = RZGate(0, gamma)
    
    # Compose: RZ2 * RY * RZ1
    U = rz2.matrix() @ ry.matrix() @ rz1.matrix()
    return U
```

### 2. Bloch Sphere Coordinates

Convert rotation parameters to Bloch sphere points:

```python
def bloch_coordinates(theta, phi):
    """Create state at (θ, φ) on Bloch sphere"""
    ry = RYGate(0, theta)
    rz = RZGate(0, phi)
    
    state_0 = np.array([1, 0])
    state = ry.matrix() @ state_0
    state = rz.matrix() @ state
    
    return state
```

### 3. Parameter Initialization

```python
# Random initialization
params = np.random.uniform(0, 2*np.pi, size=10)

# Near-zero initialization
params = np.random.normal(0, 0.1, size=10)

# Specific values
params = np.array([np.pi/4, np.pi/2, 0.5, ...])
```

---

## Verification & Debugging

### Check Unitarity

```python
rx = RXGate(target=0, parameter=0.789)
U = rx.matrix()

# U†U should equal I
identity = U.conj().T @ U
is_unitary = np.allclose(identity, np.eye(2))

print(f"Is unitary: {is_unitary}")  # True
```

### Check Determinant

```python
det = np.linalg.det(U)
print(f"|det(U)| = {np.abs(det):.10f}")  # Should be 1.0
```

### Verify Special Angles

```python
# Test RX(0) = I
rx_zero = RXGate(0, 0)
assert np.allclose(rx_zero.matrix(), np.eye(2))

# Test RX(2π) = I (up to global phase)
rx_2pi = RXGate(0, 2*np.pi)
# May have phase factor e^(iφ)
```

---

## Next Steps

1. **VQE Tutorial** - Use these gates to find molecular ground states
2. **QAOA Tutorial** - Solve optimization problems
3. **Training Tutorial** - Optimize parameters with gradient descent

---

## Full Example

```python
from quantum_debugger.qml import RXGate, RYGate, RZGate
import numpy as np

def example_variational_circuit():
    """Complete example of building and using parameterized circuit"""
    
    # Create gates
    gates = [
        RYGate(target=0, parameter=np.pi/4, trainable=True),
        RYGate(target=1, parameter=np.pi/3, trainable=True),
        RXGate(target=0, parameter=0.5, trainable=True),
        RZGate(target=1, parameter=0.8, trainable=True),
    ]
    
    # Get matrices
    print("Gate matrices:")
    for gate in gates:
        print(f"{gate.name}(θ={gate.parameter:.4f}):")
        print(gate.matrix())
        print()
    
    # Simulate parameter update
    print("Updating parameters...")
    for gate in gates:
        if gate.trainable:
            gate.gradient = np.random.rand()  # Simulated gradient
            gate.parameter -= 0.1 * gate.gradient
            print(f"{gate.name}: θ = {gate.parameter:.4f}")

if __name__ == "__main__":
    example_variational_circuit()
```

---

**Ready to learn more?** Check out:
- [VQE Preparation Tutorial](vqe_preparation.md)
- [QAOA Preparation Tutorial](qaoa_preparation.md)
- [Examples Directory](../examples/)
