# Changelog

All notable changes to QuantumDebugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (0.8.0.dev)

### Added
- **DEJMPS distillation** (`algorithms.dejmps_distill`, `bell_diagonal_state`,
  `dejmps_recurrence`, `dejmps_rounds`) — the protocol real repeaters use: works on
  *any* Bell-diagonal state (BBPSSW needs Werner) via local `Rx(±pi/2)` rotations
  before the bilateral CNOTs. The exact 4-qubit circuit reproduces the Deutsch et al.
  four-coefficient recurrence to machine precision (all Bell weights, plus success
  probability `(l1+l4)^2 + (l2+l3)^2`); on Werner inputs it reduces exactly to
  BBPSSW, and on an asymmetric state of the same fidelity it purifies strictly
  faster (0.845 vs 0.735 in one round from F = 0.7). Bell-diagonal states are closed
  under the map, so `dejmps_rounds` iterates the exact recurrence to a target.
- **GHZ vs W robustness under particle loss** (`algorithms.loss_robustness`) —
  the standard demonstration that how entanglement is *shared* matters: tracing one
  qubit out of an n-qubit GHZ leaves a fully separable mixture (negativity exactly 0,
  though the intact state is maximally entangled at 1/2), while a W state's surviving
  pair stays entangled with negativity exactly `(sqrt((n-2)^2+4) - (n-2))/(2n)` —
  the golden value `(sqrt(5)-1)/6` at n=3 — verified for n = 3..6, diluting but never
  vanishing as n grows.
- **Quantum Zeno effect** (`algorithms.quantum_zeno`, `zeno_postselected`) —
  frequent measurement freezes coherent evolution. A Rabi drive interrupted by N
  unread projective measurements (exact measurement channels on the density matrix)
  leaves `|0>` population exactly `1/2 + cos^N(wT/N)/2`; demanding outcome 0 every
  time survives with probability exactly `cos^{2N}(wT/2N)` with the state pinned at
  `|0>`. Both verified against their closed forms, monotone in N, tending to 1 —
  while a free pi-pulse fully inverts the qubit (survival 0), 50 interleaved
  measurements keep it above 0.95.
- **Dynamical decoupling (Hahn spin echo)** (`algorithms.spin_echo`,
  `echo_state_fidelity`) — the temporal counterpart to a DFS: under quasi-static
  dephasing (random per-shot detuning, Gauss-Hermite ensemble of unitaries) a bare
  `|+>` decays as `exp(-sigma^2/2)`, but an X pulse at mid-evolution refocuses the
  phase (`U(phi/2) X U(phi/2) = X` shot by shot) and restores coherence to exactly 1
  at any noise strength — for arbitrary input states. Crucially also verified where
  the echo *fails*: if the noise re-randomizes between the two halves, the echoed
  decay is exactly `exp(-sigma^2/2)` — no advantage. Noise *correlation* is the
  resource dynamical decoupling consumes.
- **Decoherence-free subspaces** (`algorithms.collective_dephasing`, `dfs_encode`,
  `dfs_protection`) — protection by symmetry instead of redundancy: under collective
  Gaussian dephasing (the same random Z phase on every qubit, computed as an exact
  Gauss-Hermite ensemble average of unitaries), a logical qubit encoded in
  `span{|01>, |10>}` keeps fidelity exactly 1 at ANY noise strength, while a bare
  `|+>` qubit's coherence dies as `exp(-sigma^2/2)` and an `a|00> + b|11>` qubit
  decays four times faster (`exp(-2 sigma^2)`) — all three verified against their
  closed forms.
