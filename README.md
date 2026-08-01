# Quantum Debugger

**A comprehensive quantum simulation & debugging toolkit — four engines, a large verified algorithm library, error correction, QSVT, and quantum machine learning.**

[![PyPI version](https://badge.fury.io/py/quantum-debugger.svg)](https://pypi.org/project/quantum-debugger/)
[![Tests](https://img.shields.io/badge/tests-2000%2B%20passing-brightgreen)](https://github.com/Raunakg2005/quantum-debugger/blob/main/tests/FINAL_TEST_SUMMARY.md)
[![CI](https://github.com/Raunakg2005/quantum-debugger/workflows/Tests/badge.svg)](https://github.com/Raunakg2005/quantum-debugger/actions)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python library for quantum circuit debugging, state inspection, and simulation across **four engines** — dense state-vector, Clifford/stabilizer (hundreds of qubits), density-matrix (open systems), and matrix-product-state (tensor networks) — plus a large, individually-verified quantum-algorithms library and quantum machine learning.

## What's New (v0.8 → v3.2, in development)

The library grew from a state-vector simulator into a full quantum-computing stack.
Every routine below is verified against a closed form, an exact computation, or the
state-vector engine.

- **Four simulation engines** — dense state-vector; **Clifford/stabilizer** (CHP
  tableau, hundred-qubit circuits, tableau entanglement entropy); **density-matrix**
  (Kraus channels, Lindblad evolution, Choi/CPTP, process tomography, discord,
  negativity, concurrence); and a **matrix-product-state** engine (`quantum_debugger.mps`)
  that holds a 100-qubit GHZ in a handful of tensors, with TEBD real- and
  imaginary-time evolution.
- **Quantum error correction** — the `[[5,1,3]]`, Steane `[[7,1,3]]` (with transversal
  gates), `[[4,2,2]]`, and 9-qubit Shor codes; QEC under continuous noise with exact
  syndrome recovery; the **toric code** with a minimum-weight-matching decoder; magic
  states, distillation, and the Petz recovery map.
- **Chemistry & many-body** — Jordan-Wigner, Fermi-Hubbard, the Kitaev topological
  chain; ground states by VQE, imaginary-time, and Krylov/Lanczos; Gibbs states and
  thermodynamics; quench dynamics (Loschmidt echo, OTOC scrambling, entanglement
  growth) and quantum-chaos level statistics.
- **QSVT & modern primitives** — quantum signal processing, block encoding, LCU, and
  Quantum Singular Value Transformation, with **Hamiltonian simulation** and **quantum
  linear systems** falling out of the one framework.
- **Error mitigation** — readout mitigation, zero-noise extrapolation, probabilistic
  error cancellation, virtual distillation, symmetry verification, Pauli twirling, and
  Clifford Data Regression.
- **Foundations** — Bell/CHSH & Horodecki nonlocality, contextuality, geometric phase,
  uncertainty relations, weak values, Holevo bound, channel capacity, state
  discrimination, no-cloning, magic measures, and quantum metrology.
- **Optimization & variational theory** — QUBO/Ising encodings & QAOA theory, adiabatic
  optimization and quantum annealing; parameter-shift gradients, barren plateaus,
  expressibility, quantum natural gradient, and entangling capability.
- **Simulation & compilation** — Trotter-Suzuki/qDRIFT/Taylor Hamiltonian simulation with
  rigorous error bounds; a circuit IR with routing, scheduling, gate cancellation, and
  verified templates; quantum volume, XEB, and randomized benchmarking.
- **Communication, networks & MBQC** — channel capacities, advanced QKD (BB84/E91/six-state,
  decoy states), quantum repeaters; PEPS/MERA tensor networks; measurement-based (one-way)
  computing with graph states and causal flow.
- **Metrology, thermodynamics & complexity** — quantum Fisher information and
  Heisenberg-limited sensing; quantum thermodynamics (Jarzynski/Crooks, Landauer, the Otto
  engine, ergotropy); and the v3.0 **quantum-complexity** milestone (Boolean-function
  complexity, query/communication separations, and complexity-class containments).
- **Open quantum systems (v3.1)** — the Lindblad master equation and Liouvillian spectra,
  quantum-trajectory (Monte Carlo wavefunction) unravelings, the Breuer-Laine-Piilo
  non-Markovianity measure, collision-model thermalization, and closed-form qubit T1/T2
  relaxation.
- **Quantum optimal control (v3.2)** — GRAPE pulse synthesis of target gates (fidelity → 1),
  dynamical-Lie-algebra controllability, the Mandelstam-Tamm / Margolus-Levitin quantum speed
  limits, and the pulse-area theorem with square/Gaussian/DRAG envelopes.
- **Docs & process** — narrative guides for every advanced theme plus a complete autodoc
  [Algorithms API reference](docs/algorithms_api.md), and an
  [AI Development Lifecycle](docs/aidlc_guide.md) (see [`AGENTS.md`](AGENTS.md)) that
  formalizes the *verify-never-fake* workflow behind the library.

See [CHANGELOG.md](CHANGELOG.md) for the full, per-version list.

## What's New in v0.7.0 (in development)

A large, genuinely gate-based **quantum algorithms library** (`quantum_debugger.algorithms`),
every routine verified against its known outcome:

- **Shor's algorithm** — quantum period finding that genuinely factors (15 → 3×5, 21 → 3×7).
- **Quantum error correction** — 3-qubit bit-flip / phase-flip codes and the 9-qubit
  Shor code (corrects an arbitrary single-qubit error) with real stabilizer syndromes.
- **Clifford / stabilizer simulator** — a second engine (CHP tableau) that runs
  hundred-qubit Clifford circuits instantly.
- **Hamiltonian simulation** (Trotter-Suzuki), **gate decomposition** (ZYZ / ABC / KAK),
  **randomized benchmarking**, **Draper QFT adder**, a **QAOA MaxCut solver**,
  entangled **state preparation** (GHZ / W / graph), **teleportation**, **superdense
  coding**, **state tomography**, plus the textbook set (QFT, Grover, QPE, HHL,
  Bernstein-Vazirani, Deutsch-Jozsa, quantum walk/counting, amplitude estimation).
- **Advanced QML/QRL** — VQD excited states, quantum autoencoder, QCNN,
  data-reuploading classifier, multi-class VQC, ansatz analysis, SPSA, plus Policy
  Gradient, DQN, and Actor-Critic reinforcement learning.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

## What's New in v0.7.0

A **second simulation engine** plus a large, verified quantum-algorithms library:
- **Clifford / stabilizer simulator** (`StabilizerSimulator`) — the
  Aaronson-Gottesman tableau: GHZ, graph/cluster states, and randomized
  benchmarking on **hundreds of qubits** instantly, far past the state-vector wall.
- **Big algorithms library** — Shor factoring, Simon, quantum error correction
  (bit-flip / phase-flip / the 9-qubit Shor code), Trotter Hamiltonian simulation,
  gate decomposition (ZYZ/KAK), quantum arithmetic (Fourier + ripple-carry adders),
  teleportation / superdense / entanglement swapping, Bell-CHSH & GHZ-Mermin
  nonlocality, and BB84 QKD — each verified against its known outcome.
- **VQE** ground-state solver converges to machine precision on larger chains
  (BFGS optimizer).

### In development (0.8.0-dev)
- **Density-matrix simulator** (`DensityMatrix`) — open quantum systems with Kraus
  channels, Lindblad master-equation evolution, and channel metrics (process /
  average gate fidelity, Choi matrix, CPTP checks).
- **QEC under continuous noise** — a code run against an independent bit-/phase-flip
  channel on every qubit, exactly, with CPTP syndrome recovery.
- **Quantum multiplier** and a **ripple-carry subtractor**.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

## What's New in v0.6.1

Correctness, performance, and "make the advertised features real" release:
- **Faster core** - gate application is now O(2ⁿ) per gate (was O(4ⁿ)); optional
  **GPU state-vector simulation** (`get_statevector(use_gpu=True)`, up to ~50-75x
  at 20+ qubits in single precision).
- **Genuinely quantum QML** - the quantum kernel/QSVM, hybrid PyTorch/TF layers,
  Quantum GAN, Quantum RL, and error mitigation (PEC, CDR, QNG, ZNE) are now real
  circuit-based implementations with real gradients, each verified — not the
  classical/placeholder stand-ins they were before.
- **Robust imports** - a broken optional dependency no longer breaks
  `import quantum_debugger`.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

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

**GPU Acceleration (v0.6.1)**
- **GPU state-vector simulation** - `circuit.get_statevector(use_gpu=True)` runs
  the whole circuit on the GPU (CuPy). Measured on an RTX 5060 vs CPU: ~6x in
  double precision, and 50-75x in single precision (`precision='single'`) at
  20-22 qubits, where the CPU becomes the bottleneck.
- **Distributed / mixed-precision training** - real data-parallel gradient
  averaging and mixed-precision steps. (Multi-GPU wall-clock speedup requires
  multiple physical GPUs; on one device these run correctly but sequentially.)
- **Windows-friendly** - auto-discovers pip-installed CUDA runtime wheels
  (`nvidia-*-cu12`) so the GPU backend works without a manual CUDA toolkit setup.

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

**Advanced algorithm guides (v0.9 → v3.1)** — one narrative guide per theme, each with runnable,
verified examples, plus a complete autodoc API reference:
- [Many-body physics](docs/many_body_guide.md) ·
  [Tensor networks II](docs/tensor_networks_advanced_guide.md) ·
  [QSVT](docs/qsvt_guide.md) ·
  [Hamiltonian simulation](docs/hamiltonian_simulation_adv_guide.md)
- [Quantum chemistry](docs/quantum_chemistry_guide.md) ·
  [Optimization & QAOA](docs/optimization_qaoa_guide.md) ·
  [VQA theory](docs/vqa_theory_guide.md) ·
  [Metrology](docs/metrology_guide.md) ·
  [Thermodynamics](docs/thermodynamics_guide.md) ·
  [Open quantum systems](docs/open_systems_guide.md) ·
  [Optimal control](docs/optimal_control_guide.md)
- [Error mitigation II](docs/error_mitigation_advanced_guide.md) ·
  [Fault-tolerant QEC](docs/fault_tolerant_qec_guide.md) ·
  [Quantum information](docs/quantum_information_theory_guide.md) ·
  [Foundations](docs/foundations_guide.md) ·
  [Communication](docs/communication_guide.md) ·
  [Complexity](docs/complexity_guide.md)
- [Advanced algorithms II](docs/advanced_algorithms_2_guide.md) ·
  [Continuous-variable](docs/continuous_variable_guide.md) ·
  [Benchmarking](docs/benchmarking_guide.md) ·
  [Compilation](docs/compilation_guide.md) ·
  [MBQC](docs/mbqc_guide.md)
- **[Full algorithms API reference](docs/algorithms_api.md)** ·
  **[AI Development Lifecycle](docs/aidlc_guide.md)** (the verify-never-fake workflow)

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

**Test Statistics (v1.3.0-dev):**
- 2000+ core tests passing (`pytest tests/ -m "not aws" --ignore=tests/qml`), plus ~400 QML tests
- GPU-hardware tests require a working CUDA + CuPy install; they skip otherwise
- A few tests are performance/timing based and may vary by machine

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

**Version:** 0.7.1 (on PyPI) · 0.8.0 → 3.2.0 (in development, staged for release)  
**Last Updated:** July 2026