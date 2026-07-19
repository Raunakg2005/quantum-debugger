# Quantum Debugger Documentation

**Version 0.7.0 (development)** - Interactive quantum circuit debugger with Quantum Machine Learning

Welcome to the documentation for Quantum Debugger, a Python library for quantum circuit debugging, performance analysis, and quantum machine learning.

## What's New in v0.7.0 (in development)

A large, genuinely gate-based **quantum algorithms library** (`quantum_debugger.algorithms`),
every routine verified against its known outcome:

- **Textbook algorithms** — QFT, Grover, Quantum Phase Estimation (+ iterative),
  Bernstein-Vazirani, Deutsch-Jozsa, quantum walk, quantum counting, amplitude
  estimation/amplification, HHL linear solver, swap test.
- **Shor's algorithm** — quantum period finding that genuinely factors (15 → 3×5,
  21 → 3×7).
- **Quantum error correction** — 3-qubit bit-flip / phase-flip codes and the
  9-qubit Shor code (corrects an arbitrary single-qubit error) with real
  stabilizer syndrome extraction.
- **Clifford / stabilizer simulator** — a second engine (CHP tableau) that runs
  hundred-qubit Clifford circuits instantly.
- **Hamiltonian simulation** (Trotter-Suzuki), **gate decomposition** (ZYZ, ABC,
  two-qubit KAK), **randomized benchmarking**, **Draper QFT adder**, a **QAOA
  MaxCut solver**, entangled **state preparation** (GHZ/W/graph), teleportation,
  superdense coding, and **state tomography**.
- **Advanced QML/QRL** — VQD excited states, quantum autoencoder, QCNN,
  data-reuploading classifier, multi-class VQC, ansatz analysis, SPSA, plus
  Policy Gradient, DQN, and Actor-Critic reinforcement learning.

See the [Algorithms guide](quantum_algorithms_guide) and the
[CHANGELOG](https://github.com/Raunakg2005/quantum-debugger/blob/main/CHANGELOG.md)
for the full list.

## What's New in v0.6.1

- **Faster simulator** - gate application is O(2ⁿ) per gate (was O(4ⁿ)), plus
  optional **GPU state-vector simulation** (`get_statevector(use_gpu=True)`).
- **Genuinely quantum QML** - the quantum kernel/QSVM, hybrid PyTorch/TensorFlow
  layers, Quantum GAN, Quantum RL, and error mitigation (PEC, CDR, QNG, ZNE) are
  now real circuit-based implementations with real gradients (each verified).
- **Robust imports** - a broken optional dependency no longer breaks
  `import quantum_debugger`.

See the [CHANGELOG](https://github.com/Raunakg2005/quantum-debugger/blob/main/CHANGELOG.md) for the full list.

## Features

- 🐛 Step-through debugging
- 🔍 State inspection
- 📊 Circuit profiling
- 🚀 GPU-accelerated state-vector simulation (CuPy)
- 🔗 Qiskit / PennyLane / Cirq integration
- 🧠 Quantum Machine Learning (QNN, AutoML, quantum kernels, hybrid models)
- ⚗️ VQE for molecular chemistry
- 🎯 QAOA for optimization (with a MaxCut solver)
- 📚 Quantum algorithms library (Shor, Grover, QPE, HHL, QEC, Trotter, ...)
- 🧮 Clifford / stabilizer simulator (hundreds of qubits)

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

### GPU-Accelerated Simulation

```python
from quantum_debugger import QuantumCircuit

qc = QuantumCircuit(20)
for q in range(20):
    qc.h(q)
for q in range(19):
    qc.cnot(q, q + 1)

# Run the whole circuit on the GPU (requires CuPy + a CUDA GPU).
# precision='single' (complex64) is dramatically faster on consumer GPUs;
# 'double' (complex128, default) is bit-identical to the CPU result.
state = qc.get_statevector(use_gpu=True, precision="single")
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
:caption: Algorithms & Advanced QML

quantum_algorithms_guide
advanced_qml_guide
quantum_rl_guide
advanced_algorithms_guide
stabilizer_guide
```

```{toctree}
:maxdepth: 2
:caption: Quantum Machine Learning

qnn_guide
hybrid_models_guide
quantum_kernels_guide
ansatz_guide
optimizers_guide
dataset_guide
hamiltonians_guide
transfer_learning_guide
```

```{toctree}
:maxdepth: 2
:caption: Error Mitigation & Noise

error_mitigation_guide
zne_guide
hardware_profiles
```

```{toctree}
:maxdepth: 2
:caption: Hardware & Performance

gpu_guide
hardware_backends_guide
circuit_optimization_guide
```

```{toctree}
:maxdepth: 2
:caption: API Reference

modules
api
api_reference
qml_api
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