- **Noisy entanglement swapping & repeater chains**
  (`algorithms.entanglement_swap_noisy`, `repeater_chain`) — a Bell measurement at a
  middle node splices two noisy Werner pairs A-B, B-C into an A-C pair of fidelity
  `F1·F2 + (1-F1)(1-F2)/3`, exact for every measurement outcome (each probability
  1/4), run as the 4-qubit density-matrix circuit with Pauli corrections. Since
  Werner⊗Werner swaps to Werner again, the scalar recurrence composes exactly:
  `repeater_chain` gives the end-to-end fidelity of an n-link chain, decaying toward
  1/4. Verified highlights: two *entangled* pairs (0.7, 0.6) swap to a *separable*
  0.46 pair (cross-checked via negativity), and one BBPSSW round rescues a degraded
  chain — the complete quantum-repeater story.
- **Entanglement distillation (BBPSSW)** (`algorithms.bbpssw_distill`,
  `werner_state`, `distillation_rounds`) — two noisy Werner pairs → one
  higher-fidelity pair using only local CNOTs, measurement, and classical
  communication, run as the exact 4-qubit density-matrix circuit. Verified to
  machine precision against the Bennett et al. closed form
  `F' = (F² + (1-F)²/9)/(F² + 2F(1-F)/3 + 5(1-F)²/9)` with success probability equal
  to the denominator; `F = 1/2` is confirmed as the distillation threshold (fixed
  point, degradation below, improvement above), and the Werner state's entanglement
  threshold at `F > 1/2` is cross-checked via negativity. `distillation_rounds`
  iterates the recurrence to a target fidelity (2^r pairs per output).
- **Magic states & T-gate injection** (`algorithms.t_magic_state`,
  `inject_t_gate`) — how fault-tolerant computers get non-Clifford gates: the T gate
  enacted on data using only Clifford operations (CNOT, S, measurement) plus one
  consumed magic state `T|+>`, via gate teleportation. Verified exactly: both
  measurement branches deliver `T|psi>` at fidelity 1 for arbitrary inputs (outcome 1
  needing the `S T-dagger = T` fix-up, and demonstrably wrong without it), and each
  outcome occurs with probability exactly 1/2 — the measurement reveals nothing about
  the data.
- **Transversal logical gates on the Steane code** (`algorithms.steane_transversal`,
  `steane_transversal_cnot`) — fault tolerance's defining property, demonstrated
  exactly: applying a physical gate to all 7 qubits enacts the *logical* gate without
  decoding. Verified: transversal X/Z/H enact logical X/Z/H; transversal S enacts
  logical **S-dagger** (the code's weight-structure hallmark — and explicitly *not*
  logical S); and a bitwise CNOT between two code blocks (14 qubits) enacts a perfect
  logical CNOT, including entangling superposition inputs into encoded logical Bell
  states (fidelity 1.0 for random logical inputs).
- **Steane 7-qubit code [[7,1,3]]** (`algorithms.steane_code`,
  `steane_stabilizers`) — the CSS code built from the classical [7,4,3] Hamming code,
  correcting an arbitrary single-qubit error. Three X-type and three Z-type stabilizer
  generators decode Z and X errors independently (a Y error trips both). Verified:
  all 22 syndromes distinct, every one of the 21 single-qubit errors corrected to
  fidelity 1 for arbitrary logical inputs, and the CSS structure confirmed (a pure X
  error leaves all X-type stabilizers at +1 and vice versa). Completes the code
  family: 3-qubit repetition → [[5,1,3]] → [[7,1,3]] → 9-qubit Shor.
- **5-qubit perfect code [[5,1,3]]** (`algorithms.five_qubit_code`,
  `five_qubit_stabilizers`) — the smallest code that corrects an *arbitrary*
  single-qubit error. Encodes a logical qubit via the stabilizer projector, applies a
  chosen `X`/`Y`/`Z` error on any qubit, extracts the 4-bit syndrome, and recovers
  exactly. Verified: all 16 syndromes are distinct (the "perfect" property — 1
  error-free + 15 single-qubit errors, none left over), and every single-qubit error
  is corrected to fidelity 1 for arbitrary logical inputs.
- **Quantum mutual information** (`DensityMatrix.mutual_information`) —
  `I(A:B) = S(A) + S(B) - S(AB)`, the total (classical + quantum) correlation across a
  cut. Verified: a Bell pair carries 2 bits, a classically correlated pair 1 bit, and a
  product state 0.
