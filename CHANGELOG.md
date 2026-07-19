# Changelog

All notable changes to QuantumDebugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (0.7.0.dev)

Theme: performance & scale, advanced QML/QRL, plus test-suite integrity.

### Added
- **Grover adaptive minimization** (`algorithms.grover_minimize`) — Durr-Hoyer
  quantum optimization: find the argmin of a cost function via Grover search with a
  threshold oracle and BBHT-randomized iteration counts (which avoid the
  over-rotation stall when many states are marked). Reliably finds the global
  minimum, verified against brute force.
- **Multi-controlled-X synthesis** (`algorithms.toffoli_gates`, `algorithms.mcx_gates`)
  — decompose Toffoli (CCX) and general n-controlled-X gates into the elementary
  H/T/T-dagger/CNOT set; the n-control MCX uses a clean-ancilla Toffoli ladder.
  Verified exactly against the ideal CCX/MCX action with ancillas restored to |0>.
- **Grover-based constraint / SAT solver** (`algorithms.grover_solve`) — finds an
  input satisfying an arbitrary boolean predicate via Grover search over the marked
  set, returning a verified satisfying assignment, the solution count, and the
  success probability.
- **Variational ground-state solver (VQE)** (`algorithms.variational_ground_state`,
  `algorithms.tfim_hamiltonian`, `algorithms.heisenberg_hamiltonian`) — a
  self-contained hardware-efficient VQE (layered RY + CNOT ansatz, restarts) for any
  Pauli-sum Hamiltonian, checked against exact diagonalization. Recovers the TFIM and
  Heisenberg ground energies to ~1e-8 for small chains; includes ready-made TFIM and
  Heisenberg Hamiltonian builders.
- **BB84 quantum key distribution** (`algorithms.bb84`) — the first quantum
  cryptography protocol, with genuine per-qubit preparation and measurement.
  Without an eavesdropper the sifted keys match exactly (QBER 0); an
  intercept-resend eavesdropper injects a ~25% error rate that trips the security
  threshold. Security emerges from real measurement back-action.
- **Bell / CHSH inequality test** (`algorithms.chsh_value`, `algorithms.correlator`,
  `algorithms.bell_state`) — demonstrates quantum nonlocality: a Bell pair measured
  along optimal angles gives a CHSH value `S = 2 sqrt(2)`, exactly Tsirelson's bound,
  violating the classical limit `|S| <= 2`. Correlator matches `cos(a-b)`.
- **Quantum metrology** (`algorithms.phase_sensitivity`, `algorithms.parity_signal`,
  `algorithms.quantum_fisher_information`) — Heisenberg-limited phase sensing: a GHZ
  probe reaches quantum Fisher information `N^2` (phase uncertainty `1/N`) versus
  `N` (`1/sqrt(N)`) for a product state, and its parity signal oscillates as
  `cos(N*phi)`. Verified exactly for N up to 5.
- **Simon's algorithm** (`algorithms.simon`, `algorithms.simon_oracle`) — recovers
  the hidden XOR mask of a 2-to-1 function with O(n) quantum queries (exponential
  speedup). Runs the H-oracle-H circuit, collects `y . s = 0` constraints, and
  solves the GF(2) null space. Recovers every planted secret for n up to 4.
- **Entangled state preparation** (`algorithms.ghz_state`, `algorithms.w_state`,
  `algorithms.graph_state`) — genuine gate-based circuits for the canonical
  entangled states: GHZ (H + CNOT chain), W (single excitation spread evenly by a
  cascade of Givens rotations), and graph/cluster states (H on all, CZ per edge).
  Verified exactly by amplitudes / stabilizers (W fidelity 1.0 up to 6 qubits).
- **QAOA MaxCut solver** (`algorithms.solve_maxcut`, `algorithms.brute_force_maxcut`)
  — an application-level wrapper that returns an actual MaxCut solution (node
  partition, cut value, brute-force optimum, approximation ratio) with random
  restarts, not just an expected cost. Reaches the optimal cut on standard test
  graphs (square, triangle, K4, path).
- **Quantum arithmetic (Draper QFT adder)** (`algorithms.qft_add`,
  `algorithms.quantum_adder`) — carry-free addition in the Fourier basis: add a
  classical constant into a register, or add two quantum registers
  (`|a>|b> -> |a+b>|b>`). Computes `(a+b) mod 2^n` exactly for every input pair.
