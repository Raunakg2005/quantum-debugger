# Zero-Noise Extrapolation (ZNE) Guide

## Overview

Zero-Noise Extrapolation (ZNE) is a quantum error mitigation technique that estimates the noise-free expectation value by running circuits at different noise levels and extrapolating to zero noise. This module provides a complete ZNE implementation for mitigating errors in quantum computations.

## Key Concepts

- **Noise Scaling**: Artificially increase noise to collect data points
- **Extrapolation**: Fit a model and extrapolate to zero noise
- **Error Mitigation**: Reduce impact of hardware noise without error correction

---

## Quick Start

### Basic ZNE Example

```python
from quantum_debugger.qml.error_mitigation import ZeroNoiseExtrapolation

# Create ZNE instance
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0],
    extrapolator='linear'
)

# Define circuit execution function
def circuit_function(noise_scale=1.0, shots=1000):
    # Your circuit execution here
    # noise_scale determines noise level
    # Return expectation value or dict with 'statevector'/'counts'
    return expectation_value

# Apply ZNE
mitigated_result = zne.execute(circuit_function, shots=1000)

# Check improvement
improvement = zne.get_improvement()
print(f"ZNE improved result by {improvement:.1f}%")
```

---

## Theory

### How ZNE Works

1. **Measure at Different Noise Levels**
   - Run circuit at noise scales λ = 1, 2, 3, ...
   - Collect expectation values E(λ)

2. **Fit a Model**
   - Fit polynomial, exponential, or linear model
   - E(λ) = a + b·λ + c·λ² + ...

3. **Extrapolate to Zero**
   - Evaluate model at λ = 0
   - E(0) ≈ ideal noise-free value

### Noise Scaling Methods

Currently supported through circuit function parameter:

```python
def circuit_with_noise_scaling(noise_scale=1.0, shots=1000):
    # Method 1: Scale noise model parameters
    noise_model.depolarizing_rate *= noise_scale
    
    # Method 2: Unitary folding (future feature)
    # Insert G·G† pairs to increase circuit depth
    
    # Execute and return
    return expectation_value
```

---

## API Reference

### ZeroNoiseExtrapolation

```python
class ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0],
    extrapolator='linear'
)
```

**Parameters:**

- `scale_factors` (list): Noise scaling factors (>= 1.0)
- `extrapolator` (str): Extrapolation method
  - `'linear'`: Linear fit
  - `'polynomial'`: Polynomial fit (degree 2)
  - `'exponential'`: Exponential decay model

**Methods:**

```python
# Execute ZNE
mitigated_value = zne.execute(
    circuit_fn,        # Circuit function
    observable=None,   # Observable operator (optional)
    shots=1000        # Measurement shots
)

# Get improvement percentage
improvement = zne.get_improvement()
```

---

## Extrapolation Methods

### Linear Extrapolation

Best for: Low noise, few scale factors.

```python
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0],
    extrapolator='linear'
)
```

Fits: E(λ) = a + b·λ

Returns: E(0) = a

### Polynomial Extrapolation

Best for: Higher noise, more scale factors.

```python
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 1.5, 2.0, 2.5, 3.0],
    extrapolator='polynomial'
)
```

Fits: E(λ) = a + b·λ + c·λ²

Returns: E(0) = a

### Exponential Extrapolation

Best for: Exponentially decaying noise.

```python
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0, 4.0],
    extrapolator='exponential'
)
```

Fits: E(λ) = a + b·exp(-c·λ)

Returns: E(0) = a + b

---

## Integration with VQE

```python
from quantum_debugger.qml import VQE, h2_hamiltonian
from quantum_debugger.qml.error_mitigation import ZeroNoiseExtrapolation

# Setup VQE
H = h2_hamiltonian()
vqe = VQE(H, ansatz, num_qubits=2)

# Create ZNE instance
zne = ZeroNoiseExtrapolation(scale_factors=[1, 2, 3])

# Wrap VQE cost function with ZNE
def mitigated_cost_function(params):
    def circuit_fn(noise_scale=1.0, shots=1000):
        # Scale quantum noise somehow
        # Execute VQE circuit with params
        return vqe.cost_function(params)
    
    return zne.execute(circuit_fn)

# Run VQE with error mitigation
# result = vqe.run(initial_params, cost_fn=mitigated_cost_function)
```

---

## Richardson Extrapolation

Advanced extrapolation technique:

```python
from quantum_debugger.qml.error_mitigation import richardson_extrapolation

# Collect data at different noise levels
scale_factors = [1.0, 2.0, 3.0, 4.0]
values = [0.85, 0.75, 0.65, 0.55]

# First-order Richardson
result = richardson_extrapolation(scale_factors, values, order=1)

# Second-order Richardson
result = richardson_extrapolation(scale_factors, values, order=2)
```

---

## Complete Example