- **Entanglement negativity** (`DensityMatrix.negativity`,
  `logarithmic_negativity`, `partial_transpose`) — a mixed-state entanglement measure
  from the Peres-Horodecki partial transpose: `N = (||rho^{T_A}||_1 - 1)/2` and the
  log-negativity `log2(2N+1)`. Verified exactly: a Bell pair gives `N = 1/2`
  (1 bit log-negativity), a product state 0, and a Werner state matches the analytic
  `max(0, (3p-1)/4)` with the PPT-separability threshold at `p = 1/3`.
- **Coherence measures** (`DensityMatrix.l1_coherence`,
  `relative_entropy_coherence`) — quantify superposition as a resource: the l1-norm of
  coherence (sum of off-diagonal magnitudes) and the relative entropy of coherence
  `S(diag rho) - S(rho)`. Verified: `|+>` and a Bell state each carry exactly 1 bit,
  computational-basis and maximally mixed states carry none, and full phase damping
  destroys all coherence.
- **Choi matrix & CPTP verification** (`density_matrix.choi_matrix`, `is_cptp`,
  `kraus_rank`) — the Jamiolkowski image of a Kraus channel, a completely-positive
  + trace-preserving check, and the Kraus rank (minimal number of Kraus operators).
  Verified: the identity channel gives a rank-1 Choi ∝ the maximally entangled state,
  all standard channels are CPTP, a non-trace-preserving map is rejected, and the
  Kraus rank counts noise terms (unitary → 1, full depolarizing → 4).
- **Lindblad master-equation evolution** (`DensityMatrix.evolve_lindblad`) —
  continuous-time open-system dynamics: evolve `rho` under a Hamiltonian plus
  collapse (jump) operators `{L_k}` for `T1` relaxation, `T2` dephasing, and general
  Markovian decoherence. Computed exactly by exponentiating the Liouvillian
  superoperator (no time-stepping error). Verified against the analytic laws:
  excited-state population `e^{-γt}`, coherence decay `½e^{-2κt}`, closed-system Rabi
  in the no-collapse limit, trace preservation, and relaxation to the ground state.
- **Channel quality metrics** (`density_matrix.process_fidelity`,
  `average_gate_fidelity`) — quantify how noisy a Kraus channel is: the entanglement
  (process) fidelity to a target unitary and the state-averaged gate fidelity, linked
  by the exact identity `F_avg = (d·F_process + 1)/(d+1)`. Verified: identity gate → 1,
  `depolarizing(p)` → `1 - p/2`, a stray Pauli-X error → 1/3.
- **Measured syndrome-extraction circuit** (`algorithms.syndrome_extraction_cycle`) —
  the *physical* 3-qubit bit-flip code cycle on the density-matrix engine: two ancilla
  qubits, CNOT parity checks (`Z0Z1`, `Z1Z2`), ancilla measurement, and the
  outcome-conditioned `X` correction (summed as a CPTP measurement channel), then the
  ancillas are traced out. Verified to reproduce the ideal-recovery fidelity
  `(1-p)^3 + 3p(1-p)^2` exactly, confirming the circuit implements the code.
- **QEC under continuous noise** (`algorithms.bit_flip_code_noisy`,
  `phase_flip_code_noisy`, `repetition_code_logical_error`) — run a quantum
  error-correcting code against *continuous* noise (an independent bit-/phase-flip
  channel of strength `p` on every physical qubit) exactly on the density-matrix
  engine, with an exact CPTP syndrome-recovery map, and read out the logical
  fidelity. Verified against the closed form `(1-p)^3 + 3p(1-p)^2`: the encoded
  qubit beats the un-encoded one for all `p < 1/2` and is worse above threshold;
  `|+_L>` is logical-X-invariant and stays perfectly protected. Ships the exact
  majority-vote logical error rate for any odd code distance, showing distance-`d`
  error suppression below threshold.
