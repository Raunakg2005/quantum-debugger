# QuantumDebugger Documentation

**Version:** 0.4.0 (Phase 1-2 Complete)  
**Repository:** [github.com/Raunakg2005/quantum-debugger](https://github.com/Raunakg2005/quantum-debugger)

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Noise Simulation (v0.3.0)](#noise-simulation)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Contributing](#contributing)

---

## Installation

```bash
pip install quantum-debugger
```

**Requirements:**
- Python 3.8+
- NumPy, SciPy, Matplotlib

**Optional:**
- Qiskit (for integration features)

---

## Quick Start

### Basic Circuit

```python
from quantum_debugger import QuantumCircuit

# Create Bell state
qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

# Get state
state = qc.get_statevector()
print(state)  # 0.707|00⟩ + 0.707|11⟩
```

### Interactive Debugging

```python
from quantum_debugger import QuantumDebugger

debugger = QuantumDebugger(qc)
debugger.step()  # Execute one gate
print(debugger.get_current_state())
```

---

## Noise Simulation

**NEW in v0.3.0:** Simulate realistic quantum hardware with noise models.

### Hardware Profiles

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import IBM_PERTH_2025, GOOGLE_SYCAMORE_2025, IONQ_ARIA_2025

# Simulate on IBM hardware
qc = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
qc.h(0).cnot(0, 1)
results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")
```

### Available Hardware Profiles

| Hardware | T1 | T2 | 1Q Error | 2Q Error |
|----------|-----|-----|----------|----------|
| IBM Perth 2025 | 180μs | 220μs | 0.03% | 0.8% |
| Google Sycamore 2025 | 40μs | 30μs | 0.15% | 0.5% |
| IonQ Aria 2025 | 1000ms | 500ms | 0.01% | 0.2% |
| Rigetti Aspen 2025 | 50μs | 40μs | 0.05% | 1.0% |

### Noise Models

**1. Depolarizing Noise**
```python
from quantum_debugger.noise import DepolarizingNoise

noise = DepolarizingNoise(0.01)  # 1% error rate
qc = QuantumCircuit(2, noise_model=noise)
```

**2. Thermal Relaxation (T1/T2)**
```python
from quantum_debugger.noise import ThermalRelaxation

noise = ThermalRelaxation(
    t1=100e-6,      # 100 microseconds
    t2=80e-6,       # 80 microseconds
    gate_time=50e-9 # 50 nanoseconds
)
```

**3. Composite Noise**
```python
from quantum_debugger.noise import CompositeNoise

composite = CompositeNoise([
    ThermalRelaxation(t1=150e-6, t2=100e-6, gate_time=50e-9),
    DepolarizingNoise(0.002)
])
```

See [NOISE_TUTORIAL.md](NOISE_TUTORIAL.md) for complete documentation.

---

## Hardware Profiles

**NEW in v0.4.0 Phase 3:** Realistic quantum hardware specifications from major providers

### Available Profiles (11 total)

**AWS Braket:**
- IonQ Harmony - 11 qubits, 99.99% fidelity
- Rigetti Aspen-M-3 - 80 qubits, fast gates

**Azure Quantum:**
- Quantinuum H1-1 - 20 qubits, 99.995% fidelity (best in class!)
- Honeywell H2 - 12 qubits, excellent coherence

**2025 Updates:**
- IBM Heron - 133 qubits, 5x better gates
- Google Willow - 105 qubits, breakthrough specs
- IonQ Forte - 32 qubits, record 99.9% two-qubit fidelity

**Original:**
- IBM Perth, Google Sycamore, IonQ Aria, Rigetti Aspen

### Basic Usage

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import IONQ_HARMONY_AWS, IBM_HERON_2025

# Simulate on IonQ Harmony (AWS Braket)
circuit = QuantumCircuit(3, noise_model=IONQ_HARMONY_AWS.noise_model)
circuit.h(0)
for i in range(2):
    circuit.cnot(i, i+1)
result = circuit.run(shots=1000)
print(f"IonQ fidelity: {result['fidelity']:.4f}")

# Compare with IBM Heron 2025
circuit2 = QuantumCircuit(3, noise_model=IBM_HERON_2025.noise_model)
# ... same gates ...
result2 = circuit2.run(shots=1000)
print(f"IBM fidelity: {result2['fidelity']:.4f}")
```

### Profile by Name

```python
from quantum_debugger.noise import get_hardware_profile

profile = get_hardware_profile('quantinuum_h1')
circuit = QuantumCircuit(2, noise_model=profile.noise_model)
```

See [HARDWARE_PROFILES.md](HARDWARE_PROFILES.md) for complete specifications.

---

## Zero-Noise Extrapolation (ZNE)

**NEW in v0.4.0:** Mitigate noise errors using Zero-Noise Extrapolation.

### Basic Usage

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import NoiseModel
from quantum_debugger.mitigation import apply_zne

# Create noisy circuit
circuit = QuantumCircuit(2)
circuit.h(0).cnot(0, 1)

noise = NoiseModel()
noise.add_depolarizing_error(0.01, [0, 1])

# Apply ZNE
mitigated_result = apply_zne(
    circuit,
    noise_model=noise,
    scale_factors=[1, 2, 3],
    extrapolation='richardson',
    shots=1000
)
```

### Extrapolation Methods

- `'richardson'` - Richardson extrapolation (recommended)
- `'linear'` - Linear extrapolation
- `'exponential'` - Exponential fit
- `'adaptive'` - Adapts to data quality
- `'weighted'` - Weighted ensemble

### Advanced: Observable Measurement

```python
def measure_energy(circuit):
    result = circuit.run(shots=1000)
    # Calculate observable expectation value
    return expectation_value

mitigated_energy = apply_zne(
    circuit,
    noise_model=noise,
    scale_factors=[1, 2, 3, 5],
    extrapolation='exponential',
    shots=2000,
    observable_fn=measure_energy
)
```

See [ZNE_TUTORIAL.md](ZNE_TUTORIAL.md) for detailed examples.

---

## API Reference

### QuantumCircuit

**Constructor:**
```python
QuantumCircuit(num_qubits, num_classical=0, noise_model=None)
```

**Parameters:**
- `num_qubits` (int): Number of qubits
- `num_classical` (int): Number of classical bits
- `noise_model` (NoiseModel): Optional noise model

**Methods:**
- `h(qubit)`: Apply Hadamard gate
- `x(qubit)`: Apply X (NOT) gate
- `cnot(control, target)`: Apply CNOT gate
- `run(shots=1000)`: Execute circuit
- `get_statevector()`: Get current quantum state
- `set_noise_model(noise_model)`: Set noise model

### QuantumDebugger

**Constructor:**
```python
QuantumDebugger(circuit)
```

**Methods:**
- `step()`: Execute next gate
- `step_back()`: Undo last gate
- `run_to_gate(n)`: Run until gate n
- `set_breakpoint(gate_index)`: Set breakpoint
- `get_current_state()`: Get current state

### Noise Models

**DepolarizingNoise(probability)**
- Random Pauli errors (X, Y, Z)

**AmplitudeDamping(gamma)**
- Energy decay (T1 relaxation)

**PhaseDamping(gamma)**
- Phase decoherence (T2 dephasing)

**ThermalRelaxation(t1, t2, gate_time)**
- Combined T1/T2 decay

**CompositeNoise(noise_models)**
- Combine multiple noise sources

---

## Examples

### Grover's Algorithm

```python
from quantum_debugger import QuantumCircuit

qc = QuantumCircuit(2)

# Superposition
qc.h(0).h(1)

# Oracle (mark |11⟩)
qc.cz(0, 1)

# Diffusion
qc.h(0).h(1)
qc.x(0).x(1)
qc.cz(0, 1)
qc.x(0).x(1)
qc.h(0).h(1)

results = qc.run(shots=1000)
print(results['counts'])
```

### Noisy Grover with Hardware

```python
from quantum_debugger.noise import IBM_PERTH_2025

qc = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
# ... same circuit as above ...
results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")
```

### Quantum Fourier Transform

```python
import numpy as np

qc = QuantumCircuit(3)

for j in range(3):
    qc.h(j)
    for k in range(j+1, 3):
        angle = np.pi / (2**(k-j))
        qc.cp(angle, k, j)

# Swap qubits
qc.swap(0, 2)
```

---

## Testing

**Test Coverage:** 177/177 tests passing

```bash
# Run all tests
python -m pytest test_*.py -v

# Run noise tests
python test_noise.py
python test_circuit_noise.py

# Qiskit comparison
python compare_with_qiskit.py
```

---

## Validation

QuantumDebugger's noise simulation is validated against:
- Quantum mechanics theory (Kraus operators, density matrices)
- Qiskit Aer noise simulator
- 177 comprehensive tests including unique quantum phenomena

**Qiskit Comparison Results:**
- Max fidelity difference: 6.28%
- Thermal relaxation accuracy: 99.9%
- All fidelity trends match

---

## Performance

**Simulation Speed:**
- 2-qubit circuits: ~10ms with noise
- 5-qubit circuits: ~50ms with noise
- Up to 12 qubits supported

**Memory Usage:**
- Noiseless: O(2^n) for n qubits
- With noise: O(4^n) (density matrix)
- Warning issued for >10 qubits with noise

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

---

## License

MIT License - see LICENSE file for details.

---

## Citation

If you use QuantumDebugger in research:

```bibtex
@software{quantumdebugger2024,
  author = {Your Name},
  title = {QuantumDebugger: Interactive Quantum Circuit Simulator},
  year = {2024},
  version = {0.3.0},
  url = {https://github.com/Raunakg2005/quantum-debugger}
}
```

---

## Links

- **Documentation:** [NOISE_TUTORIAL.md](NOISE_TUTORIAL.md)
- **GitHub:** [github.com/Raunakg2005/quantum-debugger](https://github.com/Raunakg2005/quantum-debugger)
- **PyPI:** [pypi.org/project/quantum-debugger](https://pypi.org/project/quantum-debugger)
- **Issues:** [GitHub Issues](https://github.com/Raunakg2005/quantum-debugger/issues)

---

**Version 0.3.0** - Released December 2024  
Realistic noise simulation with hardware profiles and Qiskit validation.
