# Error Mitigation Guide

Advanced error mitigation techniques for production quantum machine learning on real noisy quantum hardware.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Noise Models](#noise-models)
3. [PEC (Probabilistic Error Cancellation)](#pec)
4. [CDR (Clifford Data Regression)](#cdr)
5. [Error Characterization](#error-characterization)
6. [Best Practices](#best-practices)
7. [API Reference](#api-reference)

---

## Quick Start

### Using Error Mitigation

```python
from quantum_debugger.qml.mitigation import PEC, CDR, DepolarizingNoise

# Setup PEC for gate errors
pec = PEC(gate_error_rates={'rx': 0.005, 'cnot': 0.02})

# Apply to circuit
result, uncertainty = pec.apply_pec(circuit_function, params, n_samples=100)
print(f"Mitigated result: {result:.4f} ± {uncertainty:.4f}")
```

### Simulating Realistic Noise

```python
from quantum_debugger.qml.mitigation import create_realistic_noise_model

# IBM quantum computer-like noise
noise = create_realistic_noise_model(
    gate_error_rate=0.005,
    t1_time=100.0,  # μs
    t2_time=70.0,   # μs
    gate_time=0.05  # μs
)

# Apply to circuit execution
noisy_state = noise.apply_noise(state, 'cnot')
```

---

## Noise Models

### Depolarizing Noise

Most common noise model - uniform error across all Pauli operators.

```python
from quantum_debugger.qml.mitigation import DepolarizingNoise

# 1% depolarization per gate
noise = DepolarizingNoise(error_rate=0.01)

# Apply to state
noisy_state = noise.apply_noise(state, gate_type='rx')
```

**Use cases:**
- General-purpose noise simulation
- Conservative error estimates
- Benchmarking algorithms

### Amplitude Damping (T1 Relaxation)

Models energy decay from |1⟩ to |0⟩.

```python
from quantum_debugger.qml.mitigation import AmplitudeDampingNoise

# T1 relaxation
noise = AmplitudeDampingNoise(gamma=0.05)
```

**Physics:**
- Spontaneous emission
- Energy relaxation to ground state
- T1 time typically 50-100 μs on superconducting qubits

### Phase Damping (T2 Dephasing)

Models loss of quantum coherence without energy loss.

```python
from quantum_debugger.qml.mitigation import PhaseDampingNoise

# T2 dephasing
noise = PhaseDampingNoise(lambda_param=0.03)
```

**Physics:**
- Pure dephasing
- Loss of quantum superposition
- T2 ≤ 2*T1 (usually T2 < T1)

### Composite Noise

Combine multiple noise sources for realistic simulation.

```python
from quantum_debugger.qml.mitigation import CompositeNoise

noise = CompositeNoise([
    DepolarizingNoise(0.005),
    AmplitudeDampingNoise(0.02),
    PhaseDampingNoise(0.015)
])
```

---

## PEC (Probabilistic Error Cancellation)

### Overview

PEC mitigates **gate-level errors** using quasi-probability decomposition.

**How it works:**
1. Characterize each gate's error rate
2. Decompose noisy gates into sum of implementable operations
3. Sample circuits according to quasi-probabilities
4. Combine results with appropriate weights

### Basic Usage

```python
from quantum_debugger.qml.mitigation import PEC

# Initialize with gate errors
pec = PEC(gate_error_rates={
    'rx': 0.005,
    'ry': 0.005,
    'cnot': 0.02
})

# Apply to circuit
def my_circuit(params):
    # Execute quantum circuit
    return result

mitigated, uncertainty = pec.apply_pec(
    my_circuit,
    params=np.array([0.5, 1.2]),
    n_samples=100
)
```

### Quasi-Probability Decomposition

For a noisy gate with error rate p:
```
U_ideal = (1/(1-p)) * U_noisy - (p/3(1-p)) * (X·U + Y·U + Z·U)
```

```python
# Get decomposition
decomp = pec.decompose_noisy_gate('cnot', error_rate=0.02)

# Returns: [(gate, probability), ...]
# [('cnot', 1.02), ('cnot_X', -0.0068), ('cnot_Y', -0.0068), ('cnot_Z', -0.0068)]
```

### Sampling Overhead

PEC requires multiple circuit executions. Estimate overhead:

```python
overhead = pec.estimate_sampling_overhead(
    circuit_depth=20,
    avg_error_rate=0.01
)
print(f"Need {overhead} samples")  # Scales exponentially with depth
```

**Rule of thumb:**
- Shallow circuits (depth < 10): 10-100 samples
- Medium circuits (depth 10-20): 100-1000 samples
- Deep circuits (depth > 20): May be impractical

---

## CDR (Clifford Data Regression)

### Overview

CDR mitigates **measurement errors** by learning from Clifford circuits.

**How it works:**
1. Generate random Clifford circuits (efficiently simulatable)
2. Compare noisy vs ideal results
3. Train regression model
4. Apply learned correction to target circuits

### Basic Workflow

```python
from quantum_debugger.qml.mitigation import CDR

# 1. Initialize
cdr = CDR(n_clifford_circuits=50, regression_method='linear')

# 2. Generate training data
training_data = cdr.generate_training_data(n_qubits=4, circuit_depth=3)

# 3. Train on noisy executor
def noisy_executor(circuit):
    # Execute circuit and return measurement
    return measurement_result

cdr.train(training_data, noisy_executor)

# 4. Apply to mitigate errors
clean_result = cdr.apply_cdr(noisy_measurement)
```

### Regression Methods

```python
# Linear regression (fast, good for small errors)
cdr = CDR(regression_method='linear')

# Ridge regression (better for noisy data)
cdr = CDR(regression_method='ridge')

# Lasso regression (sparse solutions)
cdr = CDR(regression_method='lasso')
```

### CDR vs PEC

| Aspect | PEC | CDR |
|--------|-----|-----|
| **Targets** | Gate errors | Measurement errors |
| **Overhead** | High (exponential) | Low (one-time training) |
| **Accuracy** | Excellent | Good |
| **Best for** | Shallow circuits | Deep circuits |
| **Training** | No training needed | Requires Clifford training |

**Recommendation:** Use both together for best results.

---

## Error Characterization

### Readout Error

Measure confusion matrix:

```python
from quantum_debugger.qml.mitigation import characterize_readout_error

confusion_matrix = characterize_readout_error(
    n_qubits=2,
    executor=my_executor,
    n_shots=10000
)

# Diagonal = correct measurements
fidelity = np.trace(confusion_matrix) / confusion_matrix.shape[0]
print(f"Readout fidelity: {fidelity:.2%}")
```

### Gate Fidelity

Estimate using randomized benchmarking:

```python
from quantum_debugger.qml.mitigation import estimate_gate_fidelity

fidelity = estimate_gate_fidelity(
    gate_type='cnot',
    executor=my_executor,
    n_trials=100
)

error_rate = 1 - fidelity
print(f"CNOT error: {error_rate:.4f}")
```

### Full Calibration

Get all error parameters:

```python
from quantum_debugger.qml.mitigation.error_characterization import calibrate_error_mitigation

params = calibrate_error_mitigation(
    n_qubits=4,
    executor=my_executor,
    gate_types=['rx', 'ry', 'rz', 'cnot']
)

print(f"Readout fidelity: {params['readout_fidelity']:.2%}")
print(f"Gate errors: {params['gate_errors']}")
print(f"T1: {params['t1_time']:.1f} μs")
print(f"T2: {params['t2_time']:.1f} μs")
```

---

## Best Practices

### When to Use Error Mitigation

✅ **Use error mitigation when:**
- Running on real quantum hardware
- Circuit depth > 5 gates
- Accuracy is critical
- You can afford computational overhead

❌ **Skip error mitigation if:**
- Running perfect simulator
- Shallow circuits only
- Exploratory/debugging work
- Extremely limited computational budget

### Choosing Techniques

**For gate-dominated errors:**
```python
# Use PEC
pec = PEC(gate_error_rates=measured_errors)
result = pec.apply_pec(circuit, params)
```

**For measurement-dominated errors:**
```python
# Use CDR
cdr = CDR(n_clifford_circuits=50)
cdr.train(training_data, executor)
result = cdr.apply_cdr(noisy_measurement)
```

**For production systems:**
```python
# Use both
pec_result, _ = pec.apply_pec(circuit, params)
final_result = cdr.apply_cdr(pec_result)
```

### Optimizing Performance

**Reduce PEC overhead:**
```python
# 1. Minimize circuit depth
# - Compile/optimize circuits first
# - Remove unnecessary gates

# 2. Use adaptive sampling
overhead = pec.estimate_sampling_overhead(depth, error_rate)
n_samples = min(overhead, max_budget)

# 3. Parallelize sampling
# Execute samples in parallel on quantum hardware
```

**Improve CDR accuracy:**
```python
# 1. More training circuits
cdr = CDR(n_clifford_circuits=100)  # More is better

# 2. Match circuit structure
training_data = cdr.generate_training_data(
    n_qubits=target_qubits,
    circuit_depth=target_depth  # Match target circuit
)

# 3. Use appropriate regression
cdr = CDR(regression_method='ridge')  # Ridge for noisy data
```

---

## Complete Workflow Example

```python
from quantum_debugger.qml.mitigation import (
    PEC, CDR,
    create_realistic_noise_model,
    calibrate_error_mitigation
)
from quantum_debugger.qml.qnn import QuantumNeuralNetwork

# 1. Characterize hardware
print("Calibrating error parameters...")
error_params = calibrate_error_mitigation(
    n_qubits=4,
    executor=qpu_executor,
    gate_types=['rx', 'ry', 'cnot']
)

# 2. Setup PEC
pec = PEC(
    gate_error_rates=error_params['gate_errors'],
    sampling_overhead=50
)

# 3. Setup CDR
cdr = CDR(n_clifford_circuits=50)
training_data = cdr.generate_training_data(n_qubits=4, circuit_depth=5)
cdr.train(training_data, qpu_executor)

# 4. Create QNN with mitigation
qnn = QuantumNeuralNetwork(n_qubits=4)
# ... add layers ...
qnn.compile(optimizer='adam', loss='mse')

# 5. Mitigated training
def mitigated_forward(params, X):
    # Forward pass with PEC
    raw_output, _ = pec.apply_pec(
        lambda p: qnn.forward(p, X),
        params,
        n_samples=50
    )
    # CDR correction
    clean_output = cdr.apply_cdr(raw_output)
    return clean_output

# 6. Train
history = qnn.fit(X_train, y_train, epochs=50)

# 7. Evaluate with mitigation
predictions = mitigated_forward(qnn.weights, X_test)
accuracy = np.mean(predictions == y_test)
print(f"Mitigated accuracy: {accuracy:.2%}")
```

---

## API Reference

### PEC Class

```python
PEC(gate_error_rates, sampling_overhead=10)
```

**Methods:**
- `set_gate_error(gate_type, error_rate)`: Set error rate
- `decompose_noisy_gate(gate_type, error_rate)`: Get decomposition
- `estimate_sampling_overhead(depth, avg_error)`: Estimate samples needed
- `apply_pec(circuit_func, params, n_samples)`: Apply mitigation

### CDR Class

```python
CDR(n_clifford_circuits=50, regression_method='linear')
```

**Methods:**
- `generate_training_data(n_qubits, depth)`: Create Clifford circuits
- `train(training_data, executor)`: Train regression model
- `apply_cdr(noisy_result)`: Apply mitigation
- `is_trained()`: Check training status

### Noise Models

```python
DepolarizingNoise(error_rate=0.01)
AmplitudeDampingNoise(gamma=0.05)
PhaseDampingNoise(lambda_param=0.03)
CompositeNoise(noise_models)
```

**Methods:**
- `apply_noise(state, gate_type)`: Apply noise to state

### Functions

```python
characterize_readout_error(n_qubits, executor, n_shots)
estimate_gate_fidelity(gate_type, executor, n_trials)
measure_gate_errors(gate_types, executor, n_trials)
calibrate_error_mitigation(n_qubits, executor, gate_types)
create_realistic_noise_model(gate_error, t1, t2, gate_time)
```

---

## Troubleshooting

### PEC Taking Too Long

```python
# Reduce sampling
pec.sampling_overhead = 10  # Lower number

# Or use adaptive approach
required = pec.estimate_sampling_overhead(depth, error)
actual = min(required, 100)  # Cap at 100
```

### CDR Not Improving Results

```python
# 1. Check if trained
if not cdr.is_trained():
    cdr.train(training_data, executor)

# 2. Increase training circuits
cdr = CDR(n_clifford_circuits=100)  # More training

# 3. Try different regression
cdr = CDR(regression_method='ridge')  # More robust
```

### High Uncertainty in PEC

```python
# Increase samples
result, unc = pec.apply_pec(circuit, params, n_samples=500)

# Check if within tolerance
if unc > threshold:
    print("Warning: High uncertainty, increase samples")
```

---

## Performance Tips

1. **Profile first**: Measure actual error rates before applying mitigation
2. **Start simple**: Try CDR before PEC (lower overhead)
3. **Optimize circuits**: Reduce depth before mitigating
4. **Parallel execution**: Run PEC samples in parallel
5. **Cache training**: Save CDR model, reuse for similar circuits

---

## Next Steps

- **Week 5**: Circuit Optimization
- **Week 6**: Hardware Integration (IBM, AWS)

---

**Full Documentation**: [quantum-debugger.readthedocs.io](https://quantum-debugger.readthedocs.io)