- **Random Clifford circuits** (`StabilizerSimulator.random`) — apply a random
  H/S/CNOT Clifford circuit (default depth `10n`) and get back the sim; useful for
  randomized benchmarking, testing, and random stabilizer states. Scales to hundreds
  of qubits instantly.
- **Density-matrix simulator** (`quantum_debugger.density_matrix.DensityMatrix`) — an
  open-quantum-systems engine tracking the full `rho`: apply unitary gates and Kraus
  noise channels, take partial traces, and read out purity, populations, expectation
  values, and Uhlmann state fidelity. Ships standard channels (`bit_flip`,
  `phase_flip`, `depolarizing`, `amplitude_damping`, `phase_damping`). Verified:
  purity 1 for pure states, Bell reduced state maximally mixed, depolarizing → I/2,
  amplitude damping relaxes |1> → |0>; unitary evolution matches the state-vector sim.
  Also `von_neumann_entropy` and `entanglement_entropy` (Bell → 1 bit, product → 0),
  plus projective `measure(qubit)` (Born-rule collapse) and `sample(shots)`.
- **Scalable graph / cluster states** (`StabilizerSimulator.graph`) — prepare a graph
  (cluster) state (H on all qubits + CZ per edge) in `O(n + |edges|)`; thousand-qubit
  cluster states are instant, with the canonical stabilizers `X_i prod_{j~i} Z_j`.
  Verified against the state-vector `graph_state` for small graphs.
- **Stabilizer simulator: expectation values, S-dagger, state-vector bridge, sampling**
  (`StabilizerSimulator.expectation_value`, `.s_dagger`, `.to_statevector`, `.copy`,
  `.sample`) — compute `<psi|P|psi>` for any Pauli string directly from the tableau
  (exactly +1/-1 if P or -P is in the stabilizer group, else 0); reconstruct the dense
  state vector for small n via the stabilizer projector; the inverse phase gate; and
  non-destructive shot sampling of measurement outcomes (each shot measures a copy).
  All verified against the state-vector simulator.
- **Quantum multiplier** (`algorithms.quantum_multiply`) — Fourier-basis
  multiplication `|a>|b>|0> -> |a>|b>|a*b>` via doubly-controlled phase rotations
  (adds `2^(j+k)` per pair of set input bits). Returns the exact `2n`-bit product for
  every input pair; complements the Fourier and ripple-carry adders.
- **Ripple-carry subtractor** (`algorithms.ripple_carry_subtract`) — the Cuccaro adder
  run in reverse, computing `b - a` with a borrow bit (exact for every input pair).

## [0.7.0] - 2026-07-22

Theme: performance & scale, a large genuine quantum-algorithms library, advanced
QML/QRL, and test-suite integrity. Highlights: Shor factoring, Simon, quantum error
correction (incl. the 9-qubit Shor code), a Clifford/stabilizer simulator, Trotter
Hamiltonian simulation, a machine-precision VQE ground-state solver, gate
decomposition (ZYZ/KAK) and multi-controlled synthesis, quantum arithmetic (Fourier
+ ripple-carry adders), teleportation/superdense/entanglement-swapping, Bell-CHSH /
GHZ-Mermin nonlocality, BB84 QKD, and quantum spectroscopy. All routines verified
against known outcomes; the `algorithms` package is at ~99% line coverage.

### Added
- **Deutsch's algorithm** (`algorithms.deutsch`) — the first quantum algorithm
  (1985): decide whether a one-bit function is constant or balanced with a single
  query. Completes the query-algorithm family (Deutsch -> Deutsch-Jozsa ->
  Bernstein-Vazirani -> Simon).
