# Zero-Noise Extrapolation (ZNE) Tutorial

**Version:** 0.4.0  
**Feature:** Quantum Error Mitigation

---

## What is Zero-Noise Extrapolation?

Zero-Noise Extrapolation (ZNE) is a quantum error mitigation technique that improves noisy circuit results **without requiring additional qubits**. It works by:

1. Running your circuit at multiple noise levels (via circuit folding)
2. Measuring the expectation value at each noise level
3. Extrapolating back to the zero-noise limit

**Result:** 10-20% improvement in fidelity with no hardware changes!

---

## Quick Start

### Basic Usage

```python
from quantum_debugger import QuantumCircuit, zero_noise_extrapolation
from quantum_debugger.noise import IBM_PERTH_2025

# Create noisy circuit
circuit = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
circuit.h(0).cnot(0, 1)

# Apply ZNE
result = zero_noise_extrapolation(circuit, shots=1000)

print(f"Unmitigated: {result['unmitigated_value']:.4f}")
print(f"Mitigated:   {result['mitigated_value']:.4f}")
print(f"Improvement: {result['improvement_factor']:.2f}x")
```

**Output:**
```
Unmitigated: 0.9044
Mitigated:   0.9951
Improvement: 1.10x
```

---

## How It Works

### Step 1: Circuit Folding

Circuit folding amplifies noise by inserting `G†G` sequences:

```python
from quantum_debugger import global_fold

# Original circuit: H + CNOT
circuit = QuantumCircuit(2, noise_model=noise)
circuit.h(0).cnot(0, 1)

# Folded 3x: (H + CNOT) + (CNOT† + H†) + (H + CNOT)
folded = global_fold(circuit, scale_factor=3.0)
```

**Noise scales linearly with circuit depth**, so folded circuit has ~3x more noise.

### Step 2: Measure at Multiple Scales

```python
scale_factors = [1.0, 2.0, 3.0]  # 1x, 2x, 3x noise
# ZNE runs circuit at each scale
```

### Step 3: Extrapolate to Zero

```python
# Fit curve through data points
# Evaluate at x=0 (zero noise)
mitigated_value = extrapolate(noise_levels, measured_values)
```

---

## Folding Methods

### Global Folding (Default)

Folds entire circuit uniformly:

```python
result = zero_noise_extrapolation(
    circuit,
    folding_method='global'
)
```

**Best for:** Uniform noise across all gates

### Local Folding

Folds only high-error gates (e.g., CNOTs):

```python
result = zero_noise_extrapolation(
    circuit,
    folding_method='local'
)
```

**Best for:** Gate-dependent noise

### Adaptive Folding

Folds gates proportional to their error rates:

```python
result = zero_noise_extrapolation(
    circuit,
    folding_method='adaptive'
)
```

**Best for:** Hardware-aware mitigation

---

## Extrapolation Methods

### Linear (Fast)

```python
result = zero_noise_extrapolation(
    circuit,
    extrapolation_method='linear'
)
```

Best for quick estimates.

### Richardson (Robust)

```python
result = zero_noise_extrapolation(
    circuit,
    extrapolation_method='richardson',
    richardson_order=2  # Quadratic fit
)
```

Best general-purpose method.

### Adaptive (Automatic)

```python
result = zero_noise_extrapolation(
    circuit,
    extrapolation_method='adaptive'
)
```

Tries multiple methods, picks best fit.

---

## Advanced Usage

### Custom Scale Factors

```python
result = zero_noise_extrapolation(
    circuit,
    scale_factors=[1.0, 1.5, 2.0, 2.5, 3.0],  # Fine-grained
    shots=2000
)
```

**Tip:** More data points = better extrapolation

### Error Bars

```python
from quantum_debugger.mitigation import zne_with_error_bars

result = zne_with_error_bars(
    circuit,
    n_trials=10,
    shots=1000
)

print(f"Mean: {result['mean']:.4f}")
print(f"Std:  {result['std']:.4f}")
print(f"95% CI: {result['confidence_interval']}")
```

### VQE Example

```python
# Variational circuit
def ansatz(params):
    circuit = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
    circuit.ry(0, params[0])
    circuit.ry(1, params[1])
    circuit.cnot(0, 1)
    circuit.rz(0, params[2])
    return circuit

# Mitigate energy measurement
circuit = ansatz([0.1, 0.2, 0.3])
result = zero_noise_extrapolation(circuit, shots=2000)
mitigated_energy = result['mitigated_value']
```

---

## When to Use ZNE

**✓ Good for:**
- Near-term quantum devices (10-100 qubits)
- Moderate noise levels (1-5% error per gate)
- Expectation value measurements (VQE, QAOA)
- When you can't use error correction

**✗ Not ideal for:**
- Very high noise (>10% error)
- Sampling-based algorithms
- Very deep circuits (>100 gates)

---

## Performance Tips

1. **Start with fewer scale factors** (3-5 is usually enough)
2. **Use adaptive methods** for unknown noise
3. **Increase shots** for better statistics (1000-2000)
4. **Use local/adaptive folding** to reduce overhead

---

## Comparison with Other Methods

| Method | Qubit Overhead | Measurement Overhead | Improvement |
|--------|----------------|---------------------|-------------|
| **ZNE** | 0x | 3-5x | 1.1-1.2x |
| Error Correction | 10-100x | 1x | 10-100x |
| Pauli Twirling | 0x | 10-100x | 1.1-1.3x |

ZNE offers **best balance** of overhead and improvement for NISQ devices.

---

## API Reference

### `zero_noise_extrapolation()`

```python
zero_noise_extrapolation(
    circuit,
    scale_factors=[1.0, 1.5, 2.0, 2.5, 3.0],
    extrapolation_method='richardson',
    folding_method='global',
    shots=1000
)
```

**Returns:**
```python
{
    'mitigated_value': float,
    'unmitigated_value': float,
    'improvement_factor': float,
    'noise_levels': list,
    'expectation_values': list,
    'fidelity_mitigated': float,
    'total_shots': int
}
```

---

## Further Reading

- [Implementation Plan](implementation_plan_v0.4.0_phase1.md)
- [Test Results](walkthrough_v0.4.0_phase1.md)
- [Original Paper](https://arxiv.org/abs/1612.02058) - Temme et al. (2017)

---

**Questions?** Check the [DOCUMENTATION.md](DOCUMENTATION.md) or open an issue on GitHub.