```python
import numpy as np
from quantum_debugger.qml.error_mitigation import ZeroNoiseExtrapolation
from quantum_debugger.qml import VQE, h2_hamiltonian
from quantum_debugger.qml.ansatz import hardware_efficient_ansatz

# Setup problem
H = h2_hamiltonian()
exact_energy = np.linalg.eigvalsh(H)[0]

# Create VQE
vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=30)

# Without ZNE
result_noisy = vqe.run(np.array([0.5, 0.5]))
error_noisy = abs(result_noisy['ground_state_energy'] - exact_energy)

# With ZNE
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 1.5, 2.0, 2.5, 3.0],
    extrapolator='polynomial'
)

def zne_circuit(noise_scale=1.0, shots=1000):
    # Simulate noise scaling (placeholder)
    # In practice, modify noise model
    result = vqe.cost_function(np.array([0.5, 0.5]))
    return result * (1 + 0.1 * (noise_scale - 1))  # Simulated noise

mitigated_energy = zne.execute(zne_circuit)
error_mitigated = abs(mitigated_energy - exact_energy)

print(f"Noisy error: {error_noisy:.6f}")
print(f"Mitigated error: {error_mitigated:.6f}")
print(f"Improvement: {(1 - error_mitigated/error_noisy) * 100:.1f}%")
```

---

## Input Formats

### Statevector Input

```python
def circuit_fn(noise_scale=1.0, shots=1000):
    # Execute circuit, get state vector
    statevector = np.array([0.9, 0.1j, 0.0, 0.0])
    return {'statevector': statevector}

mitigated = zne.execute(circuit_fn)
```

### Measurement Counts Input

```python
def circuit_fn(noise_scale=1.0, shots=1000):
    # Execute circuit, get measurement counts
    counts = {
        '00': 850,
        '01': 50,
        '10': 70,
        '11': 30
    }
    return {'counts': counts}

mitigated = zne.execute(circuit_fn)
```

### Direct Value Input

```python
def circuit_fn(noise_scale=1.0, shots=1000):
    # Just return the expectation value
    return 0.85

mitigated = zne.execute(circuit_fn)
```

---

## Best Practices

### Choosing Scale Factors

```python
# Too few points - unreliable extrapolation
bad = [1.0, 3.0]  # Only 2 points

# Good for linear
good_linear = [1.0, 2.0, 3.0]  # 3 points

# Good for polynomial/exponential
good_poly = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]  # 6 points

# Too high - noise dominates
too_high = [1.0, 5.0, 10.0, 15.0]  # Signal lost
```

### Choosing Extrapolator

```python
# Low noise (< 5% error rate)
zne_low = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0],
    extrapolator='linear'
)

# Medium noise (5-15% error rate)
zne_med = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 1.5, 2.0, 2.5, 3.0],
    extrapolator='polynomial'
)

# High noise (> 15% error rate)
zne_high = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 1.3, 1.6, 2.0, 2.5],
    extrapolator='exponential'
)
```

---

## Performance Considerations

### Computational Cost

ZNE multiplies computational cost by the number of scale factors:

```python
# 3 scale factors = 3x cost
zne = ZeroNoiseExtrapolation(scale_factors=[1, 2, 3])

# 6 scale factors = 6x cost
zne = ZeroNoiseExtrapolation(scale_factors=[1, 1.5, 2, 2.5, 3, 3.5])
```

**Recommendation**: Start with 3 scale factors, increase if needed.

### When ZNE Helps

- **Circuit depth**: 10-100 gates
- **Noise level**: 1-15% error rate
- **Measurement shots**: > 1000

### When ZNE Struggles

- **Very deep circuits**: > 200 gates
- **Very high noise**: > 20% error rate
- **Few shots**: < 500

---

## Troubleshooting

### Extrapolation Fails

```python
# Try different extrapolator
zne = ZeroNoiseExtrapolation(
    scale_factors=[1, 2, 3],
    extrapolator='linear'  # Start simple
)

# If that fails, try polynomial
zne = ZeroNoiseExtrapolation(
    scale_factors=[1, 1.5, 2, 2.5, 3],
    extrapolator='polynomial'
)
```

### Worse Results After ZNE

```python
# Check if noise is too low
# ZNE overhead may exceed noise benefits
# In this case, use results without ZNE

# Or reduce scale factors
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 1.5, 2.0],  # Closer to λ=1
    extrapolator='linear'
)
```

---

## References

1. Temme, K., et al. "Error mitigation for short-depth quantum circuits." Physical Review Letters (2017)
2. Li, Y., & Benjamin, S. C. "Efficient variational quantum simulator incorporating active error minimization." Physical Review X (2017)
3. Endo, S., et al. "Practical quantum error mitigation for near-future applications." Physical Review X (2018)

---

## See Also

- [VQE Guide](vqe_guide.md) - Variational Quantum Eigensolver
- [QNN Guide](qnn_guide.md) - Quantum Neural Networks
- [Hamiltonians Guide](hamiltonians_guide.md) - Molecular Hamiltonians