- **Randomized benchmarking** (`algorithms.randomized_benchmarking`,
  `algorithms.single_qubit_clifford_group`) — SPAM-independent estimate of the
  average error per single-qubit Clifford. Random Clifford sequences plus the
  exact recovery gate, a per-gate depolarizing channel, and an `A p^m + B` decay
  fit. Recovers `p ≈ 1 - lambda` and average error `≈ lambda/2`; zero noise gives
  survival 1.0, confirming the Clifford-inverse logic. Enumerates the full
  24-element single-qubit Clifford group.
- **Clifford / stabilizer simulator** (`quantum_debugger.stabilizer.StabilizerSimulator`)
  — a second simulation engine using the Aaronson-Gottesman CHP tableau
  (`O(n)`/gate, `O(n^2)`/measurement) instead of a `2^n` state vector. Supports
  H/S/X/Y/Z/CNOT/CZ + computational-basis measurement with correct random and
  deterministic outcomes, and exposes the live stabilizer generators. Runs
  hundred-qubit Clifford circuits (e.g. a 200-qubit GHZ) instantly; verified
  against the state-vector simulator (every stabilizer is a +1 eigenstate).
- **Gate decomposition / synthesis** (`algorithms.zyz_decompose`,
  `algorithms.abc_decomposition`, `algorithms.kak_decompose`,
  `algorithms.canonical_coordinates`) — single-qubit ZYZ Euler decomposition,
  Nielsen-Chuang ABC form for controlled-U, and the two-qubit Cartan (KAK)
  decomposition into local gates plus the entangling core
  `exp(i(a XX + b YY + c ZZ))`. KAK uses the magic basis + a deterministic nested
  joint diagonalization, robust even for degenerate gates; verified to reconstruct
  1000/1000 random SU(4) unitaries to ~1e-13.
- **Hamiltonian simulation (Trotter-Suzuki)** (`algorithms.trotter_evolve`,
  `algorithms.trotter_circuit`, `algorithms.hamiltonian_matrix`) — simulate
  `exp(-i H t)` for a Hamiltonian given as weighted Pauli strings, using genuine
  1- and 2-qubit gates (basis-change + CNOT-ladder + RZ per term). First- and
  second-order product formulas; second order converges faster (O(dt^2)), and
  single-term evolution is exact. Verified against the exact matrix exponential.
- **Quantum error correction** (`algorithms.bit_flip_code`,
  `algorithms.phase_flip_code`, `algorithms.shor_code`) — genuine gate-based
  stabilizer codes: encode a logical qubit, inject a Pauli error, extract the
  syndrome by measuring stabilizer generators with ancillas, and recover. The
  3-qubit codes correct any single X (bit-flip) or Z (phase-flip) error; the
  9-qubit Shor code corrects an **arbitrary** single-qubit error (X/Y/Z on any of
  the 9 qubits). Logical fidelity returns to 1.0 in every case.
- **Shor's algorithm** (`algorithms.period_finding`, `algorithms.shor_factor`) —
  quantum period finding via QPE on the modular-multiplication unitary
  `U|y> = |a*y mod N>`, with continued-fraction recovery of the period. Genuinely
  factors composites: 15 -> (3, 5) via period r=4, 21 -> (3, 7) via r=6.
- **Quantum teleportation, superdense coding & entanglement swapping**
  (`algorithms.teleport`, `algorithms.superdense_coding`,
  `algorithms.entanglement_swap`) — teleport an arbitrary single-qubit state with
  fidelity ~1.0 using a Bell pair + X/Z feedforward; superdense coding recovers all
  four 2-bit messages from a single transmitted qubit; entanglement swapping
  entangles two qubits that never interacted (fidelity 1.0 to |Phi+>), the basis of
  quantum repeaters.
- **HHL quantum linear-systems solver** (`algorithms.hhl`) — solves `A x = b` for
  a small Hermitian `A` via QPE + eigenvalue-inversion rotation + inverse QPE +
  post-selection; the solution state matches the classical `A^{-1} b` with
  fidelity ~1.0.
- **Quantum State Tomography** (`quantum_debugger.tomography.state_tomography`) —
  reconstructs a <=3-qubit density matrix from simulated Pauli measurements
  (fidelity ~1.0 to the true state).
