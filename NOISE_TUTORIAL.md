# Noise Simulation Tutorial

## Introduction

This tutorial demonstrates how to use QuantumDebugger's noise simulation features to model realistic quantum hardware.

## Quick Start

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import DepolarizingNoise

# Create a noisy circuit
noise = DepolarizingNoise(0.01)  # 1% error rate
qc = QuantumCircuit(2, noise_model=noise)

# Build circuit
qc.h(0)
qc.cnot(0, 1)

# Run with noise
results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")
```

## Hardware Profiles

Simulate real quantum computers:

```python
from quantum_debugger.noise import IBM_PERTH_2025, GOOGLE_SYCAMORE_2025, IONQ_ARIA_2025

# Method 1: Direct assignment
qc = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)

# Method 2: By name
from quantum_debugger.noise import get_hardware_profile
ibm = get_hardware_profile('ibm')
ibm.apply_to_circuit(qc)

# Method 3: Runtime configuration
qc = QuantumCircuit(2)
qc.set_noise_model(IONQ_ARIA_2025.noise_model)

# View hardware specs
print(IBM_PERTH_2025.info())
```

## Noise Models

### 1. Depolarizing Noise
Random Pauli errors (X, Y, Z):

```python
from quantum_debugger.noise import DepolarizingNoise

noise = DepolarizingNoise(0.05)  # 5% error rate
qc = QuantumCircuit(2, noise_model=noise)
```

### 2. Amplitude Damping (T1)
Energy decay |1⟩ → |0⟩:

```python
from quantum_debugger.noise import AmplitudeDamping

noise = AmplitudeDamping(gamma=0.01)
qc = QuantumCircuit(1, noise_model=noise)
```

### 3. Phase Damping (T2)
Phase coherence loss:

```python
from quantum_debugger.noise import PhaseDamping

noise = PhaseDamping(gamma=0.02)
qc = QuantumCircuit(1, noise_model=noise)
```

### 4. Thermal Relaxation (T1 + T2)
Combined energy and phase decay:

```python
from quantum_debugger.noise import ThermalRelaxation

noise = ThermalRelaxation(
    t1=100e-6,      # T1 = 100 microseconds
    t2=80e-6,       # T2 = 80 microseconds
    gate_time=50e-9 # Gate time = 50 nanoseconds
)
qc = QuantumCircuit(1, noise_model=noise)
```

### 5. Composite Noise
Combine multiple noise sources:

```python
from quantum_debugger.noise import CompositeNoise, ThermalRelaxation, DepolarizingNoise

thermal = ThermalRelaxation(t1=150e-6, t2=100e-6, gate_time=50e-9)
depol = DepolarizingNoise(0.002)
composite = CompositeNoise([thermal, depol])

qc = QuantumCircuit(2, noise_model=composite)
```

## Example: Grover's Algorithm with Noise

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import IBM_PERTH_2025, IONQ_ARIA_2025
import numpy as np

def grover_search(noise_model=None):
    qc = QuantumCircuit(2, noise_model=noise_model)
    
    # Initialize superposition
    qc.h(0)
    qc.h(1)
    
    # Oracle (mark |11⟩)
    qc.cz(0, 1)
    
    # Diffusion
    qc.h(0).h(1)
    qc.x(0).x(1)
    qc.cz(0, 1)
    qc.x(0).x(1)
    qc.h(0).h(1)
    
    return qc

# Compare hardware
for name, profile in [('Clean', None), ('IBM', IBM_PERTH_2025), ('IonQ', IONQ_ARIA_2025)]:
    noise = profile.noise_model if profile else None
    qc = grover_search(noise_model=noise)
    results = qc.run(shots=1000)
    
    if noise:
        print(f"{name}: Fidelity = {results['fidelity']:.4f}")
    else:
        print(f"{name}: Perfect execution")
```

## Fidelity Tracking

Noise simulation automatically tracks fidelity:

```python
qc = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
qc.h(0).cnot(0, 1)

results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")
print(f"Std Dev:  {results['fidelity_std']:.4f}")
```

## Memory Warnings

For circuits >10 qubits, density matrices require lots of memory:

```python
# This will warn about ~16MB memory usage
qc = QuantumCircuit(11, noise_model=DepolarizingNoise(0.01))
# Warning: Density matrix for 11 qubits requires ~16.0MB memory.
```

## Best Practices

1. **Start Simple**: Use `DepolarizingNoise` for initial tests
2. **Match Hardware**: Use hardware profiles for realistic simulation
3. **Check Fidelity**: Monitor `results['fidelity']` to see noise impact
4. **Combine Sources**: Use `CompositeNoise` for realistic scenarios
5. **Mind Memory**: Keep <10 qubits for density matrix simulation

## Advanced: List Available Profiles

```python
from quantum_debugger.noise import list_hardware_profiles

profiles = list_hardware_profiles()
print("Available hardware:")
for p in profiles:
    print(f"  - {p}")
```

## Troubleshooting

**Q: Why is my noisy circuit slower?**
A: Noise simulation uses density matrices (2^n × 2^n), which are slower than state vectors.

**Q: Can I simulate circuits >10 qubits with noise?**
A: Yes, but memory usage grows exponentially. Consider using partial noise models.

**Q: How do I compare different hardware?**
A: Run the same circuit with different profiles and compare fidelity values.

## Next Steps

- Try different noise models
- Experiment with hardware profiles
- Test your quantum algorithms with realistic noise
- Compare results with noiseless execution
