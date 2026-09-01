# Quantum Debugger Documentation

**Version 1.0.1** - Interactive quantum circuit debugger with Quantum Machine Learning and Tensor Networks

Welcome to the documentation for Quantum Debugger, a Python library for quantum circuit debugging, performance analysis, quantum machine learning, and large-scale tensor-network simulation.

## What's New in v1.0.0

Scale & tensor networks — **breaking the exponential state-vector wall**:

- **Matrix Product State Simulator (`MPS`)** — `O(n·χ²)` memory instead of `2ⁿ`. Represents large, lightly-entangled quantum systems (e.g. **100-qubit GHZ states**, area-law ground states) with exact single-qubit gates, SVD-truncated two-qubit gates, and long-range connectivity via SWAP networks.
- **Matrix Product Operators (`MPO`)** — compact tensor chains for TFIM (`tfim_mpo`) and Heisenberg (`heisenberg_mpo`) models; evaluate `<ψ|H|ψ>` in `O(n·χ²·D²)` time without dense matrices.
- **TEBD Real-Time Dynamics** (`tebd_tfim`, `tebd_magnetization`) — Trotterized time evolution on the MPS engine with automatic SVD bond truncation.
- **Imaginary-Time DMRG-Style Ground States** (`imaginary_tebd_ground_state`) — cool MPS into true ground states on 24+ qubit chains unreachable by dense diagonalizers.
- **Arbitrary Pauli & Energy Readout** — `MPS.expectation_pauli` and `MPS.energy` evaluate arbitrary Pauli strings and Hamiltonians by tensor contraction.
- **Born-Rule Measurement Sampling** (`MPS.sample`) — sequential conditional sampling with precomputed environments, drawing shots directly from the MPS.
- **Circuit-to-MPS Converter** (`MPS.from_circuit`) — execute `QuantumCircuit` instances directly on the tensor-network engine.

See the [Matrix Product States Guide](mps_guide) and the
[CHANGELOG](https://github.com/Raunakg2005/quantum-debugger/blob/main/CHANGELOG.md) for the full list.

## What's New in v0.9.1

Correctness patch: `DepolarizingNoise.get_kraus_operators()` now implements the same
channel as `apply()` and the class docstring (the Pauli-error convention
`ρ → (1−p)ρ + (p/3)(XρX + YρY + ZρZ)`). The old `√(p/4)` weighting made
`StochasticNoiseSampler`'s sampled depolarizing noise `4/3×` too strong for a given `p`;
trace preservation is unchanged. See the
[CHANGELOG](https://github.com/Raunakg2005/quantum-debugger/blob/main/CHANGELOG.md).

## What's New in v0.9.0

Quantum chemistry, many-body physics & advanced simulation: fermionic systems
(Jordan-Wigner, Fermi-Hubbard, the Kitaev chain), ground/excited-state solvers
(chemistry-via-VQE, imaginary-time cooling, Krylov/Lanczos, adiabatic evolution),
finite-temperature physics (Gibbs states & thermodynamics), quantum dynamics (Trotter
error scaling, Loschmidt echo & DQPTs, OTOC scrambling, entanglement growth), quantum
chaos (level statistics), metrology (spin squeezing, mixed-state QFI), and the modern
measurement/tensor-network toolkit (classical shadows, Schmidt decomposition & the area
law). Open systems, noise, and fault tolerance shipped in v0.8.0.

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
