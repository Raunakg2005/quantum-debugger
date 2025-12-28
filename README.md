# Quantum Debugger

**Interactive debugger, profiler, and quantum machine learning library for quantum circuits**

[![PyPI version](https://badge.fury.io/py/quantum-debugger.svg)](https://pypi.org/project/quantum-debugger/)
[![Tests](https://img.shields.io/badge/tests-689%20passing-brightgreen)](https://github.com/Raunakg2005/quantum-debugger/blob/main/tests/FINAL_TEST_SUMMARY.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

A powerful Python library for quantum circuit debugging, state inspection, performance analysis, and **quantum machine learning**. Now with VQE, QAOA, and parameterized quantum circuits!

## ✨ What's New in v0.5.0

**Advanced Quantum Machine Learning** 🚀

```python
# NEW: Quantum Neural Networks
from quantum_debugger.qml.qnn import QuantumNeuralNetwork, EncodingLayer, VariationalLayer

qnn = QuantumNeuralNetwork(n_qubits=4)
qnn.add(EncodingLayer(4, feature_map='zz'))
qnn.add(VariationalLayer(4, ansatz='real_amplitudes', reps=2))
qnn.compile(optimizer='adam', loss='mse', learning_rate=0.01)
history = qnn.fit(X_train, y_train, epochs=50, batch_size=16)

# NEW: Zero-Noise Extrapolation (Error Mitigation)
from quantum_debugger.qml.error_mitigation import ZeroNoiseExtrapolation

zne = ZeroNoiseExtrapolation(scale_factors=[1.0, 2.0, 3.0])
mitigated_value = zne.execute(circuit_function)

# NEW: GPU Acceleration
from quantum_debugger.backends import GPUBackend

backend = GPUBackend()  # Auto-detects GPU, falls back to CPU
state = backend.allocate_state(n_qubits=15)  # 2-5x faster on GPU
```

**v0.5.0 Features:**
- ✅ **Quantum Neural Networks** (Layer-based QML with batch training)
- ✅ **Zero-Noise Extrapolation** (Error mitigation for noisy circuits)
- ✅ **GPU Acceleration** (CuPy integration with automatic CPU fallback)
- ✅ **Advanced Ansätze** (4 new templates: RealAmplitudes, TwoLocal, etc.)
- ✅ **Dataset Integration** (CSV/JSON loading, preprocessing, feature maps)
- ✅ **Molecular Hamiltonians** (LiH, H2O, BeH2 with accurate energies)
- ✅ **Advanced Optimizers** (QNG, Nelder-Mead, L-BFGS-B)
- ✅ **190+ comprehensive tests** (all passing ✅)
- ✅ **Professional documentation** (7 detailed guides)

See full [QML Documentation](#quantum-machine-learning-v040) below.

## Features

### Core Debugging
- **Step-through Debugging** - Execute circuits gate-by-gate with breakpoints
- **State Inspection** - Analyze quantum states at any point
- **Circuit Profiling** - Depth analysis, gate statistics, optimization suggestions  
- **Visualization** - State vectors, Bloch spheres, and more
- **Noise Simulation** - Realistic hardware noise models
- **Qiskit Integration** - Import/export circuits from Qiskit

### Quantum Machine Learning (v0.5.0)
- **Quantum Neural Networks** - Layer-based deep learning on quantum hardware
- **Error Mitigation** - Zero-noise extrapolation for accurate results
- **GPU Acceleration** - Hardware-accelerated simulations (2-5x speedup)
- **VQE & QAOA** - Molecular chemistry and optimization
- **Advanced Optimizers** - 7 optimizers including quantum natural gradient
- **Ansätze Library** - 8 pre-built quantum circuit templates
- **Dataset Tools** - Loading, preprocessing, quantum feature encoding

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

### Quantum Machine Learning

```python
from quantum_debugger.qml import RXGate, RYGate, RZGate

# Parameterized quantum gate
rx = RXGate(target=0, parameter=0.5, trainable=True)
matrix = rx.matrix()  # 2x2 unitary matrix

# Update parameter during training
rx.parameter = 0.7
new_matrix = rx.matrix()  # Automatically cached for performance
```

## v0.5.0 Feature Spotlight

### 1. Quantum Neural Networks

Build and train quantum machine learning models:

```python
from quantum_debugger.qml.qnn import (
    QuantumNeuralNetwork,
    EncodingLayer,
    VariationalLayer
)

# Create network
qnn = QuantumNeuralNetwork(n_qubits=4)
qnn.add(EncodingLayer(4, feature_map='zz'))
qnn.add(VariationalLayer(4, ansatz='real_amplitudes', reps=2))

# Train
qnn.compile(optimizer='adam', loss='mse')
history = qnn.fit(X_train, y_train, epochs=50, batch_size=16)

# Predict
predictions = qnn.predict(X_test)
```

📖 **Documentation:** [QNN Guide](docs/qnn_guide.md)

### 2. Zero-Noise Extrapolation (Error Mitigation)

Reduce quantum noise effects:

```python
from quantum_debugger.qml.error_mitigation import ZeroNoiseExtrapolation

# Setup ZNE
zne = ZeroNoiseExtrapolation(
    scale_factors=[1.0, 2.0, 3.0],
    extrapolator='polynomial'
)

# Apply to circuit
mitigated_result = zne.execute(circuit_function)

# Check improvement
improvement = zne.get_improvement()
print(f"Error reduced by {improvement:.1f}%")
```

📖 **Documentation:** [ZNE Guide](docs/zne_guide.md)

### 3. GPU Acceleration

Hardware-accelerated quantum simulations:

```python
from quantum_debugger.backends import GPUBackend

# Auto-detect GPU (falls back to CPU)
backend = GPUBackend()

# Allocate on GPU
state = backend.allocate_state(n_qubits=15)

# 2-5x faster for large circuits
# Transparent API - same code for CPU/GPU
```

📖 **Documentation:** [GPU Guide](docs/gpu_guide.md)

## Quantum Machine Learning (v0.4.0+)

### 1. Parameterized Gates

**Rotation gates with trainable parameters:**

```python
from quantum_debugger.qml import RXGate, RYGate, RZGate

# Three rotation gate types
rx = RXGate(0, theta=0.5, trainable=True)   # Rotation about X-axis
ry = RYGate(0, theta=0.3, trainable=True)   # Rotation about Y-axis  
rz = RZGate(0, theta=0.7, trainable=True)   # Rotation about Z-axis

# Get unitary matrix
U = rx.matrix()  # 2x2 complex array
```

**Features:**
- Matrix caching (100-1000x speedup)
- Thread-safe operations
- Parameter validation
- Gradient tracking

### 2. VQE (Variational Quantum Eigensolver)

**Find ground state energy of molecules:**

```python
from quantum_debugger.qml import VQE, h2_hamiltonian, hardware_efficient_ansatz
import numpy as np

# Setup H2 molecule Hamiltonian
H = h2_hamiltonian()  # 2 qubits, chemistry-accurate

# Create VQE instance
vqe = VQE(
    hamiltonian=H,
    ansatz_builder=hardware_efficient_ansatz,
    num_qubits=2,
    optimizer='COBYLA',
    max_iterations=100
)

# Run optimization
initial_params = np.random.rand(2)
result = vqe.run(initial_params)

print(f"Ground state energy: {result['ground_state_energy']:.6f} Hartree")
print(f"Optimal parameters: {result['optimal_params']}")
print(f"Iterations: {result['iterations']}")

# Compare with exact solution
exact = vqe.exact_ground_state()
error = abs(result['ground_state_energy'] - exact)
print(f"Error from exact: {error:.6f} Hartree")
```

**Available Ansätze:**
- `hardware_efficient_ansatz` - RY rotations with CNOTs
- `real_amplitudes_ansatz` - Real-valued states
- `ucc_singlet_ansatz` - Chemistry-inspired
- `alternating_layered_ansatz` - RX and RY layers

### 3. QAOA (Quantum Approximate Optimization)

**Solve MaxCut on graphs:**

```python
from quantum_debugger.qml import QAOA

# Define graph (list of edges)
graph = [(0, 1), (1, 2), (2, 3), (3, 0)]  # Square graph

# Create QAOA instance
qaoa = QAOA(
    graph=graph,
    p=2,                    # 2 QAOA layers
    optimizer='COBYLA',
    max_iterations=50
)

# Run optimization
result = qaoa.run()

print(f"Best cut value: {result['best_value']:.2f}")
print(f"Optimal parameters: {result['optimal_params']}")
print(f"Approximation ratio: {result['best_value']/4:.1%}")  # 4 is optimal for square
```

**Supported graph topologies:**
- Complete graphs, Cycles, Stars
- Line graphs, Custom graphs
- Disconnected graphs

### 4. Training & Optimization

**Classical optimizers for quantum circuits:**

```python
from quantum_debugger.qml.optimizers import Adam, GradientDescent, SPSA
from quantum_debugger.qml.utils.gradients import parameter_shift_gradient

# Adam optimizer
optimizer = Adam(learning_rate=0.01)

# Training loop
params = np.array([0.5, 0.3])
for epoch in range(100):
    # Compute gradients
    grad = parameter_shift_gradient(circuit_builder, cost_function, params, 0)
    
    # Update parameters
    params = optimizer.step(params, grad)
```

**Available optimizers:**
- **Adam** - Adaptive learning rates (recommended)
- **SGD** - Stochastic gradient descent
- **SPSA** - Gradient-free, noise-tolerant
- **RMSprop** - Adaptive learning

**Gradient methods:**
- **Parameter shift rule** - Exact for quantum gates
- **Finite differences** - General purpose

### 5. Training Framework

**Complete training workflow:**

```python
from quantum_debugger.qml.training import QuantumTrainer

def circuit_builder(params):
    gates = []
    gates.append(RYGate(0, params[0]))
    gates.append(RXGate(1, params[1]))
    return gates

def cost_function(circuit):
    # Your cost calculation
    return energy

# Create trainer
trainer = QuantumTrainer(
    circuit_builder=circuit_builder,
    cost_function=cost_function,
    optimizer='adam',
    learning_rate=0.01,
    gradient_method='parameter_shift'
)

# Train
result = trainer.train(
    initial_params=np.random.rand(2),
    epochs=100,
    verbose=True
)

print(f"Final loss: {result['final_loss']:.6f}")
print(f"Training history: {len(result['history'])} epochs")
```

## 📚 Core Features

### Supported Gates

**Single-qubit:** H, X, Y, Z, S, T, RX, RY, RZ, PHASE  
**Two-qubit:** CNOT, CZ, CP (controlled-phase), SWAP  
**Three-qubit:** Toffoli (CCNOT)

### Debugging Features

- ✅ Forward/backward stepping
- ✅ Breakpoints (gate-based & conditional)
- ✅ Execution history tracking
- ✅ State comparison
- ✅ Circuit profiling

### Noise Simulation (v0.3.0)

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import IBM_PERTH_2025

# Simulate on IBM hardware
qc = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
qc.h(0).cnot(0, 1)
results = qc.run(shots=1000)
print(f"Fidelity: {results['fidelity']:.4f}")
```

**Available noise models:**
- Depolarizing, Amplitude/Phase Damping, Thermal Relaxation
- Hardware profiles: IBM, Google, IonQ, Rigetti

## 🧪 Testing & Quality

- **316/316 tests passing** (100%)
- Core logic, integration, regression, property-based tests
- Validated up to **12 qubits** (4,096-D state space)
- Numerical precision < 1e-10
- Cross-platform (Windows/Linux/macOS)
- Python 3.9-3.12 compatible

See [test files](.) for details.

## 🔧 Requirements

- Python 3.9+
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Matplotlib >= 3.5.0 (optional, for visualization)
- Qiskit >= 2.0 (optional, for integration)

## 📖 Documentation

- **Tutorials:**
  - [Parameterized Gates Tutorial](https://github.com/Raunakg2005/quantum-debugger/blob/main/tutorials/parameterized_gates_tutorial.md)
  - [VQE Preparation Guide](https://github.com/Raunakg2005/quantum-debugger/blob/main/tutorials/vqe_preparation.md)
  - [QAOA Tutorial](https://github.com/Raunakg2005/quantum-debugger/blob/main/tutorials/qaoa_tutorial.md)
  - [Noise Tutorial](https://github.com/Raunakg2005/quantum-debugger/blob/main/tutorials/noise_tutorial.md)
  - [ZNE Tutorial](https://github.com/Raunakg2005/quantum-debugger/blob/main/tutorials/zne_tutorial.md)

- **Examples:**
  - [VQE H2 Molecule](https://github.com/Raunakg2005/quantum-debugger/blob/main/examples/vqe_h2_example.py)
  - [QAOA MaxCut](https://github.com/Raunakg2005/quantum-debugger/blob/main/examples/qaoa_maxcut_example.py)
  - [QML Basic Example](https://github.com/Raunakg2005/quantum-debugger/blob/main/examples/qml_basic_example.py)

## 📈 Version History

**v0.4.0** (December 2024) - Quantum Machine Learning
- ✅ Parameterized gates (RX, RY, RZ)
- ✅ VQE algorithm for molecular chemistry
- ✅ QAOA for combinatorial optimization
- ✅ Training framework with 4 optimizers
- ✅ Gradient computation (parameter shift, finite differences)
- ✅ 316 comprehensive tests
- ✅ 3 tutorials, 4 example scripts

**v0.3.0** (December 2024) - Noise Simulation
- Realistic noise models (4 types)
- Hardware profiles (IBM, Google, IonQ, Rigetti)
- Qiskit Aer validation
- 89 new tests

**v0.2.0** - Qiskit Integration
- Bidirectional circuit conversion
- CP gate support
- 12-qubit support

**v0.1.0** - Foundation
- Core quantum simulation
- Basic debugging features

## 🗺️ Roadmap

**v0.5.0** (Q1 2025) - Advanced QML
- [ ] Quantum Neural Networks (QNN)
- [ ] More molecular Hamiltonians (LiH, H2O)
- [ ] Error mitigation integration
- [ ] GPU acceleration

**v1.0.0** (Future)
- [ ] Real hardware backend support
- [ ] Advanced visualization dashboards
- [ ] Quantum error correction tools
- [ ] Production deployment tools

## 🧪 Testing

**v0.4.2: 656 Comprehensive Tests** ✅

### Test Suite Coverage
- **Core Tests**: 441 tests (quantum operations, circuits, debugging)
- **QML Tests**: 139 tests (VQE, QAOA, training, parameterized gates)
- **Integration**: 76 tests (Cirq, Qiskit, backend validation)
- **All test files converted to pytest format**

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v          # Core unit tests
pytest tests/cirq/ -v          # Cirq integration
pytest tests/qiskit/ -v        # Qiskit integration
pytest tests/qml/ -v           # QML tests

# Run with coverage
pytest tests/ --cov=quantum_debugger --cov-report=html

# Run specific converted tests
pytest tests/unit/test_backends_advanced.py -v
pytest tests/unit/test_hardware_profiles_phase3.py -v
```

### Test Documentation
- 📊 [Complete Test Summary](https://github.com/Raunakg2005/quantum-debugger/blob/main/tests/FINAL_TEST_SUMMARY.md) - Full breakdown of all 656 tests
- 📁 [Test Structure](https://github.com/Raunakg2005/quantum-debugger/blob/main/tests/README.md) - Organization and conventions

### Test Categories
1. **Backend Tests** (59 tests) - NumPy, Sparse, GPU backends
2. **Noise Tests** (64 tests) - Noise models, hardware profiles
3. **Mitigation Tests** (28 tests) - ZNE, error mitigation
4. **Hardware Profiles** (18 tests) - AWS Braket, Azure Quantum, 2025 updates
5. **QML Tests** (139 tests) - VQE, QAOA, training framework
6. **Integration Tests** (76 tests) - Cirq, Qiskit compatibility

## 🤝 Contributing

Contributions welcome! Please ensure tests pass:

```bash
pytest tests/ -v --tb=short
```

See [Testing Section](#testing) for details.

## 📄 License

MIT License - see [LICENSE](https://github.com/Raunakg2005/quantum-debugger/blob/main/LICENSE) file.

---

## 🙏 Acknowledgments

**Author:** Raunak Kumar Gupta  
**Supervised by:** Dr. Vaibhav Prakash Vasani  
**Institution:** K.J. Somaiya School of Engineering

---

**PyPI:** https://pypi.org/project/quantum-debugger/  
**Author:** Raunak Kumar Gupta  
**Institution:** K.J. Somaiya School of Engineering  
**Version:** 0.4.2  
**Python:** 3.9+
