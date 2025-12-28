# Advanced Optimizers Guide

## Overview

The advanced optimizers module provides sophisticated optimization algorithms for quantum variational algorithms. These optimizers complement basic gradient descent with specialized techniques for quantum optimization landscapes.

## Available Optimizers

### Quantum Natural Gradient (QNG)

Uses the quantum Fisher information metric to precondition gradients, accounting for the geometry of the quantum state space.

**Theory:**

Natural gradient descent follows the steepest descent direction in the parameter space when equipped with the quantum geometric tensor (Fubini-Study metric):

```
θₙₑw = θ - η · F⁻¹ · ∇L(θ)
```

Where F is the quantum Fisher information matrix.

**Advantages:**
- Faster convergence on quantum optimization landscapes
- Accounts for parameter reparametrization invariance
- Reduces barren plateau effects

**Usage:**
```python
from quantum_debugger.qml.optimizers.advanced import QuantumNaturalGradient

qng = QuantumNaturalGradient(
    learning_rate=0.01,
    epsilon=1e-8
)

# In optimization loop
for iteration in range(max_iterations):
    gradient = compute_gradient(params)
    params = qng.step(params, gradient, circuit_function)
```

**Parameters:**
- `learning_rate` (float): Step size, typically 0.001-0.1
- `epsilon` (float): Numerical stability constant

**Computational Cost:** O(n²) for n parameters (metric tensor inversion)

---

### Nelder-Mead

Gradient-free simplex optimization method. Robust to noisy cost functions.

**Theory:**

Maintains a simplex of n+1 points in n-dimensional parameter space. Iteratively:
1. Reflects worst point through centroid
2. Expands or contracts based on improvement
3. Shrinks simplex if no improvement

**Advantages:**
- No gradient computation required
- Robust to noise
- Works with non-differentiable functions
- Good for small-dimensional problems (< 20 parameters)

**Usage:**
```python
from quantum_debugger.qml.optimizers.advanced import NelderMeadOptimizer

nm = NelderMeadOptimizer(
    max_iterations=1000,
    tolerance=1e-6
)

result = nm.minimize(
    cost_function=cost_fn,
    initial_params=initial_guess
)

optimal_params = result['params']
optimal_cost = result['cost']
```

**Parameters:**
- `max_iterations` (int): Maximum function evaluations
- `tolerance` (float): Convergence threshold

**Best For:**
- Problems with noisy gradients
- Non-differentiable cost functions
- Small parameter spaces

**Limitations:**
- Slow convergence for large parameter counts
- May get stuck in local minima

---

### L-BFGS-B

Limited-memory Broyden–Fletcher–Goldfarb–Shanno algorithm with box constraints.

**Theory:**

Quasi-Newton method that approximates the inverse Hessian using limited memory:

```
θₙₑw = θ - α · H⁻¹ · ∇L(θ)
```

Where H is approximated from recent gradient history.

**Advantages:**
- Memory-efficient: O(m·n) storage for m history steps
- Fast convergence (superlinear)
- Supports bound constraints
- Excellent for medium-scale problems (100-1000 parameters)

**Usage:**
```python
from quantum_debugger.qml.optimizers.advanced import LBFGSBOptimizer

lbfgs = LBFGSBOptimizer(
    max_iterations=1000,
    tolerance=1e-6,
    bounds=[(0, 2*np.pi)] * n_params  # Optional
)

result = lbfgs.minimize(
    cost_function=cost_fn,
    initial_params=initial_guess,
    gradient_function=grad_fn  # Optional
)
```

**Parameters:**
- `max_iterations` (int): Maximum iterations
- `tolerance` (float): Convergence tolerance
- `bounds` (list, optional): Parameter bounds [(min, max), ...]

**Gradient:**
- Can use analytical gradient if provided
- Otherwise uses finite differences

---

### COBYLA

Constrained Optimization BY Linear Approximation.

**Theory:**

Trust-region method that builds linear approximations of the objective and constraint functions.

**Advantages:**
- Handles constraints naturally
- Gradient-free
- Robust implementation

**Usage:**
```python
from quantum_debugger.qml.optimizers.advanced import COBYLAOptimizer

cobyla = COBYLAOptimizer(
    max_iterations=1000,
    tolerance=1e-6
)

result = cobyla.minimize(
    cost_function=cost_fn,
    initial_params=initial_guess,
    constraints=constraint_list  # Optional
)
```

**Constraints Format:**
```python
# Constraint: x[0] + x[1] ≤ 1
constraints = [
    {'type': 'ineq', 'fun': lambda x: 1 - x[0] - x[1]}
]
```

---

## Factory Function

Simplified optimizer creation:

```python
from quantum_debugger.qml.optimizers.advanced import get_optimizer

# Create by name
opt_qng = get_optimizer('qng', learning_rate=0.05)
opt_nm = get_optimizer('nelder-mead', max_iterations=500)
opt_lbfgs = get_optimizer('lbfgs', tolerance=1e-8)

# Case insensitive
opt1 = get_optimizer('L-BFGS-B')
opt2 = get_optimizer('lbfgsb')  # Same optimizer
```

**Supported Names:**
- 'qng', 'quantum-natural-gradient'
- 'nelder-mead', 'nm'
- 'lbfgs', 'lbfgsb', 'l-bfgs-b'
- 'cobyla'

---

## Optimizer Comparison

Compare multiple optimizers on the same problem:

```python
from quantum_debugger.qml.optimizers.advanced import compare_optimizers

results = compare_optimizers(
    cost_function=cost_fn,
    initial_params=initial_guess,
    optimizers=['nelder-mead', 'lbfgs', 'cobyla']
)

for opt_name, result in results.items():
    print(f"{opt_name}:")
    print(f"  Final cost: {result['cost']:.6f}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Success: {result['success']}")
```

