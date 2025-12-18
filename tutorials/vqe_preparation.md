# VQE Preparation Tutorial - Using Parameterized Gates

## What is VQE?

**Variational Quantum Eigensolver (VQE)** is a hybrid quantum-classical algorithm that finds the ground state energy of molecules. It's one of the most important near-term quantum algorithms.

**Key Idea:** Use a parameterized quantum circuit (ansatz) to prepare trial quantum states, then classically optimize the parameters to minimize the energy expectation value.

**Applications:**
- Quantum chemistry (drug discovery)
- Material science
- Condensed matter physics

---

## The VQE Algorithm

```
1. Choose an ansatz (parameterized circuit)
2. Initialize parameters θ
3. Prepare state |ψ(θ)⟩ using ansatz
4. Measure energy E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
5. Classical optimizer updates θ to minimize E(θ)
6. Repeat until convergence
```

---

## Prerequisites

```python
from quantum_debugger.qml import RXGate, RYGate, RZGate
import numpy as np
```

---

## Step 1: Build an Ansatz

An **ansatz** is a parameterized quantum circuit that can represent your target state.

### Hardware-Efficient Ansatz

```python
def hardware_efficient_ansatz(params, num_qubits=2):
    """
    Hardware-efficient ansatz using RY gates and CNOTs.
    
    Args:
        params: Array of rotation angles [θ₀, θ₁, ..., θₙ]
        num_qubits: Number of qubits
        
    Returns:
        List of gates forming the ansatz
    """
    gates = []
    param_idx = 0
    
    # Layer 1: Single-qubit rotations
    for q in range(num_qubits):
        gates.append(RYGate(target=q, parameter=params[param_idx], trainable=True))
        param_idx += 1
    
    # Entanglement layer (CNOTs handled by circuit)
    # For now, we focus on the parameterized gates
    
    # Layer 2: More rotations
    for q in range(num_qubits):
        gates.append(RXGate(target=q, parameter=params[param_idx], trainable=True))
        param_idx += 1
    
    return gates

# Example: 2 qubits = 4 parameters
params = np.array([0.5, 0.8, 0.3, 0.7])
ansatz_gates = hardware_efficient_ansatz(params, num_qubits=2)
```

### UCC Ansatz (Chemistry-Inspired)

```python
def ucc_singles_ansatz(params):
    """
    Unitary Coupled Cluster Singles ansatz.
    Good for molecular ground states.
    """
    gates = []
    
    # Single excitations: RY rotations
    for i, theta in enumerate(params):
        gates.append(RYGate(target=i, parameter=theta, trainable=True))
    
    return gates
```

---

## Step 2: Define a Hamiltonian

The Hamiltonian H describes the system's energy operator.

### H₂ Molecule (Hydrogen)

```python
def h2_hamiltonian():
    """
    Simplified 2-qubit Hamiltonian for H₂ molecule.
    
    H = g₀·I⊗I + g₁·I⊗Z + g₂·Z⊗I + g₃·Z⊗Z + g₄·X⊗X
    
    Coefficients from quantum chemistry calculations.
    """
    # Pauli matrices
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    Z = np.array([[1, 0], [0, -1]])
    
    # Coefficients (in Hartree units)
    g0 = -1.0523732
    g1 =  0.39793742
    g2 = -0.39793742
    g3 = -0.01128010
    g4 =  0.18093120
    
    # Build Hamiltonian
    H = (g0 * np.kron(I, I) +
         g1 * np.kron(I, Z) +
         g2 * np.kron(Z, I) +
         g3 * np.kron(Z, Z) +
         g4 * np.kron(X, X))
    
    return H

# Expected ground state energy: -1.857 Hartree
```

### LiH Molecule

```python
def lih_hamiltonian():
    """4-qubit Hamiltonian for LiH"""
    # More complex, but same idea
    # Pauli string decomposition
    pass
```

---

## Step 3: Energy Expectation Value

Compute ⟨ψ(θ)|H|ψ(θ)⟩

```python
def energy_expectation(params, hamiltonian, ansatz_builder):
    """
    Compute energy expectation value.
    
    E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
    
    Args:
        params: Circuit parameters
        hamiltonian: Hamiltonian matrix
        ansatz_builder: Function that builds ansatz from params
        
    Returns:
        Energy expectation value (real number)
    """
    # Build ansatz circuit
    gates = ansatz_builder(params)
    
    # Apply gates to |0...0⟩ state
    num_qubits = int(np.log2(hamiltonian.shape[0]))
    state = np.zeros(2**num_qubits)
    state[0] = 1.0  # |00...0⟩
    
    # Apply all gates (simplified - in practice use circuit)
    for gate in gates:
        # This is simplified; real implementation would handle multi-qubit
        matrix = gate.matrix()
        # Apply to specific qubit...
        pass
    
    # Compute expectation
    energy = np.real(state.conj() @ hamiltonian @ state)
    
    return energy
```

---

## Step 4: Optimization Loop

### Using SciPy Optimizer