- **Amplitude Amplification** (`algorithms.amplitude_amplification`) — generalizes
  Grover to any state preparation A; boosts a marked-state probability of 0.001
  to ~1.0.
- **Quantum Actor-Critic (A2C)** (`qml.algorithms.QuantumActorCritic`) — online
  advantage actor-critic with a PQC actor and a PQC critic; the critic learns a
  genuine value function (V increases toward the goal). Completes the QRL suite
  (value-based, policy-based, actor-critic).
- **Multi-class Variational Quantum Classifier**
  (`qml.advanced.VariationalQuantumClassifier`) — K-class softmax readout with
  cross-entropy + parameter-shift training (~0.98 on 3-class data).
- **Iterative QPE** (`algorithms.iterative_phase_estimation`) — single-ancilla,
  bit-by-bit phase estimation (Kitaev); recovers representable phases exactly.
- **SPSA optimizer** (`qml.optimizers.SPSA`) — gradient-free, two objective
  evaluations per step regardless of parameter count (ideal for VQAs).
- **Maximum-Likelihood Amplitude Estimation** (`algorithms.amplitude_estimation`)
  — QPE-free amplitude/count estimation via Grover powers + max-likelihood; more
  accurate than QPE-based counting (counts recovered to <0.6).
- **VQD (Variational Quantum Deflation)** (`qml.algorithms.VQD`) — finds excited
  states, not just the ground state, by penalizing overlap with previously found
  eigenstates. Recovers exact ground + excited energies on test Hamiltonians.
- **Quantum walk** (`algorithms.quantum_walk`) — discrete-time coined walk on a
  cycle; spreads ballistically (std ~ steps) vs a classical walk's sqrt(steps).
- **Quantum counting** (`algorithms.quantum_counting`) — estimates the number of
  marked states via QPE on the Grover iterate.
- **Quantum algorithms library** (`quantum_debugger.algorithms`) — textbook
  algorithms as first-class, tested functions: **QFT / inverse QFT** (matches the
  analytic DFT), **Grover search** (finds marked states at ~94% in the optimal
  number of iterations), **Quantum Phase Estimation** (exact phase readout),
  **Bernstein-Vazirani** (recovers the hidden string in one query), and
  **Deutsch-Jozsa** (constant vs balanced). All genuinely gate-based.
- **Quantum Autoencoder** (`qml.advanced.QuantumAutoencoder`) — compresses
  n qubits into fewer by training the trash qubits toward |0> with parameter-
  shift gradients (trash fidelity ~0.45 -> ~1.0 on compressible data).
- **Quantum Convolutional Neural Network** (`qml.advanced.QCNN`) — convolution +
  pooling layers that halve the qubits toward a single readout; learns separable
  data to 100%.
- **Quantum Policy Gradient (REINFORCE)** — a policy-based QRL agent with a PQC
  policy (state encoding + variational ansatz + softmax over per-action <Z>
  readouts), trained with exact parameter-shift policy gradients. Learns the
  gridworld to the optimal policy. (`qml.algorithms.QuantumPolicyGradient`)
- **Quantum DQN** — value-based QRL with an experience-replay buffer and a
  periodically-synced target network on top of the PQC Q-function; converges
  faster/more stably than plain Q-learning. (`qml.algorithms.QuantumDQN`)
- **Data-reuploading classifier** — re-encodes inputs between variational layers
  (Perez-Salinas et al.) for higher expressivity; learns nonlinearly-separable
  data (concentric circles ~0.9 acc) that single-encoding circuits cannot.
  (`qml.advanced.DataReuploadingClassifier`)
- **Ansatz analysis toolkit** — `expressibility` (KL to the Haar fidelity
  distribution, Sim et al.), `entangling_capability` (Meyer-Wallach Q), and
  `gradient_variance` (barren-plateau probe, McClean et al.), each validated
  against the expected theoretical behavior. (`qml.advanced`)

### Changed
- **`QuantumCircuit.run()` simulates once and samples all shots** from the
  resulting distribution, instead of re-simulating the whole circuit for every
  shot (was O(shots x gates), now O(gates + shots)). Statistically identical for
  independent projective Z-measurements; 20k shots on a 10-qubit circuit now
  runs in ~50 ms. `run()` also accepts `use_gpu` / `precision`.

