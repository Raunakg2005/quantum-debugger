# QuantumDebugger Documentation

Welcome to QuantumDebugger's documentation!

QuantumDebugger is an interactive debugger and profiler for quantum circuits with Qiskit integration.

## Features

- 🐛 Step-through debugging
- 🔍 State inspection
- 📊 Circuit profiling
- 🔗 Qiskit integration
- ✅ 88/88 tests passing

## Quick Start

### Installation

```bash
pip install quantum-debugger
```

### Basic Usage

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

## Contents

```{toctree}
:maxdepth: 2
:caption: User Guide

quickstart
api
examples
```

```{toctree}
:maxdepth: 2
:caption: Reference

modules
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