```python
from scipy.optimize import minimize

def vqe_scipy(hamiltonian, ansatz_builder, initial_params):
    """
    Run VQE using SciPy's COBYLA optimizer.
    
    Args:
        hamiltonian: System Hamiltonian
        ansatz_builder: Function to build ansatz
        initial_params: Starting parameter values
        
    Returns:
        Optimization result with ground state energy
    """
    history = []
    
    def cost_function(params):
        """Cost = Energy expectation"""
        energy = energy_expectation(params, hamiltonian, ansatz_builder)
        history.append(energy)
        return energy
    
    # Optimize
    result = minimize(
        fun=cost_function,
        x0=initial_params,
        method='COBYLA',
        options={'maxiter': 100}
    )
    
    return {
        'optimal_params': result.x,
        'ground_state_energy': result.fun,
        'iterations': len(history),
        'history': history,
        'success': result.success
    }

# Run VQE
H = h2_hamiltonian()
initial_params = np.random.rand(4)  # Random initialization

result = vqe_scipy(H, hardware_efficient_ansatz, initial_params)

print(f"Ground state energy: {result['ground_state_energy']:.6f} Hartree")
print(f"Exact value: -1.857275 Hartree")
print(f"Error: {abs(result['ground_state_energy'] + 1.857275):.6f}")
```

---

## Step 5: Observable Measurement

For real quantum hardware, we measure Pauli expectation values.

### Measuring ⟨Z⟩

```python
def measure_pauli_z(circuit, qubit, shots=1000):
    """
    Measure expectation value of Z operator.
    
    ⟨Z⟩ = P(0) - P(1)
    """
    # Run circuit
    results = circuit.run(shots=shots)
    
    # Count 0s and 1s for target qubit
    counts_0 = sum(1 for r in results if r[qubit] == 0)
    counts_1 = shots - counts_0
    
    # Expectation
    expectation = (counts_0 - counts_1) / shots
    
    return expectation
```

### Measuring ⟨X⟩

```python
def measure_pauli_x(circuit, qubit, shots=1000):
    """
    Measure X by rotating to Z basis first.
    
    Insert RY(-π/2) before measurement.
    """
    # Add basis rotation
    circuit.add(RYGate(qubit, -np.pi/2))
    
    # Measure in Z basis
    return measure_pauli_z(circuit, qubit, shots)
```

---

## Complete VQE Example

```python
def run_vqe_h2():
    """
    Complete VQE example for H₂ molecule.
    """
    print("VQE for H₂ Molecule")
    print("=" * 50)
    
    # 1. Define Hamiltonian
    H = h2_hamiltonian()
    print(f"Hamiltonian shape: {H.shape}")
    
    # 2. Choose ansatz
    def ansatz(params):
        return hardware_efficient_ansatz(params, num_qubits=2)
    
    # 3. Initialize parameters
    np.random.seed(42)
    initial_params = np.random.rand(4) * 0.1
    print(f"Initial parameters: {initial_params}")
    
    # 4. Run VQE
    result = vqe_scipy(H, ansatz, initial_params)
    
    # 5. Results
    print(f"\nResults:")
    print(f"  Ground state energy: {result['ground_state_energy']:.6f} Hartree")
    print(f"  Optimal parameters: {result['optimal_params']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Converged: {result['success']}")
    
    # 6. Plot convergence
    import matplotlib.pyplot as plt
    plt.plot(result['history'])
    plt.xlabel('Iteration')
    plt.ylabel('Energy (Hartree)')
    plt.title('VQE Convergence for H₂')
    plt.grid(True)
    plt.show()
    
    return result

if __name__ == "__main__":
    result = run_vqe_h2()
```

---

## Tips for Better VQE Results

### 1. Good Parameter Initialization

```python
# Strategy 1: Small random values
params = np.random.normal(0, 0.1, size=n_params)

# Strategy 2: Hartree-Fock inspired
params = np.zeros(n_params)
params[0] = np.pi  # Excitation

# Strategy 3: Layer-by-layer
# Start with 1 layer, optimize, then add more
```

### 2. Better Optimizers

```python
# Gradient-based (use parameter shift rule)
from scipy.optimize import minimize

result = minimize(
    cost_function,
    x0=initial_params,
    method='L-BFGS-B',  # Gradient-based
    jac=gradient_function  # Provide gradients
)

# SPSA - good for noisy environments
# ADAM - adaptive learning rates
```

### 3. Ansatz Selection

```python
# For 2-qubit H₂: 2-4 parameters sufficient
# For 4-qubit LiH: 8-12 parameters
# Rule of thumb: ~2-3 params per qubit
```

---

## Next Steps

**Week 2 Implementation:**
1. Complete VQE class
2. Automatic gradient computation
3. Multiple Hamiltonian support
4. Convergence monitoring

**Try it yourself:**
1. Implement the energy expectation function
2. Test with H₂ Hamiltonian
3. Compare with exact diagonalization
4. Experiment with different ansätze

---

## Resources

- **Quantum Chemistry:** Understanding molecular Hamiltonians
- **Optimization:** Classical optimization methods
- **Parameter Shift Rule:** Computing quantum gradients
- **Ansatz Design:** Choosing effective circuit structures

---

**Next:** [QAOA Preparation Tutorial](qaoa_preparation.md)