### Fixed
- **Test integrity**: ~116 legacy tests across 10 files signalled pass/fail via
  `return True/False`, which pytest ignores -- so they passed vacuously. Converted
  to real `assert`s (all still pass, confirming the checks genuinely hold) and
  removed the `PytestReturnNotNoneWarning`s.
- Registered the `aws` pytest marker (`pytest.ini`) so `-m "not aws"` is clean.

## [0.6.1] - 2026-07-16

Release-hardening pass focused on correctness, performance, and robustness. No
breaking API changes.

### Added
- **GPU state-vector simulation**: `QuantumCircuit.get_statevector(use_gpu=True,
  precision='single'|'double')` runs the entire circuit on the GPU (CuPy) — the
  state lives on the device across all gates with a single transfer back.
  Verified identical to CPU in double precision; measured ~6x (double) and
  50-75x (single) vs CPU at 20-22 qubits on an RTX 5060.
- **Automatic Windows CUDA DLL discovery** so the GPU backend works out of the
  box with the `cupy-cuda12x` + `nvidia-*-cu12` pip wheel setup.

### Fixed
- **Import robustness**: a broken or version-incompatible optional dependency
  (e.g. PennyLane against a mismatched JAX) no longer crashes
  `import quantum_debugger`. Optional-integration guards now degrade gracefully
  to `<FRAMEWORK>_AVAILABLE = False` instead of only catching `ImportError`.
- **QNN training**: `QuantumNeuralNetwork.fit` now uses the compiled optimizer
  (Adam / SGD) instead of a hardcoded `params -= 0.01 * gradient` that ignored
  `compile(...)`. Training now actually converges.
- **QNN readout**: the network output is now a proper Pauli-Z expectation
  `<Z_0>` over the full distribution, rather than `P(|0...0>) - P(|1...1>)`
  which discarded almost all amplitudes for >2 qubits.
- **AutoML**: `AutoQNN` now selects models on a held-out validation split (was
  scoring on the training data — leakage) and refits the winning configuration
  on all data.
- **QAOA**: the cost layer now applies genuine two-qubit ZZ interactions
  (CNOT·RZ·CNOT) instead of single-qubit RZ rotations, so the ansatz can
  entangle and reach the true MaxCut optima.
- **Hybrid (PyTorch)**: fixed a shape-mismatch crash in `HybridQNN` caused by a
  duplicated output projection, and replaced the all-zero backward pass with
  finite-difference gradients so the quantum layer (and any preceding classical
  layers) actually train.
- Corrected two test bugs exposed once the suite became collectable
  (a swapped-argument `rx` call and a sign error in a QAOA convergence check).
- **Windows CUDA DLL discovery**: with the common `cupy-cuda12x` + `nvidia-*-cu12`
  wheel setup, the CUDA DLLs live under `site-packages/nvidia/*/bin` and are not
  on the Windows DLL search path, so CuPy failed to load `nvrtc`/`cublas`. The
  backend now adds those directories to `PATH` and the DLL search list before
  importing CuPy, so the GPU backend works out of the box (verified on an
  RTX 5060 / sm_120).

### Reworked — placeholder features are now genuinely quantum
Several advertised features previously returned classical surrogates, random
values, or zero gradients. They are now real implementations, each verified:
- **Quantum fidelity kernel / QSVM**: `FidelityKernel` computes
  `|<phi(x1)|phi(x2)>|^2` by simulating the real feature-map circuits (was a
  classical RBF). Gram matrix verified symmetric, unit-diagonal, PSD.
  `ProjectedKernel` is now the real reduced-density-matrix kernel.
- **Hybrid quantum layer** (`QuantumMiddleLayer`): forward is now a real
  encoding + variational circuit measured in Z (was `cos(x + params)`), with
  exact parameter-shift gradients wired into the PyTorch and TensorFlow layers
  (were all-zero gradients). Gradients verified against finite differences.
- **Quantum GAN**: real variational generator circuit and a trainable
  discriminator with exact BCE gradients (was a global-phase no-op generator and
  a random discriminator). Generator demonstrably learns a target distribution.
- **Quantum RL**: real parameterized-circuit Q-function with parameter-shift TD
  updates (was `tanh` of a dot product). Agent learns the gridworld to optimum.
- **Error mitigation**: genuine PEC (quasi-probability Monte Carlo that recovers
  the ideal expectation), CDR (exact Clifford simulation + regression), Quantum
  Natural Gradient (true Fubini-Study metric, matches analytic values), and ZNE
  noise scaling by real unitary folding (preserves the logical unitary).
