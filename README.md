# Quantum Debugger

**The Most Comprehensive Quantum Machine Learning Library with AutoML**

[![PyPI version](https://badge.fury.io/py/quantum-debugger.svg)](https://pypi.org/project/quantum-debugger/)
[![Tests](https://img.shields.io/badge/tests-384%20passing-brightgreen)](https://github.com/Raunakg2005/quantum-debugger/blob/main/tests/FINAL_TEST_SUMMARY.md)
[![CI](https://github.com/Raunakg2005/quantum-debugger/workflows/Tests/badge.svg)](https://github.com/Raunakg2005/quantum-debugger/actions)
[![Codecov](https://codecov.io/gh/Raunakg2005/quantum-debugger/branch/main/graph/badge.svg)](https://codecov.io/gh/Raunakg2005/quantum-debugger)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A powerful Python library for quantum circuit debugging, state inspection, performance analysis, and **production-grade quantum machine learning**. From basic circuits to enterprise QML with one-line AutoML.

## What's New in v0.6.0

**ONE-LINE QUANTUM MACHINE LEARNING**

```python
# NEW: AutoML - Quantum ML for everyone
from quantum_debugger.qml.automl import auto_qnn

model = auto_qnn(X_train, y_train)
predictions = model.predict(X_test)
```

**No quantum expertise required.** AutoML automatically:
- Selects optimal number of qubits
- Chooses best ansatz architecture  
- Tunes all hyperparameters
- Finds best model configuration

### v0.6.0 Complete Feature Set

**Advanced QML (Weeks 1-3)**
- **Hybrid Models** - TensorFlow and PyTorch quantum layers
- **Quantum Kernels** - QSVM with multiple kernel types
- **Transfer Learning** - PretrainedQNN, model zoo, fine-tuning

**Production Tools (Weeks 4-5)**
- **Error Mitigation** - PEC, CDR, realistic noise models
- **Circuit Optimization** - Gate reduction, compilation, transpilation

**Universal Compatibility (Week 6)**
- **Framework Integrations** - Qiskit, PennyLane, Cirq bridges

**Hardware and Performance (Weeks 7-8)**
- **Real Quantum Computers** - IBM Quantum (FREE), AWS Braket
- **Benchmarking** - QML vs Classical performance analysis

**AutoML (Week 9)**
- **auto_qnn()** - One-line interface for quantum ML
- **Automatic Ansatz Selection** - Finds best circuit architecture
- **Hyperparameter Tuning** - Grid and random search
- **Neural Architecture Search** - Optimizes qubit and layer counts

**Jupyter Notebooks (Week 10)**
- **5 Example Notebooks** - AutoML, Transfer Learning, Hardware, Optimization, Benchmarking
- **Google Colab Compatible** - Run in browser

**Advanced Algorithms (Week 11 - NEW)**
- **Quantum GANs** - Generative adversarial networks for quantum states
- **Quantum RL** - Q-learning with quantum circuits
- **SimpleEnvironment** - Test environment for RL

**CI/CD Automation (Week 12 - NEW)**
- **GitHub Actions** - Auto-testing on Python 3.9-3.12
- **Auto-Publishing** - Automatic PyPI releases
- **Code Quality** - Linting, formatting checks

**GPU Acceleration (Week 13 - NEW)**
- **Multi-GPU** - Distribute training across GPUs (1.8-3x speedup)
- **Mixed Precision** - FP16/FP32 for 2-3x faster training
- **Memory Optimization** - Gradient checkpointing (50% reduction)
- **GPU Benchmarking** - Performance profiling tools

See [complete documentation](https://github.com/Raunakg2005/quantum-debugger#documentation) for details.

## Features

### Core Debugging
- **Step-through Debugging** - Execute circuits gate-by-gate with breakpoints
- **State Inspection** - Analyze quantum states at any point
- **Circuit Profiling** - Depth analysis, gate statistics, optimization suggestions  
- **Visualization** - State vectors, Bloch spheres, and more
- **Noise Simulation** - Realistic hardware noise models
- **Qiskit Integration** - Import/export circuits from Qiskit

### Quantum Machine Learning (v0.6.0)
- **AutoML** - One-line interface with automatic optimization
- **Advanced Algorithms** - Quantum GANs and Quantum Reinforcement Learning
- **Transfer Learning** - PretrainedQNN, model zoo, fine-tuning
- **GPU Acceleration** - Multi-GPU, mixed precision (2-3x speedup)
- **Error Mitigation** - PEC, CDR, realistic noise models  
- **Circuit Optimization** - Gate reduction, compilation, transpilation
- **Framework Bridges** - Qiskit, PennyLane, Cirq compatibility
- **Hardware Backends** - IBM Quantum (FREE), AWS Braket
- **Benchmarking** - QML vs Classical performance analysis
- **Hybrid Models** - TensorFlow and PyTorch quantum layers
- **Quantum Kernels** - QSVM with multiple kernel types
- **VQE and QAOA** - Molecular chemistry and optimization
- **Advanced Optimizers** - 7 optimizers including QNG
- **Ansatz Library** - 8 pre-built quantum circuit templates
- **Example Notebooks** - 5 comprehensive Jupyter tutorials

## Quick Start

### Installation

```bash
pip install quantum-debugger
```

### Basic Circuit Debugging

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

### Quantum Machine Learning with AutoML

```python
from quantum_debugger.qml.automl import auto_qnn
import numpy as np

# Load your data
X_train = np.random.randn(100, 4)
y_train = np.random.randint(0, 2, 100)

# One line to train quantum model
model = auto_qnn(X_train, y_train)

# Make predictions
X_test = np.random.randn(20, 4)
predictions = model.predict(X_test)
```

### Manual QNN Configuration

For more control over your quantum neural network:

```python
from quantum_debugger.qml.qnn import QuantumNeuralNetwork

# Create network
qnn = QuantumNeuralNetwork(n_qubits=4)
qnn.compile(optimizer='adam', loss='mse')

# Train
history = qnn.fit(X_train, y_train, epochs=50, batch_size=16)

# Predict
predictions = qnn.predict(X_test)
```

## Advanced Features

### Transfer Learning

```python
from quantum_debugger.qml.transfer import PretrainedQNN

# Load pretrained model
pretrained = PretrainedQNN.from_zoo('iris_classifier')

# Fine-tune on your data
pretrained.fine_tune(X_new, y_new, epochs=10, freeze_layers=2)

# Save your model
pretrained.save('models/my_qnn.pkl')
```

### Error Mitigation

```python
from quantum_debugger.qml.mitigation import PEC, CDR

# Probabilistic Error Cancellation
pec = PEC(gate_error_rates={'rx': 0.01, 'cnot': 0.02})
mitigated_result, uncertainty = pec.apply_pec(circuit)

# Clifford Data Regression
cdr = CDR(n_clifford_circuits=50)
training_data = cdr.generate_training_data(n_qubits=4, depth=3)
cdr.train(training_data, noisy_executor)
mitigated = cdr.apply_cdr(noisy_measurement)
```

### Circuit Optimization

```python
from quantum_debugger.optimization import optimize_circuit, compile_circuit

# Simple optimization
gates = [('h', 0), ('h', 0), ('x', 1)]  # H cancels itself
optimized = optimize_circuit(gates)  # Returns: [('x', 1)]

# Multi-level compilation
compiled = compile_circuit(gates, optimization_level=3)
```

### Hardware Deployment

```python
from quantum_debugger.backends import IBMQuantumBackend

# Connect to IBM Quantum (FREE tier)
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_FREE_IBM_TOKEN'})

# Execute on real quantum computer
gates = [('h', 0), ('cnot', (0, 1))]
counts = backend.execute(gates, n_shots=1024)
```

Get your free IBM Quantum token at: https://quantum.ibm.com

### Framework Integration

```python
from quantum_debugger.integrations import to_qiskit, from_qiskit, to_pennylane, to_cirq

# Convert to Qiskit
qiskit_circuit = to_qiskit(gates)

# Convert to PennyLane
pennylane_qnode = to_pennylane(gates)

# Convert to Cirq
cirq_circuit = to_cirq(gates)
```

## Installation Options

### Basic Installation

```bash
pip install quantum-debugger
```

### With Optional Dependencies

```bash
# All frameworks
pip install quantum-debugger[all]

# Individual frameworks
pip install quantum-debugger[qiskit]
pip install quantum-debugger[pennylane]
pip install quantum-debugger[cirq]
pip install quantum-debugger[tensorflow]
pip install quantum-debugger[pytorch]

# Hardware backends
pip install quantum-debugger[ibm]  # FREE
pip install quantum-debugger[aws]  # Paid service

# Development tools
pip install quantum-debugger[dev]
```

## Documentation

**v0.6.0 Guides:**
- [V0.6.0 Features](V06_FEATURES.md) - Complete feature reference
- [Transfer Learning Guide](docs/transfer_learning_guide.md)
- [Error Mitigation Guide](docs/error_mitigation_guide.md)
- [Circuit Optimization Guide](docs/circuit_optimization_guide.md)
- [Hardware Backends Guide](docs/hardware_backends_guide.md)

**v0.5.0 Guides (still valid):**
- [QNN Guide](docs/qnn_guide.md)
- [Hybrid Models Guide](docs/hybrid_models_guide.md)
- [VQE Guide](docs/vqe_guide.md)
- [QAOA Guide](docs/qaoa_guide.md)

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/qml/ -v
pytest tests/test_optimization.py -v
pytest tests/test_integrations.py -v

# With coverage
pytest tests/ --cov=quantum_debugger --cov-report=html
```

See [FINAL_TEST_SUMMARY.md](tests/FINAL_TEST_SUMMARY.md) for detailed test information.

**Test Statistics:**
- Total Tests: 384
- Status: 100% passing
- Skipped: 3 (AWS Braket - optional dependency)

## Contributing

Contributions are welcome. Please ensure:
1. All tests pass
2. Code follows PEP 8 style guidelines
3. Documentation is updated
4. New features include tests

## License

MIT License - see [LICENSE](LICENSE) file.

## Citation

If you use quantum-debugger in your research, please cite:

```bibtex
@software{quantum_debugger_2026,
  title = {Quantum Debugger: Production-Grade Quantum Machine Learning Library},
  author = {Gupta, Raunak Kumar},
  year = {2026},
  url = {https://github.com/Raunakg2005/quantum-debugger}
}
```

## Acknowledgments

**Author:** Raunak Kumar Gupta  
**GitHub:** [@Raunakg2005](https://github.com/Raunakg2005)  
**LinkedIn:** [Raunak Kumar Gupta](https://www.linkedin.com/in/raunak-kumar-gupta-7b3503270/)  
**Supervised by:** Dr. Vaibhav Prakash Vasani  
**Supervisor LinkedIn:** [Dr. Vaibhav Vasani](https://www.linkedin.com/in/dr-vaibhav-vasani-phd-460a4162/)  
**Institution:** K.J. Somaiya School of Engineering

## Links

**PyPI:** https://pypi.org/project/quantum-debugger/  
**GitHub:** https://github.com/Raunakg2005/quantum-debugger  
**Issues:** https://github.com/Raunakg2005/quantum-debugger/issues  
**Documentation:** https://github.com/Raunakg2005/quantum-debugger#readme

---

**Version:** 0.6.0  
**Status:** Production Ready  
**Last Updated:** January 14, 2026