# QuantumDebugger 🔬

A powerful Python library for **interactive debugging and profiling of quantum circuits** with step-through execution, state visualization, and performance analysis.

## 🌟 Features

### 🐛 Interactive Debugging
- **Step-through execution**: Execute quantum circuits gate-by-gate
- **Breakpoints**: Set breakpoints at specific gates or conditions
- **State inspection**: Examine quantum state at any point in execution
- **Execution history**: Track and replay circuit execution
- **Rewind capability**: Step backwards through circuit execution

### 📊 Visualization
- **State vector plots**: Visualize quantum state amplitudes and phases
- **Probability distributions**: See measurement probabilities
- **Bloch sphere**: 3D visualization for single qubit states
- **Circuit diagrams**: ASCII and graphical circuit representations

### 📈 Performance Profiling
- **Gate depth analysis**: Measure circuit depth and critical paths
- **Complexity metrics**: Gate counts, T-count, CNOT count
- **Performance estimation**: Predict execution time on quantum hardware
- **Optimization suggestions**: Get recommendations for circuit improvements

## 🚀 Quick Start

### Installation

```bash
pip install quantum-debugger
```

### Basic Usage

```python
from quantum_debugger import QuantumCircuit, QuantumDebugger

# Create a Bell state circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

# Debug the circuit
debugger = QuantumDebugger(qc)

# Step through execution
debugger.step()  # Apply H gate
debugger.inspect_state()  # Examine current state
debugger.visualize()  # Show state visualization

debugger.step()  # Apply CNOT
debugger.inspect_state()  # See entangled state
```

### Setting Breakpoints

```python
# Set breakpoint at gate 5
debugger.set_breakpoint(gate=5)

# Run until breakpoint
debugger.run_until_breakpoint()

# Conditional breakpoint
debugger.set_breakpoint(condition=lambda state: state.is_entangled())
```

### Profiling

```python
from quantum_debugger import CircuitProfiler

profiler = CircuitProfiler(qc)
report = profiler.analyze()

print(f"Gate depth: {report.depth}")
print(f"Total gates: {report.gate_count}")
print(f"CNOT count: {report.cnot_count}")
```

## 📚 Examples

Check out the `examples/` directory for:
- **Bell State Debugging**: Step-by-step entanglement creation
- **Grover's Algorithm**: Profiling and optimization
- **Interactive Demo**: Full feature showcase

## 🛠️ Requirements

- Python 3.8+
- NumPy
- Matplotlib
- (Optional) Qiskit/Cirq for integration

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use in your quantum computing projects!

## 🎯 Why QuantumDebugger?

Unlike existing quantum libraries that focus on circuit creation and execution, **QuantumDebugger** is specifically designed for:
- **Learning**: Understand how quantum algorithms work step-by-step
- **Development**: Debug complex quantum circuits efficiently
- **Research**: Analyze and optimize quantum algorithms
- **Teaching**: Demonstrate quantum concepts interactively

## 📖 Documentation

Full documentation available at: [quantum-debugger.readthedocs.io](https://quantum-debugger.readthedocs.io)

## 🌐 Links

- **GitHub**: [github.com/yourusername/quantum-debugger](https://github.com/yourusername/quantum-debugger)
- **PyPI**: [pypi.org/project/quantum-debugger](https://pypi.org/project/quantum-debugger)
- **Issues**: [Report bugs](https://github.com/yourusername/quantum-debugger/issues)

---

Made with ❤️ for the quantum computing community