- **Quantum spectroscopy** (`algorithms.unitary_eigenphase`,
  `algorithms.hermitian_eigenvalue`) — phase estimation for an *arbitrary* unitary
  or Hermitian operator (not just the demo phase gate): read out the eigenphase of a
  unitary or the eigenvalue of a Hermitian `H` (via `U = exp(iH)`) from a supplied
  eigenstate. Verified against classical diagonalization (exact eigenphases for
  P/T gates, Hermitian eigenvalues to ~1e-3).
- **Repetition-code logical error rate** (`algorithms.repetition_code_error_rate`) —
  Monte-Carlo QEC-threshold demonstration: encode a logical bit in the 3-qubit code,
  apply independent per-qubit bit-flip noise, syndrome-correct, and measure the
  logical failure rate. Matches the analytic `3p^2(1-p)+p^3` and stays below the
  physical rate for all `p < 1/2`.
- **Grover adaptive minimization** (`algorithms.grover_minimize`) — Durr-Hoyer
  quantum optimization: find the argmin of a cost function via Grover search with a
  threshold oracle and BBHT-randomized iteration counts (which avoid the
  over-rotation stall when many states are marked). Reliably finds the global
  minimum, verified against brute force.
- **Multi-controlled gate synthesis** (`algorithms.toffoli_gates`,
  `algorithms.fredkin_gates`, `algorithms.mcx_gates`) — decompose Toffoli (CCX),
  Fredkin (controlled-SWAP), and general n-controlled-X gates into the elementary
  H/T/T-dagger/CNOT set; the n-control MCX uses a clean-ancilla Toffoli ladder.
  Verified exactly against the ideal CCX/CSWAP/MCX action with ancillas restored
  to |0>.
- **Grover-based constraint / SAT solver** (`algorithms.grover_solve`) — finds an
  input satisfying an arbitrary boolean predicate via Grover search over the marked
  set, returning a verified satisfying assignment, the solution count, and the
  success probability.
- **Variational ground-state solver (VQE)** (`algorithms.variational_ground_state`,
  `algorithms.tfim_hamiltonian`, `algorithms.heisenberg_hamiltonian`) — a
  self-contained hardware-efficient VQE (layered RY + CNOT ansatz, gradient-based
  BFGS optimizer, restarts) for any Pauli-sum Hamiltonian, checked against exact
  diagonalization. Reaches the exact TFIM/Heisenberg ground energies to near machine
  precision up to ~4 qubits (~1e-11) and ~1e-6 at 5 qubits; includes ready-made TFIM
  and Heisenberg Hamiltonian builders.
- **BB84 quantum key distribution** (`algorithms.bb84`) — the first quantum
  cryptography protocol, with genuine per-qubit preparation and measurement.
  Without an eavesdropper the sifted keys match exactly (QBER 0); an
  intercept-resend eavesdropper injects a ~25% error rate that trips the security
  threshold. Security emerges from real measurement back-action.
- **Bell/CHSH test, nonlocal game & GHZ-Mermin paradox** (`algorithms.chsh_value`,
  `algorithms.correlator`, `algorithms.bell_state`, `algorithms.chsh_game`,
  `algorithms.mermin_ghz_test`) — a Bell pair measured along optimal angles gives a
  CHSH value `S = 2 sqrt(2)` (Tsirelson's bound), violating the classical limit
  `|S| <= 2`; the CHSH game wins with `cos^2(pi/8) ~ 0.854` vs the classical 0.75; and
  the 3-qubit GHZ (Mermin) test gives an all-or-nothing violation (quantum 4 vs
  classical bound 2). Classical bounds are brute-forced, quantum values exact.
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
- **Quantum arithmetic (Fourier + ripple-carry)** (`algorithms.qft_add`,
  `algorithms.quantum_adder`, `algorithms.qft_subtract`, `algorithms.quantum_compare`,
  `algorithms.ripple_carry_add`) — two addition paradigms: carry-free Fourier-basis
  (Draper) addition of a constant or two registers, plus a Cuccaro ripple-carry adder
  (CNOT/Toffoli MAJ-UMA) that returns the exact sum with carry-out. Also subtraction
  and comparison. All exact for every input pair.
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
