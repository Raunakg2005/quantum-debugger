# Quantum Debugger Documentation

**Version 0.4.0** - Interactive quantum circuit debugger with Quantum Machine Learning

Welcome to the documentation for Quantum Debugger, a powerful Python library for quantum circuit debugging, performance analysis, and quantum machine learning.

## What's New in v0.4.0

- **Quantum Machine Learning (QML)** - Complete QML module with VQE, QAOA
- **Parameterized Gates** - RX, RY, RZ with gradient computation  
- **Training Framework** - 4 classical optimizers (Adam, SGD, SPSA, RMSprop)
- **316 Tests** - Comprehensive test coverage (100% passing)

## Features

- 🐛 Step-through debugging
- 🔍 State inspection  
- 📊 Circuit profiling
- 🔗 Qiskit integration
- 🧠 Quantum Machine Learning (NEW!)
- ⚗️ VQE for molecular chemistry (NEW!)
- 🎯 QAOA for optimization (NEW!)

## Quick Start

### Installation

```bash
pip install quantum-debugger
```

### Basic Debugging

```python
from quantum_debugger import QuantumCircuit, QuantumDebugger

# Create a Bell state
qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

# Debug step-by-step
debugger = QuantumDebugger(qc)
debugger.step()
print(debugger.get_current_state())
```

### Quantum Machine Learning

```python
from quantum_debugger.qml import VQE, h2_hamiltonian, hardware_efficient_ansatz

# VQE for H2 molecule
H = h2_hamiltonian()
vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)
result = vqe.run(initial_params)
print(f"Ground state: {result['ground_state_energy']:.6f} Hartree")
```

## Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

quickstart
examples
```

```{toctree}
:maxdepth: 2
:caption: API Reference  

modules
api
qml_api
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
