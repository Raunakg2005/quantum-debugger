# QuantumDebugger

**Interactive debugger and profiler for quantum circuits with Qiskit integration**

[![PyPI version](https://badge.fury.io/py/quantum-debugger.svg)](https://pypi.org/project/quantum-debugger/)
[![Tests](https://img.shields.io/badge/tests-88%2F88%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue)](https://quantum-debugger.readthedocs.io/)


A powerful Python library for step-through debugging, state inspection, and performance analysis of quantum circuits. Now with **production-grade Qiskit integration**!

## ✨ Features

- 🐛 **Step-through Debugging** - Execute circuits gate-by-gate with breakpoints
- 🔍 **State Inspection** - Analyze quantum states at any point
- 📊 **Circuit Profiling** - Depth analysis, gate statistics, optimization suggestions  
- 🎨 **Visualization** - State vectors, Bloch spheres, and more
- 🔗 **Qiskit Integration** - Import/export circuits from Qiskit (NEW in v0.2.0!)
- ✅ **100% Tested** - 88 comprehensive tests, production-ready

## 🚀 Quick Start

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
debugger.step()  # Execute first gate
print(debugger.get_current_state())
debugger.step()  # Execute second gate
print(debugger.get_current_state())
```

### Qiskit Integration (NEW!)

```python
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter

# Import from Qiskit
qc_qiskit = QiskitCircuit(2)
qc_qiskit.h(0)
qc_qiskit.cx(0, 1)

qc_qd = QiskitAdapter.from_qiskit(qc_qiskit)

# Debug with our tools
debugger = QuantumDebugger(qc_qd)
debugger.add_breakpoint_at_gate(1)
debugger.continue_execution()

# Export back to Qiskit
qc_back = QiskitAdapter.to_qiskit(qc_qd)
```

## 📚 Core Features

### Supported Gates

**Single-qubit**: H, X, Y, Z, S, T, RX, RY, RZ, PHASE  
**Two-qubit**: CNOT, CZ, CP (controlled-phase), SWAP  
**Three-qubit**: Toffoli (CCNOT)

### Debugging Features

- ✅ Forward/backward stepping
- ✅ Breakpoints (gate-based & conditional)
- ✅ Execution history tracking
- ✅ State comparison
- ✅ Circuit profiling

### Validated Algorithms

Grover's Search • Deutsch-Jozsa • Shor's Period Finding • Quantum Phase Estimation • VQE • Quantum Teleportation • QAOA • Error Correction

## 🎯 Examples

### Debugging Grover's Algorithm

```python
from quantum_debugger import QuantumCircuit, QuantumDebugger

# 2-qubit Grover's
qc = QuantumCircuit(2)
qc.h(0).h(1)  # Superposition
qc.cz(0, 1)   # Oracle
qc.h(0).h(1)  # Diffusion
qc.z(0).z(1)
qc.cz(0, 1)
qc.h(0).h(1)

# Debug with breakpoints
debugger = QuantumDebugger(qc)
debugger.add_breakpoint_at_gate(2)  # Break after oracle
debugger.continue_execution()
print(f"After oracle: {debugger.get_current_state()}")
```

### Circuit Profiling

```python
from quantum_debugger import QuantumCircuit, CircuitProfiler

qc = QuantumCircuit(3)
for i in range(10):
    qc.h(i % 3)
    qc.cnot(i % 3, (i + 1) % 3)

profiler = CircuitProfiler(qc)
metrics = profiler.analyze()

print(f"Depth: {metrics.depth}")
print(f"Gates: {metrics.total_gates}")
print("Optimization suggestions:")
for suggestion in profiler.get_optimization_suggestions():
    print(f"  • {suggestion}")
```

## 📊 Testing & Quality

- **88/88 tests passing** (100%)
- Validated up to **12 qubits** (4,096-D state space)
- **100+ gate circuits** tested
- Perfect Qiskit integration fidelity
- Numerical precision < 1e-10

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for details.

## 🔧 Requirements

- Python 3.8+
- NumPy >= 1.21.0
- SciPy >= 1.7.0
- Matplotlib >= 3.5.0
- Qiskit >= 2.0 (optional, for integration features)

## 📖 Documentation

- [Examples](examples/) - Interactive demos
- [Test Summary](TEST_SUMMARY.md) - Complete test coverage
- [Changelog](CHANGELOG.md) - Version history
- [Roadmap](ROADMAP.md) - Future features

## 🤝 Contributing

Contributions welcome! See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🌟 What's New in v0.2.0

- ✨ **Qiskit Integration** - Bidirectional circuit conversion
- ✨ **CP Gate** - Controlled-phase gate support  
- ✨ **19 New Tests** - Qiskit integration fully validated
- ✨ **12-Qubit Support** - Tested on extreme-scale circuits
- 🐛 **Bug Fixes** - Improved debugger API compatibility

## 🚀 Roadmap

- [ ] Noise simulation
- [ ] Web-based debugger UI
- [ ] Cirq integration
- [ ] Hardware backend support
- [ ] Quantum machine learning tools

---

**PyPI**: https://pypi.org/project/quantum-debugger/  
**Author**: warlord9004  
**Version**: 0.2.0
