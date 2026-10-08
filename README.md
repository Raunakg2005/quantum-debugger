# Quantum Debugger

**The Most Comprehensive Quantum Machine Learning Library with AutoML**

[![Documentation Status](https://readthedocs.org/projects/quantum-debugger/badge/?version=latest)](https://quantum-debugger.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/quantum-debugger.svg)](https://pypi.org/project/quantum-debugger/)
[![Tests](https://img.shields.io/badge/tests-2468%20passing-brightgreen)](tests/README.md)
[![CI](https://github.com/Raunakg2005/quantum-debugger/workflows/Tests/badge.svg)](https://github.com/Raunakg2005/quantum-debugger/actions)
[![Codecov](https://codecov.io/gh/Raunakg2005/quantum-debugger/branch/main/graph/badge.svg)](https://codecov.io/gh/Raunakg2005/quantum-debugger)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What's New in v1.1.0

Theme: **Quantum Singular Value Transformation (QSVT) & Modern Algorithm Primitives** — the grand unification framework behind modern quantum algorithms, verified bottom-up to machine precision:

- **Quantum Signal Processing (QSP)** (`qsp_unitary`, `qsp_response`, `chebyshev_via_qsp`, `signal_operator`) — one-qubit signal transformation engine producing designable polynomials via interleaved signal and phase rotations. Zero phases recover Chebyshev polynomials $T_d(x)$ to machine precision.
- **Block Encoding & Qubitization** (`block_encode`, `qubitization_walk`, `chebyshev_of_matrix`) — embedding arbitrary non-unitary Hermitian matrices into unitaries ($\langle 0|U|0\rangle = A$), with the qubitization walk generating matrix Chebyshev polynomials $T_d(A) = \langle 0|W^d|0\rangle$.
- **Linear Combination of Unitaries (LCU)** (`lcu_block_encoding`, `lcu_matrix`) — exact PREPARE and SELECT state preparation for Pauli expansions and Hamiltonians ($H = \sum \alpha_k U_k$).
- **Quantum Singular Value Transformation (QSVT)** (`qsvt_transform`, `qsvt_scalar_response`) — the grand unification paradigm, applying polynomial matrix functions eigenvalue-by-eigenvalue ($P(A) = \sum_i P(\lambda_i)|v_i\rangle\langle v_i|$).
- **Quantum Linear Systems via QSVT** (`solve_linear_system_qsvt`, `matrix_inverse_qsvt`) — optimal polynomial inversion solving $A x = b$ without phase estimation, matching exact classical solutions.
- **Matrix Functions & Hamiltonian Simulation** (`matrix_function_chebyshev`, `hamiltonian_simulation_qsvt`, `matrix_exp_qsvt`, `matrix_log_qsvt`, `matrix_sqrt_qsvt`) — smooth matrix functions and real-time unitary evolution $e^{-i H t}$ with geometric Chebyshev convergence.
- **Spectral Filtering & Projectors** (`spectral_projector_qsvt`, `ground_state_projector_qsvt`, `bandpass_filter_qsvt`, `pseudo_inverse_qsvt`) — ground-state projection, sign functions, and regularized inverses.
- **Kernel Polynomial Method (KPM) & Spectral Estimation** (`spectral_moments`, `density_of_states_kpm`, `eigenvalue_count_in_interval`, `trace_of_function`) — Jackson-damped Chebyshev moment estimation of density of states and eigenvalue counting without full diagonalization.
- **Amplitude Amplification as QSVT** (`amplitude_amplification_qsvt`) — generalized Grover search unified under odd Chebyshev polynomials.

See the [QSVT Guide](docs/qsvt_guide.md), [Online Documentation](https://quantum-debugger.readthedocs.io/en/latest/), and [CHANGELOG.md](CHANGELOG.md).

## What's New in v1.0.0

Scale & tensor networks — **breaking the exponential state-vector wall**:

- **Matrix Product State Simulator (`MPS`)** — `O(n·χ²)` memory instead of `2ⁿ`. Represents large, lightly-entangled quantum systems (e.g. **100-qubit GHZ states**, area-law ground states) with exact single-qubit gates, SVD-truncated two-qubit gates, and long-range connectivity via SWAP networks.
- **Matrix Product Operators (`MPO`)** — compact tensor chains for TFIM (`tfim_mpo`) and Heisenberg (`heisenberg_mpo`) models; evaluate `<ψ|H|ψ>` in `O(n·χ²·D²)` time without dense matrices.
- **TEBD Real-Time Dynamics** (`tebd_tfim`, `tebd_magnetization`) — Trotterized time evolution on the MPS engine with automatic SVD bond truncation.
- **Imaginary-Time DMRG-Style Ground States** (`imaginary_tebd_ground_state`) — cool MPS into true ground states on 24+ qubit chains unreachable by dense diagonalizers.
- **Arbitrary Pauli & Energy Readout** — `MPS.expectation_pauli` and `MPS.energy` evaluate arbitrary Pauli strings and Hamiltonians by tensor contraction.
- **Born-Rule Measurement Sampling** (`MPS.sample`) — sequential conditional sampling with precomputed environments, drawing shots directly from the MPS.
- **Circuit-to-MPS Converter** (`MPS.from_circuit`) — execute `QuantumCircuit` instances directly on the tensor-network engine.

See the [Matrix Product States Guide](docs/mps_guide.md) and [CHANGELOG.md](CHANGELOG.md).

## What's New in v0.9.1

Correctness patch: **`DepolarizingNoise.get_kraus_operators()`** now implements the same
channel as `apply()` and the class docstring — the Pauli-error convention
`ρ → (1−p)ρ + (p/3)(XρX + YρY + ZρZ)` (`K₀ = √(1−p)·I`, `K₁₋₃ = √(p/3)·{X, Y, Z}`). The old
`√(p/4)` weighting made `StochasticNoiseSampler`'s Monte-Carlo depolarizing noise `4/3×` too
strong for a given `p`. Trace preservation is unchanged; channel-equivalence and sampler
regression tests added. See [CHANGELOG.md](CHANGELOG.md).

## What's New in v0.9.0

Quantum **chemistry, many-body physics & advanced simulation** — every routine verified
against a closed form or an independent computation:

- **Fermionic systems** — Jordan-Wigner transform, the Fermi-Hubbard model, and the
  Kitaev topological chain (Majorana edge modes).
- **Ground- & excited-state solvers** — chemistry via VQE with Pauli decomposition,
  imaginary-time cooling, Krylov/Lanczos, and adiabatic evolution.
- **Finite-temperature physics** — Gibbs states and thermodynamic quantities.
- **Quantum dynamics** — Trotter error scaling, the Loschmidt echo & dynamical quantum
  phase transitions, out-of-time-order correlators (scrambling), and entanglement growth.
- **Quantum chaos** — level-spacing statistics (GOE vs Poisson).
- **Metrology** — spin squeezing and mixed-state quantum Fisher information.
- **Modern measurement & tensor-network toolkit** — classical shadows, Schmidt
  decomposition, and the area law.

(Open systems, noise, and fault tolerance shipped in v0.8.0.)

See [CHANGELOG.md](CHANGELOG.md) for the full, itemized list.

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

### v0.8.0 — density-matrix engine & open systems
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

**Full Documentation & API Reference:** [https://quantum-debugger.readthedocs.io/en/latest/](https://quantum-debugger.readthedocs.io/en/latest/)

**Key Guides:**
- [QSVT & Modern Primitives Guide](docs/qsvt_guide.md) - Quantum Signal Processing, block encoding, LCU, Hamiltonian simulation, and linear systems
- [Quantum Algorithms Guide](docs/quantum_algorithms_guide.md) - Complete algorithms reference (Shor, Grover, QPE, many-body, etc.)
- [Matrix Product States Guide](docs/mps_guide.md) - 100+ qubit tensor-network simulation, TEBD, and MPO
- [Clifford / Stabilizer Guide](docs/stabilizer_guide.md) - Aaronson-Gottesman tableau simulation past the state-vector wall
- [Density Matrix Guide](docs/density_matrix_guide.md) - Open systems, Kraus operators, and Lindblad evolution
- [Error Mitigation Guide](docs/error_mitigation_guide.md) - ZNE, PEC, and Clifford Data Regression
- [GPU Acceleration Guide](docs/gpu_guide.md) - CuPy CUDA state-vector simulation
- [Transfer Learning Guide](docs/transfer_learning_guide.md) - Pretrained QNNs and model zoo
- [Circuit Optimization Guide](docs/circuit_optimization_guide.md) - Multi-level compilation and hardware transpilation
- [Hardware Backends Guide](docs/hardware_backends_guide.md) - IBM Quantum and AWS Braket

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run QSVT & modern primitives suite
pytest tests/test_qsvt.py tests/test_qsvt_applications.py tests/test_qsvt_linear_systems.py tests/test_qsp.py tests/test_block_encoding.py tests/test_lcu.py tests/test_matrix_functions.py -v

# Run specific test suites
pytest tests/qml/ -v
pytest tests/test_optimization.py -v
pytest tests/test_integrations.py -v

# With coverage
pytest tests/ --cov=quantum_debugger --cov-report=html
```

See [tests/README.md](tests/README.md) for detailed test information.

**Test Statistics (v1.1.0):**
- **2,468 comprehensive tests** passing across the repository (100% pass rate)
- Complete coverage of QSVT, QSP, LCU, block encoding, MPS, stabilizer, open systems, QML, and circuit optimization
- GPU-hardware tests require a working CUDA + CuPy install; they skip gracefully otherwise

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
  title = {Quantum Debugger: Interactive Circuit Debugging, Multi-Engine Simulation, and Quantum Machine Learning Framework},
  author = {Raunak Kumar Gupta},
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

**Documentation (ReadTheDocs):** https://quantum-debugger.readthedocs.io/en/latest/  
**PyPI:** https://pypi.org/project/quantum-debugger/  
**GitHub:** https://github.com/Raunakg2005/quantum-debugger  
**Issues:** https://github.com/Raunakg2005/quantum-debugger/issues  

---

**Version:** 1.1.0 (latest) · 1.0.1, 1.0.0, 0.9.1, 0.9.0 (previous)  
**Last Updated:** October 2026