- **GPU module**: `DistributedQNN`/`DataParallelQNN` now genuinely train via real
  data-parallel gradient averaging (base class no longer raises
  `NotImplementedError`); mixed-precision `train_step` uses a real gradient (was
  random). Multi-GPU wall-clock speedup still requires GPU hardware.

### Changed
- **Core simulator performance**: `QuantumState.apply_gate` now applies gates by
  tensor contraction (O(2**n) per gate) instead of materializing the full
  2**n x 2**n operator (O(4**n)). Results are numerically identical (verified
  against the previous implementation over thousands of random configurations);
  16-qubit circuits that were previously infeasible now run in tens of ms.
- Reconciled version metadata: `__version__` is the single source of truth and
  `setup.py` reads it (previously `0.4.2` in the package vs `0.6.0` in setup).

## [0.4.2] - 2025-12-22

### Added
- **Complete pytest migration**: All 200 legacy script-style tests converted to pytest format
- **Hardware profiles extended**: AWS Braket, Azure Quantum provider support
- **2025 hardware updates**: IBM Heron, Google Willow, IonQ Forte profiles
- **Advanced backend tests**: 8 edge case and performance tests
- **GPU backend support**: CuPy backend availability testing
- **Enhanced test coverage**: 656 comprehensive tests (all passing ✅)

### Changed
- Migrated all legacy test files from script execution to pytest format
- Updated test structure for better CI/CD compatibility
- Enhanced backend validation with 6 comprehensive backend tests
- Improved hardware profile testing (18 tests total)

### Fixed
- Test suite compatibility issues
- Backend detection for GPU/CuPy
- Hardware profile version tracking

### Documentation
- Updated README.md with v0.4.2 features and test count
- Added comprehensive testing section in README
- Created FINAL_TEST_SUMMARY.md with complete 656 test breakdown
- Fixed all documentation links (tutorials, examples, LICENSE)
- Updated version numbers across all files

### Testing
- **656 total tests** (all passing ✅)
- All script-style tests converted to pytest
- Complete test coverage documentation

## [0.4.1] - 2024-12-XX

### Added
- Additional QML features and optimizations
- Performance improvements

## [0.4.0] - 2024-12-XX

### Added
- **Quantum Machine Learning Module**
- Parameterized gates (RX, RY, RZ with trainable parameters)
- VQE algorithm for molecular chemistry
- QAOA for combinatorial optimization
- Training framework with 4 optimizers (Adam, SGD, SPSA, RMSprop)
- Gradient computation (parameter shift rule, finite differences)
- 316 comprehensive tests
- 3 tutorials, 4 example scripts

### Changed
- Enhanced circuit profiling
- Improved state visualization

## [0.3.0] - 2024-12-XX

### Added
- Realistic noise models (4 types)
- Hardware profiles (IBM, Google, IonQ, Rigetti)
- Qiskit Aer validation
- 89 new tests

## [0.2.0] - 2024-XX-XX

### Added
- Bidirectional circuit conversion with Qiskit
- CP gate support
- 12-qubit support

## [0.1.1] - 2024-12-03

### Fixed
- Fixed SWAP gate matrix for little-endian qubit ordering
- Fixed CNOT gate matrix for little-endian qubit ordering
- Fixed Toffoli gate matrix for little-endian qubit ordering
- Fixed entanglement detection for Bell states
- Rewrote multi-qubit gate expansion algorithm using tensor products

### Added
- 69 comprehensive tests (100% pass rate)
- Test suites: quickstart, advanced, comprehensive, extreme, validation, production, edge cases
- Numerical stability tests (100+ consecutive operations)
- Quantum mechanics validation tests
- Production readiness tests

### Changed
- Improved gate expansion algorithm for better accuracy
- Enhanced test coverage to 69 tests across 7 test suites

## [0.1.0] - 2024-11-30

### Added
- Initial release
- Core quantum state representation
- 15+ quantum gates (H, X, Y, Z, S, T, RX, RY, RZ, PHASE, CNOT, CZ, SWAP, Toffoli)
- Step-through debugger with breakpoints
- Circuit profiler with optimization suggestions
- State visualization tools
- Bloch sphere representation
- Support for up to 15 qubits
- Example circuits and demos
- Comprehensive documentation