---

## Integration with VQE

### Using QNG with VQE

```python
from quantum_debugger.qml.algorithms import VQE
from quantum_debugger.qml.ansatz import real_amplitudes
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian

H, E_nuc = h2_hamiltonian()
ansatz = real_amplitudes(num_qubits=2, reps=2)

# VQE with Quantum Natural Gradient
vqe = VQE(
    hamiltonian=H,
    ansatz=ansatz,
    optimizer='qng',  # Use QNG
    learning_rate=0.01,
    max_iterations=100
)

result = vqe.run()
```

### Using L-BFGS-B with VQE

```python
# VQE with L-BFGS-B
vqe_lbfgs = VQE(
    hamiltonian=H,
    ansatz=ansatz,
    optimizer='lbfgs',
    max_iterations=200
)

result_lbfgs = vqe_lbfgs.run()
```

---

## Choosing an Optimizer

### Decision Tree

```
Is gradient available?
├─ YES
│  ├─ Small problem (<20 params) → Quantum Natural Gradient
│  └─ Large problem (>20 params) → L-BFGS-B
└─ NO
   ├─ Small problem (<20 params) → Nelder-Mead
   └─ Large problem (>20 params) → COBYLA
```

### Comparison Table

| Optimizer | Gradient | Best For | Convergence | Memory |
|-----------|----------|----------|-------------|--------|
| QNG | Required | Quantum problems | Fast | O(n²) |
| Nelder-Mead | Free | Noisy functions | Moderate | O(n) |
| L-BFGS-B | Optional | Large-scale | Very fast | O(m·n) |
| COBYLA | Free | Constrained | Moderate | O(n) |

---

## Performance Considerations

### Function Evaluations

Typical evaluations to convergence:

- **QNG**: 50-200 iterations
- **L-BFGS-B**: 20-100 iterations
- **Nelder-Mead**: 100-500 iterations
- **COBYLA**: 100-1000 iterations

### Scaling with Parameters

| Parameters | Best Choice |
|------------|-------------|
| < 10 | Any optimizer works |
| 10-50 | QNG or Nelder-Mead |
| 50-200 | L-BFGS-B or QNG |
| > 200 | L-BFGS-B only |

---

## Hyperparameter Tuning

### Learning Rate (QNG)

Start conservative and increase:

```python
# Conservative
qng = QuantumNaturalGradient(learning_rate=0.001)

# Moderate
qng = QuantumNaturalGradient(learning_rate=0.01)

# Aggressive
qng = QuantumNaturalGradient(learning_rate=0.1)
```

### Tolerance

Balance between accuracy and runtime:

```python
# High accuracy
opt = LBFGSBOptimizer(tolerance=1e-8)

# Standard
opt = LBFGSBOptimizer(tolerance=1e-6)

# Fast convergence
opt = LBFGSBOptimizer(tolerance=1e-4)
```

---

## Common Issues and Solutions

### Issue: Slow Convergence

**Solutions:**
1. Increase learning rate (QNG)
2. Use L-BFGS-B instead of Nelder-Mead
3. Better initial parameters
4. Reduce tolerance requirement

### Issue: Optimizer Fails

**Solutions:**
1. Check gradient implementation
2. Normalize cost function
3. Use bounded optimization
4. Try gradient-free method

### Issue: Gets Stuck in Local Minimum

**Solutions:**
1. Random restart from different initial points
2. Use Nelder-Mead (more exploratory)
3. Increase simplex size (Nelder-Mead)
4. Multi-start strategy

---

## Testing

Run optimizer tests:

```bash
pytest tests/qml/test_advanced_optimizers.py -v
```

Expected: 25 tests passing

---

## API Reference

### Common Result Format

All optimizers return a dictionary:

```python
result = {
    'params': final_parameters,      # Optimal parameters found
    'cost': final_cost_value,        # Cost at optimal parameters
    'iterations': n_iterations,       # Number of iterations used
    'success': True/False,           # Whether optimization succeeded
    'message': 'status message'      # Termination reason
}
```

### QNG-Specific Methods

```python
qng = QuantumNaturalGradient()

# Single step
new_params = qng.step(params, gradient, circuit_fn)

# Metric tensor
metric = qng.compute_metric_tensor(circuit_fn, params)
```

---

## Advanced Usage

### Custom Stopping Criteria

```python
def custom_optimization(optimizer, cost_fn, initial_params):
    params = initial_params
    best_cost = float('inf')
    patience = 0
    max_patience = 10
    
    for iteration in range(1000):
        cost = cost_fn(params)
        
        if cost < best_cost - 1e-6:
            best_cost = cost
            patience = 0
        else:
            patience += 1
            
        if patience >= max_patience:
            print("Early stopping")
            break
            
        # Optimization step
        gradient = compute_gradient(params)
        params = optimizer.step(params, gradient)
    
    return params, best_cost
```

### Warm Starting

```python
# First optimization
result1 = lbfgs.minimize(cost_fn, initial_params)

# Use result as starting point for refinement
result2 = qng.minimize(cost_fn, result1['params'])
```

---

## References

1. Stokes et al., "Quantum Natural Gradient", Quantum 4, 269 (2020)
2. Nelder & Mead, "A Simplex Method for Function Minimization" (1965)
3. Liu & Nocedal, "On the Limited Memory BFGS Method" (1989)
4. Powell, "A Direct Search Optimization Method That Models the Objective" (1994)
