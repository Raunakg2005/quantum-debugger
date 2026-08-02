# Quantum Debugger Documentation

**Version 3.0.0 (development)** - Interactive quantum circuit debugger with a large, verified quantum algorithms library

Welcome to the documentation for Quantum Debugger, a Python library for quantum circuit debugging, performance analysis, and quantum machine learning.

Since v0.8 the library has grown a broad, *verified* algorithms library
(`quantum_debugger.algorithms`) spanning many-body physics, tensor networks, QSVT,
error correction and mitigation, quantum chemistry, metrology, thermodynamics, and quantum
complexity. Each area has a narrative guide (see the sidebar sections below) and a complete
[Algorithms API reference](algorithms_api); every routine is checked against a closed form or an
exact computation. The process behind this is documented in the [AI Development Lifecycle](aidlc_guide).

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

algorithms_overview
quantum_algorithms_guide
advanced_qml_guide
quantum_rl_guide
advanced_algorithms_guide
stabilizer_guide
density_matrix_guide
qec_noise_guide
mps_guide
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
:caption: Advanced Physics & Simulation (v0.9–v3.0)

many_body_guide
tensor_networks_advanced_guide
qsvt_guide
hamiltonian_simulation_adv_guide
quantum_chemistry_guide
optimization_qaoa_guide
vqa_theory_guide
metrology_guide
thermodynamics_guide
open_systems_guide
optimal_control_guide
```

```{toctree}
:maxdepth: 2
:caption: Error Correction & Mitigation (v1.2–v1.6)

error_mitigation_advanced_guide
fault_tolerant_qec_guide
ldpc_guide
```

```{toctree}
:maxdepth: 2
:caption: Information, Foundations & Complexity (v1.5–v3.0)

quantum_information_theory_guide
foundations_guide
communication_guide
complexity_guide
```

```{toctree}
:maxdepth: 2
:caption: Models, Algorithms & Compilation (v1.7–v2.8)

advanced_algorithms_2_guide
continuous_variable_guide
benchmarking_guide
compilation_guide
mbqc_guide
zx_calculus_guide
```

```{toctree}
:maxdepth: 2
:caption: Development

aidlc_guide
```

```{toctree}
:maxdepth: 2
:caption: API Reference

modules
algorithms_api
api
api_reference
qml_api
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
