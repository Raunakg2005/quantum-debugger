# QuantumDebugger v0.3.0 - Noise Simulation User Guide Addendum

## Noise Simulation (NEW in v0.3.0)

QuantumDebugger now includes **realistic noise simulation** to model real quantum hardware!

### Quick Start with Noise

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import DepolarizingNoise

# Create noisy circuit
noise = DepolarizingNoise(0.01)  # 1% error rate
qc = QuantumCircuit(2, noise_model=noise)
qc.h(0).cnot(0, 1)

# Run and get fidelity
results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")  # ~0.98
```

### Hardware Profiles

Simulate real quantum computers:

```python
from quantum_debugger.noise import IBM_PERTH_2025, GOOGLE_SYCAMORE_2025, IONQ_ARIA_2025

# IBM hardware
qc = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)

# View specs
print(IBM_PERTH_2025.info())
# Shows: T1=180μs, T2=220μs, gate errors, etc.
```

### Available Noise Models

1. **DepolarizingNoise** - Random Pauli errors
2. **AmplitudeDamping** - T1 energy decay
3. **PhaseDamping** - T2 dephasing
4. **ThermalRelaxation** - Combined T1/T2
5. **CompositeNoise** - Multiple sources combined

### Example: Compare Hardware

```python
for name, profile in [('IBM', IBM_PERTH_2025), ('IonQ', IONQ_ARIA_2025)]:
    qc = QuantumCircuit(2, noise_model=profile.noise_model)
    qc.h(0).cnot(0, 1)
    results = qc.run(shots=1000)
    print(f"{name}: Fidelity = {results['fidelity']:.4f}")
# IBM:  Fidelity = 0.9948
# IonQ: Fidelity = 0.9987 (better!)
```

### Memory Warning

For >10 qubits with noise, memory usage is high:

```python
# This warns about memory usage
qc = QuantumCircuit(11, noise_model=DepolarizingNoise(0.01))
# Warning: Density matrix requires ~16MB
```

### Full Tutorial

See [NOISE_TUTORIAL.md](NOISE_TUTORIAL.md) for complete documentation.

### Hardware Profiles Available

- IBM Perth 2025 (T1=180μs)
- Google Sycamore 2025 (T1=40μs) 
- IonQ Aria 2025 (T1=1000ms)
- Rigetti Aspen-M-3 2025 (T1=50μs)

---

*For full v0.2.2 User Guide, see above sections*
