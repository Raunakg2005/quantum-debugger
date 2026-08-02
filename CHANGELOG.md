# Changelog

All notable changes to QuantumDebugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (3.4.0.dev)

Theme: the ZX-calculus — a diagrammatic language for qubit computing. Z- and X-spiders with phases
and their exact tensor/matrix semantics; the core rewrite rules (spider fusion, identity, colour
change, copy, pi-commutation, Hopf) each verified as a matrix identity; the Clifford+T gate set and
CNOT/CZ built as ZX diagrams; and phase gadgets for multi-qubit Pauli-Z rotations — every diagram
checked against the exact linear map (rules hold up to the ZX scalar, accounted for where noted).

### Added
- **Hadamard box** (`algorithms.hadamard_matrix`) — the colour-swapping Hadamard.
- **Hadamard self-inverse** (`algorithms.is_hadamard_self_inverse`) — verifies ``H H = I``.
- **Z-spider tensor** (`algorithms.z_spider_tensor`) — the green spider as a leg tensor.
- **Z-spider matrix** (`algorithms.z_spider_matrix`) — ``|0..0><0..0| + e^{iα}|1..1><1..1|``.
- **X-spider tensor** (`algorithms.x_spider_tensor`) — the red spider (Hadamard-conjugated) tensor.
- **X-spider matrix** (`algorithms.x_spider_matrix`) — its linear map.
- **Spider matrix** (`algorithms.spider_to_matrix`) — reshape a spider tensor into a matrix.
- **Green phase spider** (`algorithms.green_phase`) — a single-leg Z rotation.
- **Red phase spider** (`algorithms.red_phase`) — a single-leg X rotation.
- **Z spider fusion** (`algorithms.spider_fusion_z`) — connected green spiders merge, phases add.
- **Multi-leg fusion** (`algorithms.spider_fusion_multi`) — fusion checked by tensor contraction.
- **X spider fusion** (`algorithms.spider_fusion_x`) — the red-spider fusion rule.
- **Identity rule** (`algorithms.identity_rule`) — a phase-0 two-legged spider is a bare wire.
- **Colour change** (`algorithms.color_change_rule`) — ``X = H^{⊗n} Z H^{⊗m}`` on every leg.
- **Copy rule** (`algorithms.copy_rule`) — the Z-spider copies computational-basis states.
- **pi-commutation** (`algorithms.pi_copy_rule`) — an ``X(π)`` pushes through a Z-spider, negating its
  phase (up to the ZX scalar).
- **Hopf rule** (`algorithms.hopf_rule`) — a Z- and X-spider on two shared wires decouple.
- **Hadamard gate** (`algorithms.hadamard_gate`) — the Hadamard as a ZX box.
- **Z-phase gate** (`algorithms.z_phase_gate`) — Rz as a one-legged Z-spider.
- **X-phase gate** (`algorithms.x_phase_gate`) — Rx as a one-legged X-spider.
- **Pauli gates** (`algorithms.z_gate`, `x_gate`) — Z and X as π-spiders, verified.
- **S and T gates** (`algorithms.s_gate`, `t_gate`) — Clifford+T phase spiders, verified.
- **CNOT diagram** (`algorithms.cnot_zx`) — a Z-copy joined to an X-spider.
- **CNOT verification** (`algorithms.cnot_zx_is_cnot`) — verified equal to CNOT (little-endian).
- **CZ diagram** (`algorithms.cz_zx`) — two Z-spiders on a Hadamard edge.
- **CZ verification** (`algorithms.cz_zx_is_cz`) — verified equal to CZ.
- **Gate equality** (`algorithms.gate_equals`) — equality up to a global phase.
- **ZZ phase gadget** (`algorithms.zz_gadget`) — the CNOT-ladder ``exp(−i(α/2) Z⊗Z)``.
- **ZZ exact target** (`algorithms.zz_phase_exact`) — the reference matrix exponential.
- **n-qubit phase gadget** (`algorithms.phase_gadget`) — the CNOT-ladder gadget for
  ``exp(−i(α/2) Z^{⊗n})``.
- **Gadget verification** (`algorithms.phase_gadget_exact`, `gadget_matches_exact`) — verified
  against the exponential for n up to 4.

## [3.3.0]

Theme: low-density parity-check (LDPC) codes & message-passing decoding — the codes and iterative
decoders behind modern classical and quantum error correction. Parity-check matrices and Tanner
graphs; exact maximum-likelihood syndrome decoding as the reference; and the belief-propagation
(sum-product / min-sum) and Gallager bit-flipping decoders — verified against the exact ML decoder
and the ``[7,4,3]`` Hamming code, with the message-passing decoders shown to correct every single-bit
error on a regular column-weight-3 LDPC.

### Added
- **Repetition check** (`algorithms.repetition_check`) — the ``[n, 1, n]`` parity-check matrix.
- **Hamming check** (`algorithms.hamming_code_check`) — the ``[2^r−1, 2^r−1−r, 3]`` parity-check
  matrix (``[7,4,3]`` at ``r=3``).
- **Syndrome** (`algorithms.syndrome`) — ``H w (mod 2)``, zero iff a codeword.
- **Codeword test** (`algorithms.is_codeword`) — checks the zero syndrome.
- **Codeword enumeration** (`algorithms.all_codewords`) — the GF(2) null space.
- **Code dimension** (`algorithms.code_dimension`) — ``k = n − rank H``.
- **Code rate** (`algorithms.code_rate`) — ``k / n``.
- **Code parameters** (`algorithms.code_parameters`) — the ``[n, k, d]`` triple.
- **Minimum distance** (`algorithms.minimum_distance`) — brute-force over non-zero codewords.
- **Tanner graph** (`algorithms.tanner_graph`) — the bipartite check/bit adjacency.
- **Column weights** (`algorithms.column_weights`) — checks per bit.
- **Row weights** (`algorithms.row_weights`) — bits per check.
- **Regularity** (`algorithms.is_regular`) — constant column and row weight.
- **Tanner girth** (`algorithms.tanner_girth`) — the shortest cycle length (short cycles hurt BP).
- **Random regular LDPC** (`algorithms.random_regular_ldpc`) — a permuted-socket sparse ``H``.
- **Syndrome table** (`algorithms.syndrome_table`) — the exact syndrome → coset-leader map.
- **Coset leader** (`algorithms.coset_leader`) — the minimum-weight error of a syndrome.
- **ML decode** (`algorithms.ml_decode`) — maximum-likelihood decoding via the coset leader.
- **Error-correcting capability** (`algorithms.error_correcting_capability`) — ``t = ⌊(d−1)/2⌋``;
  exact decoding verified to correct all weight-``t`` errors on Hamming.
- **Channel LLRs** (`algorithms.bsc_llr`) — binary-symmetric-channel log-likelihood ratios.
- **Sum-product decoding** (`algorithms.sum_product_decode`) — the belief-propagation decoder.
- **Min-sum decoding** (`algorithms.min_sum_decode`) — its low-complexity approximation.
- **BP error recovery** (`algorithms.bp_decode_error`, `bp_corrects`) — decode an error pattern and
  test recovery of the zero codeword.
- **BP vs ML** (`algorithms.bp_matches_ml_on_weight1`) — verified BP corrects every single-bit error
  on a regular column-weight-3 LDPC.
- **Unsatisfied checks** (`algorithms.unsatisfied_checks`) — the failed parity checks of a word.
- **Unsatisfied count per bit** (`algorithms.unsatisfied_count_per_bit`) — the bit-flip decision
  statistic.
- **Bit-flipping decoder** (`algorithms.gallager_bit_flip`) — Gallager's hard-decision decoder.
- **Bit-flip recovery** (`algorithms.bit_flip_corrects`, `bit_flip_corrects_all_weight1`) — verified
  to correct every single-bit error on a column-weight-3 LDPC.
- **Minimum column weight** (`algorithms.min_column_weight`) — the bit-flipping reliability
  indicator.

## [3.2.0]

Theme: quantum optimal control & pulse engineering — how to *steer* a quantum system to a target
gate or state. Piecewise-constant control propagators and GRAPE (gradient-ascent pulse
engineering) with an analytic, finite-difference-checked gradient; the dynamical-Lie-algebra
controllability test; the Mandelstam-Tamm and Margolus-Levitin quantum speed limits; and the
pulse-area theorem with square/Gaussian/DRAG envelopes — every routine verified against a synthesized
gate fidelity, an exact Lie-algebra dimension, a saturated speed-limit bound, or a rotation unitary.

### Added
- **Control Hamiltonian** (`algorithms.control_hamiltonian`) — assembles ``H_0 + Σ_j u_j H_j``.
- **Slice / total propagators** (`algorithms.slice_propagators`, `piecewise_propagator`) — the
  per-slice and product unitaries of a piecewise-constant pulse.
- **Gate fidelity** (`algorithms.gate_fidelity`) — ``|Tr(target† U)|²/d²``, 1 up to global phase.
- **State fidelity** (`algorithms.state_fidelity`) — ``|⟨target|ψ⟩|²`` for state transfer.
- **GRAPE gradient** (`algorithms.grape_gradient`) — the analytic fidelity gradient, verified
  against finite differences.
- **GRAPE optimizer** (`algorithms.grape_optimize`) — gradient-ascent pulse synthesis, verified to
  reach fidelity > 0.999 for X and Hadamard.
- **GRAPE state transfer** (`algorithms.grape_state_transfer`) — optimize controls to move a state
  to a target.
- **Control fluence** (`algorithms.control_fluence`) — the pulse-energy cost of a control.
- **Pauli controls** (`algorithms.pauli`) — the single-qubit control operators.
- **Lie bracket** (`algorithms.lie_bracket`) — the commutator ``[A, B]``.
- **Lie closure** (`algorithms.lie_closure`) — a basis for the dynamical Lie algebra generated
  under commutation.
- **DLA dimension** (`algorithms.dla_dimension`) — the dynamical-Lie-algebra dimension.
- **su(d)/u(d) dimensions** (`algorithms.su_dimension`, `u_dimension`) — the controllability targets.
- **Controllability** (`algorithms.is_controllable`, `gate_reachable`) — the Lie-algebra rank
  criterion; verified ``{X, Z}`` generates ``su(2)`` and a full-local-plus-``ZZ`` set generates ``su(4)``.
- **Mean energy** (`algorithms.mean_energy`) — ``⟨H⟩`` of a state.
- **Energy variance** (`algorithms.energy_variance`) — ``⟨H²⟩ − ⟨H⟩²``.
- **Energy uncertainty** (`algorithms.energy_uncertainty`) — ``ΔE = √Var H``, the Mandelstam-Tamm
  speed scale.
- **Mandelstam-Tamm bound** (`algorithms.mandelstam_tamm_time`) — ``arccos(overlap)/ΔE``.
- **Margolus-Levitin bound** (`algorithms.margolus_levitin_time`) — the mean-energy speed limit.
- **Quantum speed limit** (`algorithms.quantum_speed_limit_time`) — the tighter of the two bounds.
- **Survival amplitude** (`algorithms.evolution_overlap`) — ``|⟨ψ₀|e^{−iHt}|ψ₀⟩|``.
- **Orthogonalization time** (`algorithms.orthogonalization_time`) — the first orthogonal time,
  found by first-crossing refinement.
- **Speed-limit saturation** (`algorithms.saturates_mandelstam_tamm`) — verified that a qubit
  precession is time-optimal.
- **Square & Gaussian pulses** (`algorithms.square_pulse`, `gaussian_pulse`) — the basic control
  envelopes.
- **DRAG pulse** (`algorithms.drag_pulse`) — the leakage-suppressing derivative quadrature.
- **Pulse area** (`algorithms.pulse_area`, `gaussian_area`) — the drive area, numeric and analytic.
- **Rotation from area** (`algorithms.rotation_from_area`) — the pulse-area theorem ``θ = area``.
- **π-pulse amplitude** (`algorithms.pi_pulse_amplitude`) — the square bit-flip amplitude.
- **Pulse unitary** (`algorithms.pulse_unitary`, `square_pulse_unitary`) — the rotation a pulse
  realizes.
- **Pulse-area theorem** (`algorithms.pi_pulse_is_bit_flip`) — verified an area-π pulse equals X.

## [3.1.0]

Theme: open quantum systems & Lindblad dynamics — how real, noisy quantum systems evolve when
coupled to an environment. The Gorini-Kossakowski-Sudarshan-Lindblad master equation and its
Liouvillian superoperator; quantum-trajectory (Monte Carlo wavefunction) unravelings; the
Breuer-Laine-Piilo non-Markovianity measure; collision-model thermalization; and closed-form
qubit T1/T2 relaxation — every routine verified against an exact channel, the analytic steady
state, or Bloch decay.

### Added
- **Vectorization** (`algorithms.vectorize` / `unvectorize`) — column-stacking map that turns the
  master equation into a linear system.
- **Superoperators** (`algorithms.left_multiply`, `right_multiply`) — the ``I⊗A`` / ``A^T⊗I`` maps
  on a vectorized density matrix.
- **Dissipator** (`algorithms.dissipator_superoperator`, `apply_dissipator`) — the GKSL dissipator
  ``D[L]ρ = LρL† − ½{L†L, ρ}``, superoperator and direct forms.
- **Liouvillian** (`algorithms.lindbladian`, `lindblad_derivative`) — the full GKSL superoperator,
  verified against the direct ``dρ/dt``.
- **Lindblad evolution** (`algorithms.evolve_lindblad`) — ``ρ(t) = unvec(e^{Lt} vec ρ₀)``, matched
  to the exact amplitude-damping and dephasing channels.
- **Trace preservation** (`algorithms.is_trace_preserving`) — checks the Liouvillian conserves
  probability.
- **Liouvillian spectrum & gap** (`algorithms.liouvillian_spectrum`, `spectral_gap`) — all
  eigenvalues have ``Re ≤ 0``; the gap sets the relaxation rate.
- **Steady state** (`algorithms.steady_state`) — the kernel of the Liouvillian, verified equal to
  ``|0⟩⟨0|`` for amplitude damping.
- **Jump operators** (`algorithms.amplitude_damping_jump`, `dephasing_jump`) — the T1 and T2
  Lindblad operators.
- **Effective Hamiltonian** (`algorithms.effective_hamiltonian`) — ``H − (i/2)ΣL†L`` governing the
  no-jump evolution.
- **Jump rates** (`algorithms.jump_rates`) — instantaneous quantum-jump probabilities.
- **Quantum trajectory** (`algorithms.quantum_jump_trajectory`) — one Monte Carlo wavefunction run.
- **Trajectory ensemble** (`algorithms.trajectory_ensemble`) — the stochastic estimate of ``ρ(t)``.
- **Unraveling convergence** (`algorithms.trajectory_lindblad_error`) — trace distance to the exact
  Lindblad state, verified < 0.05.
- **Emission statistics** (`algorithms.mean_photon_emissions`) — mean jumps per trajectory, matched
  to ``1 − e^{−γt}``.
- **Dephasing map** (`algorithms.dephasing_map`) — a coherence-shrinking qubit channel.
- **BLP trace distance** (`algorithms.coherence_trace_distance`) — the ``|+⟩/|−⟩`` distinguishability,
  equal to ``|c(t)|``.
- **Coherence models** (`algorithms.markovian_coherence`, `nonmarkovian_coherence`) — monotone vs
  reviving decoherence.
- **Distinguishability backflow** (`algorithms.distinguishability_backflow`) — the positive
  trace-distance increments.
- **BLP non-Markovianity** (`algorithms.blp_measure`, `is_markovian`) — 0 for Markovian dynamics,
  positive when the trace distance revives.
- **Revival count** (`algorithms.revival_count`) — number of information-backflow episodes.
- **Partial swap** (`algorithms.partial_swap`) — the ``exp(−iθ·SWAP)`` collision unitary.
- **Thermal ancilla** (`algorithms.thermal_qubit`) — the Gibbs state that drives thermalization.
- **Collision step** (`algorithms.collision_step`, `repeated_collisions`) — one system-ancilla
  interaction and its iteration.
- **Thermalization** (`algorithms.thermalize`, `fixed_point_error`) — repeated collisions drive the
  system to the Gibbs state (fixed-point error → 0).
- **Full-swap thermalization** (`algorithms.full_swap_is_one_step`) — a full SWAP replaces the
  system with the ancilla in one collision.
- **Bloch vector** (`algorithms.bloch_vector`, `density_from_bloch`) — Bloch ↔ density-matrix.
- **T1/T2 relations** (`algorithms.t2_from_t1_tphi`, `t2_upper_bound`, `relaxation_times`) — the
  ``1/T2 = 1/(2T1) + 1/Tφ`` relation and the ``T2 ≤ 2T1`` bound.
- **Bloch decay** (`algorithms.bloch_decay`, `bloch_decay_matches_lindblad`) — the closed-form
  T1/T2 decay, verified against exact Lindblad evolution.
- **Purity** (`algorithms.purity`) — the ``Tr ρ²`` decoherence witness.

## [3.0.0]

Theme: quantum complexity & advantage — the milestone 3.0 release, on *why* quantum computers
are (sometimes) faster. Boolean-function complexity (sensitivity, block sensitivity, certificate
complexity, decision-tree depth, degree) and the exact inequalities between them; Fourier
analysis on the Boolean cube (Parseval, influences, noise stability); the quantum query
separations behind Deutsch-Jozsa, Simon, Grover, and parity; and communication complexity with
quantum fingerprinting — every measure computed by brute force and every relation verified.

### Documentation & developer tooling
- **Narrative guides** for every advanced theme added since v0.8 — many-body physics, tensor
  networks II, QSVT, error mitigation II, fault-tolerant QEC, quantum chemistry, quantum
  information, advanced algorithms II, continuous-variable, benchmarking, compilation,
  optimization/QAOA, VQA theory, Hamiltonian simulation, metrology, foundations, communication,
  MBQC, thermodynamics, and complexity — each with runnable, verified examples, wired into the
  Sphinx table of contents.
- **Algorithms API reference** (`docs/algorithms_api.md`) — autodoc coverage of every module in
  `quantum_debugger.algorithms`; `conf.py` now documents the in-tree package and mocks optional
  integrations so the reference builds cleanly.
- **AI Development Lifecycle** scaffolding — `AGENTS.md` (agent working agreement),
  `docs/aidlc_guide.md` (the five-phase Intent → Decompose → Implement → Verify → Integrate
  lifecycle), and a verification checklist added to the pull-request template.

### Added
- **Truth table** (`algorithms.truth_table`) — evaluate a Boolean function on all inputs.
- **Local sensitivity** (`algorithms.sensitivity_at`) — the number of pivotal bits at one input.
- **Sensitivity** (`algorithms.max_sensitivity`) — the global ``s(f) = max_x s(f,x)``.
- **Block sensitivity** (`algorithms.block_sensitivity`) — the max disjoint sensitive blocks,
  verified ``>= s(f)``.
- **Certificate complexity** (`algorithms.certificate_complexity`) — the smallest certifying
  assignment, verified ``>= bs(f)``.
- **Decision-tree complexity** (`algorithms.decision_tree_complexity`) — the deterministic query
  complexity ``D(f)``.
- **Polynomial degree** (`algorithms.polynomial_degree`) — the multilinear representing-polynomial
  degree, verified ``<= D(f)``.
- **Complexity hierarchy** (`algorithms.sensitivity_hierarchy_holds`) — verifies
  ``s <= bs <= C <= D`` and ``deg <= D`` on OR/AND/parity/majority.
- **±1 conversion** (`algorithms.to_pm1`) — the ``{0,1} -> {-1,+1}`` map for Fourier analysis.
- **Fourier coefficients** (`algorithms.fourier_coefficients`) — the character-basis spectrum
  ``fhat(S)``.
- **Parseval** (`algorithms.parseval`) — the total Fourier weight, verified equal to 1.
- **Variable influence** (`algorithms.influence`) — the weight on sets containing a variable.
- **Total influence** (`algorithms.total_influence`) — the average sensitivity, verified ``n`` for
  parity and 1 for a dictator.
- **Noise stability** (`algorithms.noise_stability`) — ``sum rho^{|S|} fhat(S)^2``, verified 1 at
  ``rho=1``.
- **High-degree weight** (`algorithms.fourier_weight_above_degree`) — the spectral weight above a
  degree.
- **Fourier degree** (`algorithms.degree_from_fourier`) — the top non-zero level, verified equal
  to the polynomial degree.
- **Deutsch-Jozsa queries** (`algorithms.deutsch_jozsa_queries`) — ``1`` quantum vs ``2^{n-1}+1``
  classical.
- **Simon queries** (`algorithms.simon_queries`) — ``O(n)`` quantum vs ``Omega(2^{n/2})``
  classical.
- **Grover queries** (`algorithms.grover_queries`) — the ``(pi/4)sqrt N`` quantum search count.
- **Grover optimality** (`algorithms.grover_is_optimal`) — verifies the count is ``Theta(sqrt N)``
  (BBBV-optimal).
- **Parity queries** (`algorithms.parity_queries`) — ``ceil(n/2)`` quantum vs ``n`` classical.
- **Quantum speedup** (`algorithms.quantum_speedup`) — the classical/quantum query ratio.
- **Polynomial-method bound** (`algorithms.polynomial_method_bound`) — the ``deg(f)/2`` quantum
  query lower bound.
- **Exponential separation test** (`algorithms.is_exponential_separation`) — verified for
  Deutsch-Jozsa/Simon, not for parity.
- **Deterministic equality** (`algorithms.equality_deterministic`) — the ``n+1``-bit deterministic
  cost.
- **Randomized equality** (`algorithms.equality_randomized`) — the ``O(log n)`` shared-coin cost.
- **Quantum fingerprint** (`algorithms.quantum_fingerprint_length`) — the ``O(log n)`` qubit
  fingerprint for Equality.
- **Equality saving** (`algorithms.equality_exponential_saving`) — verifies the exponential
  fingerprint saving over deterministic communication.
- **Inner-product complexity** (`algorithms.inner_product_complexity`) — ``Theta(n)`` with no
  quantum advantage.
- **Disjointness complexity** (`algorithms.disjointness_complexity`) — ``sqrt n`` quantum vs ``n``
  classical.
- **Quantum-advantage test** (`algorithms.has_quantum_advantage`) — flags a communication quantum
  speedup (disjointness yes, inner product no).
- **Containment DAG** (`algorithms.known_containments`) — the proven
  ``P subseteq BPP subseteq BQP subseteq PP subseteq PSPACE`` order.
- **Containment query** (`algorithms.contains`) — transitive-closure membership in the class
  order.
- **Problem classification** (`algorithms.problem_class`) — the smallest known class of a problem.
- **BQP membership** (`algorithms.in_bqp`) — whether a problem is efficiently quantum-solvable
  (factoring, sorting yes).
- **Open separations** (`algorithms.is_open_separation`) — flags open questions (BPP vs BQP, BQP
  vs NP).
- **Hierarchy consistency** (`algorithms.hierarchy_is_consistent`) — verifies the containment order
  is reflexive, transitive, and acyclic.

## [2.9.0]

Theme: quantum thermodynamics — the laws of heat and work at the quantum scale. Work and heat
along a quantum process, entropy production and the second law, the Jarzynski equality and
Crooks fluctuation theorem, the Landauer bound on erasure, passive states, and the quantum Otto
engine cycle — every relation verified against its closed form and the exact statistics.

### Added
- **Gibbs state** (`quantum_thermodynamics.gibbs_state`) — the thermal equilibrium state
  ``e^{-beta H}/Z``.
- **Partition function** (`quantum_thermodynamics.partition_function`) — ``Z = Tr e^{-beta H}``.
- **Free energy** (`algorithms.free_energy`) — the equilibrium ``-(1/beta) ln Z``.
- **Internal energy** (`algorithms.internal_energy`) — the mean energy ``<H>``.
- **Quench work** (`algorithms.quench_work`) — the work of a sudden Hamiltonian change.
- **Heat exchanged** (`algorithms.heat_exchanged`) — the energy change at fixed Hamiltonian.
- **Non-equilibrium free energy** (`algorithms.nonequilibrium_free_energy`) — ``<H> - S/beta``,
  verified minimized by the Gibbs state.
- **Heat capacity** (`algorithms.heat_capacity`) — ``beta^2 Var(H)``, verified non-negative.
- **Thermal entropy** (`algorithms.thermal_entropy`) — the Gibbs-state entropy.
- **Entropy production** (`algorithms.entropy_production`) — ``beta(W - Delta F)``, the second
  law, verified non-negative.
- **Two-point work distribution** (`algorithms.two_point_work_distribution`) — the measurement
  statistics of work, verified normalized.
- **Jarzynski average** (`algorithms.jarzynski_average`) — the exponential work average
  ``<e^{-beta W}>``.
- **Jarzynski verification** (`algorithms.verify_jarzynski`) — verifies ``<e^{-beta W}> =
  e^{-beta Delta F}`` exactly.
- **Free-energy difference** (`algorithms.free_energy_difference`) — the ``Delta F`` Jarzynski
  recovers from non-equilibrium work.
- **Average work** (`algorithms.average_work`) — the mean two-point-measurement work, verified
  ``>= Delta F``.
- **Dissipated work** (`algorithms.dissipated_work`) — the irreversible excess ``<W> - Delta F``,
  verified non-negative.
- **Work variance** (`algorithms.work_variance`) — the size of the work fluctuations.
- **Landauer bound** (`algorithms.landauer_bound`) — the ``k_B T ln 2`` erasure cost, verified.
- **Crooks ratio** (`algorithms.crooks_ratio`) — the forward/reverse work-probability ratio,
  verified 1 at the reversible work.
- **Otto cycle** (`algorithms.otto_cycle`) — the four-stroke qubit engine, returning heats, work,
  and efficiency.
- **Otto efficiency** (`algorithms.otto_efficiency`) — the closed form ``1 - omega_c/omega_h``.
- **Carnot efficiency** (`algorithms.carnot_efficiency`) — the universal ``1 - T_c/T_h`` bound.
- **Engine test** (`algorithms.is_engine`) — whether the Otto cycle delivers net work.
- **Carnot bound check** (`algorithms.efficiency_below_carnot`) — verifies the Otto efficiency
  never exceeds Carnot (the second law).
- **Passive state** (`algorithms.passive_state`) — the work-free rearrangement of a state's
  populations.
- **Ergotropy** (`algorithms.ergotropy`) — the maximum unitary-extractable work, verified
  non-negative and zero for passive states.
- **Max extractable work** (`algorithms.max_extractable_work`) — the ergotropy as the single-copy
  work bound.
- **Passivity test** (`algorithms.is_passive`) — whether a state has zero ergotropy.
- **Bound energy** (`algorithms.bound_energy`) — the non-extractable part of the energy, verified
  to sum with ergotropy to ``<H>``.
- **Gibbs passivity** (`algorithms.gibbs_is_passive`) — verifies a thermal state stores no
  extractable work.

## [2.8.0]

Theme: measurement-based & cluster-state computing — computing by *measuring* a fixed
entangled resource. Graph-state construction and stabilizers, the 1D/2D cluster states,
local complementation, one-way single-qubit rotations and CNOT via adaptive measurements
with Pauli byproduct tracking, and the measurement-calculus notion of causal flow — every
measurement pattern verified to reproduce the intended circuit unitary.

### Added
- **Graph state** (`graph_states.graph_state`) — the ``prod CZ |+>^n`` MBQC resource state.
- **Graph-state stabilizers** (`algorithms.graph_state_stabilizers`) — the
  ``K_v = X_v prod_{w~v} Z_w`` generators.
- **Stabilizer verification** (`algorithms.verify_stabilizers`) — checks each generator fixes the
  graph state.
- **Linear cluster** (`algorithms.linear_cluster_edges`) — the 1D cluster (path graph) edges.
- **2D cluster** (`algorithms.cluster_2d_edges`) — the universal 2D cluster-state lattice edges.
- **Complete-graph state** (`algorithms.complete_graph_edges`) — the ``K_n`` graph, GHZ-equivalent.
- **Star-graph state** (`algorithms.star_graph_edges`) — the star graph, exactly GHZ up to local
  Cliffords.
- **Graph-state entanglement** (`algorithms.graph_state_entanglement`) — the Meyer-Wallach measure,
  verified 0 for the empty graph and ~1 for a connected one.
- **Local complementation** (`algorithms.local_complementation`) — the edge-toggle transformation
  on a graph.
- **Local-Clifford equivalence** (`algorithms.local_clifford_equivalent`) — verifies a graph and
  its local complement give locally-equivalent states.
- **Z-rotation** (`algorithms.rz`) — the ``R_z`` gate the teleportation angle implements.
- **X-Y measurement basis** (`algorithms.xy_measurement_states`) — the ``|+-_phi>`` measurement
  outcomes of the one-way model.
- **Teleportation step** (`algorithms.teleport_step`) — one MBQC measurement step, verified equal
  to ``X^s H R_z(-phi)|psi>``.
- **Step unitary** (`algorithms.expected_step_unitary`) — the gate a teleportation step
  implements, the verification target.
- **MBQC rotation** (`one_way_computing.mbqc_rotation`) — a chain of teleportation steps realizing
  an arbitrary single-qubit rotation.
- **Rotation unitary** (`algorithms.expected_rotation_unitary`) — the composed gate the step chain
  implements, verified against the MBQC output.
- **MBQC identity wire** (`algorithms.mbqc_identity`) — two angle-0 steps giving ``H.H=I`` up to a
  Pauli, verified.
- **Measurement probability** (`algorithms.measurement_probability`) — verified ``1/2`` (the
  outcome is random, as MBQC requires).
- **Byproduct operator** (`algorithms.byproduct_operator`) — the tracked Pauli correction.
- **Measurement pattern** (`algorithms.measurement_pattern`) — the declarative one-way computation
  (entangle / measure / correct).
- **Causal flow** (`algorithms.causal_flow`) — the Danos-Kashefi flow, verified for the linear
  cluster (``f(i)=i+1``).
- **Flow verification** (`algorithms.verify_flow`) — checks the causal-flow determinism
  conditions.
- **Flow existence** (`algorithms.has_flow`) — whether a pattern admits a deterministic flow.
- **Pattern depth** (`algorithms.pattern_depth`) — the parallel measurement depth of the flow.
- **Native CZ** (`algorithms.native_cz`) — the free entangling gate of the one-way model (a
  cluster edge).
- **MBQC Hadamard** (`algorithms.mbqc_hadamard`) — the Hadamard realized by a measurement step.
- **Hadamard verification** (`algorithms.hadamard_is_teleport`) — verifies the angle-0 step equals
  the ``H`` gate.
- **CNOT decomposition** (`algorithms.cnot_decomposition`) — the ``(I⊗H)CZ(I⊗H)`` MBQC identity.
- **CNOT verification** (`algorithms.verify_cnot_decomposition`) — verifies the decomposition
  equals the exact CNOT.
- **MBQC CNOT** (`algorithms.mbqc_cnot`) — the two-qubit gate via a native CZ bond plus Hadamard
  teleportations, verified against the exact CNOT.

## [2.7.0]

Theme: tensor networks II — the geometry of entanglement beyond 1D. Tensor-contraction cost
analysis and optimal contraction ordering; 2D **PEPS** construction and exact contraction;
**MERA** disentanglers and isometric coarse-graining; **tree tensor networks**; and the
entanglement-scaling laws (area law, the Page value of a random state, critical log-scaling) —
verified by round-tripping to the exact state vector and against closed forms.

### Added
- **Pairwise contraction** (`algorithms.contract_pair`) — the atomic ``tensordot`` of two
  tensors over shared indices.
- **Contraction cost** (`algorithms.pairwise_cost`) — the FLOP cost of one pairwise contraction.
- **Chain contraction** (`algorithms.contract_chain`) — the matrix-chain product, the reference
  result every order must reproduce.
- **Naive chain cost** (`algorithms.matrix_chain_left_cost`) — the left-to-right
  scalar-multiplication count.
- **Optimal chain cost** (`algorithms.matrix_chain_optimal_cost`) — the dynamic-program minimum,
  verified below the naive cost.
- **Optimal chain order** (`algorithms.matrix_chain_optimal_order`) — the parenthesization
  achieving the optimal cost.
- **SVD bond truncation** (`algorithms.svd_bond_truncation`) — truncate a bipartition to a bond
  dimension and report the retained fidelity, the core compression step.
- **Contraction speedup** (`algorithms.contraction_speedup`) — the naive/optimal cost ratio.
- **Product PEPS** (`algorithms.product_peps`) — the bond-dimension-1 (product) 2D tensor
  network.
- **Product-PEPS test** (`algorithms.is_product_peps`) — the bond-dimension-1 check.
- **Bond dimension** (`algorithms.bond_dimension`) — the maximum PEPS virtual bond.
- **PEPS contraction** (`algorithms.contract_2x2`) — exact contraction of a ``2x2`` PEPS to the
  state vector, verified on product states.
- **Cluster-state PEPS** (`algorithms.cluster_peps_statevector`) — the exact bond-dimension-2
  cluster-state PEPS contraction.
- **Cluster-state reference** (`algorithms.cluster_state_reference`) — the ``H``+``CZ`` cluster
  state the PEPS is verified against.
- **MERA disentangler** (`algorithms.disentangler`) — the two-site unitary that removes
  cross-boundary entanglement, verified unitary.
- **MERA isometry** (`algorithms.isometry`) — the two-site coarse-grainer with orthonormal
  columns.
- **Isometry test** (`algorithms.is_isometry`) — the ``w^dagger w = I`` check.
- **Descending superoperator** (`algorithms.descending_superoperator`) — the coarse->fine MERA
  map, verified trace-preserving.
- **Ascending superoperator** (`algorithms.ascending_superoperator`) — the fine->coarse
  renormalization of observables.
- **Causal cone** (`algorithms.causal_cone_width`) — the constant-width MERA past cone that makes
  observables scalable.
- **Ternary isometry** (`algorithms.ternary_isometry`) — the 3-site->1-site MERA coarse-grainer,
  verified isometric.
- **Operator renormalization** (`algorithms.renormalize_operator`) — the RG flow of an observable
  up the network.
- **State coarse-graining** (`algorithms.coarse_grain_state`) — one MERA layer applied to a
  state.
- **Bipartite entropy** (`algorithms.bipartite_entropy`) — the entanglement entropy of a
  subsystem, verified 0 for product and 1 for a Bell pair.
- **Maximum entanglement** (`algorithms.max_entanglement`) — the ``min(n_A, n-n_A)`` volume-law
  ceiling.
- **Page average entropy** (`algorithms.page_average_entropy`) — Page's closed form for a random
  state's average entanglement.
- **Random-state entropy** (`algorithms.random_state_entropy`) — the sampled mean, verified to
  match the Page value (volume law).
- **Entanglement spectrum** (`algorithms.entanglement_spectrum`) — the squared Schmidt
  coefficients of a bipartition.
- **Rényi-2 entropy** (`algorithms.renyi2_entropy`) — the measurable second Rényi entanglement
  entropy.
- **Area-law test** (`algorithms.is_area_law`) — the constant-entropy-across-cuts check.
- **Volume-law slope** (`algorithms.volume_law_slope`) — the ``~1 bit/qubit`` entropy-vs-size
  slope of a random state.

## [2.6.0]

Theme: quantum communication & networks — sending quantum information reliably and securely.
Quantum-channel capacities (coherent information, quantum / private / entanglement-assisted
capacity, with closed forms for the erasure, dephasing, and depolarizing channels); quantum
key distribution (BB84, six-state, and E91 key rates with their QBER thresholds); and quantum
networks (entanglement swapping, repeater rates, and entanglement routing) — every rate and
threshold verified against its closed form.

### Added
- **Binary entropy** (`algorithms.binary_entropy`) — ``h(p)``, the workhorse of capacity and
  key-rate formulas.
- **Depolarizing channel** (`algorithms.depolarizing_kraus`) — the isotropic-noise Kraus
  operators.
- **Dephasing channel** (`algorithms.dephasing_kraus`) — the phase-flip Kraus operators.
- **Amplitude-damping channel** (`algorithms.amplitude_damping_kraus`) — the energy-loss Kraus
  operators.
- **Channel application** (`algorithms.apply_channel`) — apply a Kraus channel to a density
  matrix.
- **Coherent information** (`quantum_channels_advanced.coherent_information`) —
  ``S(N(rho)) - S(N^c(rho))``, verified equal to the dephasing quantum capacity ``1-h(p)``.
- **Entanglement-assisted capacity** (`algorithms.entanglement_assisted_capacity`) — the
  quantum mutual information, verified to exceed the coherent information.
- **Erasure quantum capacity** (`algorithms.erasure_quantum_capacity`) — the closed form
  ``max(0, 1-2p)``, zero above ``p=1/2``.
- **Dephasing quantum capacity** (`algorithms.dephasing_quantum_capacity`) — the closed form
  ``1-h(p)``.
- **Holevo information** (`algorithms.holevo_information`) — the classical-information bound of a
  quantum ensemble, verified 1 bit for orthogonal states and 0 for identical.
- **Channel fidelity** (`algorithms.channel_fidelity`) — the average gate fidelity to the
  identity, verified 1 for the identity channel.
- **BB84 key rate** (`algorithms.bb84_key_rate`) — ``1 - 2h(QBER)``, verified positive below the
  threshold.
- **BB84 threshold** (`algorithms.bb84_threshold`) — the ``QBER ~ 11%`` security threshold,
  verified where the key rate hits zero.
- **Six-state key rate** (`algorithms.six_state_key_rate`) — the three-basis protocol rate.
- **Six-state threshold** (`algorithms.six_state_threshold`) — the higher ``~12.6%`` threshold,
  verified above BB84's.
- **QBER from CHSH** (`algorithms.qber_from_chsh`) — the E91 error rate from the CHSH value,
  verified 0 at Tsirelson's bound.
- **E91 key rate** (`algorithms.e91_key_rate`) — the Ekert-protocol rate, verified 1 at
  Tsirelson and 0 at the classical bound.
- **Secret fraction** (`algorithms.secret_fraction`) — the asymptotic secret-key fraction of a
  protocol at a given QBER.
- **Sifting ratio** (`algorithms.sifting_ratio`) — the basis-reconciliation efficiency (``1/2``
  BB84, ``1/3`` six-state).
- **Decoy-state gain** (`algorithms.decoy_state_gain`) — the single-photon detection gain that
  defeats photon-number-splitting attacks.
- **Werner fidelity** (`algorithms.werner_fidelity`) — the Bell-state fidelity of a Werner link.
- **Werner swap** (`algorithms.swap_werner`) — the Werner-parameter product after swapping two
  links.
- **Swapped fidelity** (`algorithms.entanglement_swapping_fidelity`) — the fidelity after
  swapping, verified to reduce to the input for a perfect second link.
- **Repeater fidelity** (`algorithms.repeater_werner`) — the ``w^n`` fidelity decay across a
  chain of swaps.
- **Repeater rate** (`algorithms.repeater_rate`) — the entanglement-generation rate across a
  repeater chain.
- **Purification** (`algorithms.purified_fidelity`) — one DEJMPS round, verified to raise the
  link fidelity.
- **Path fidelity** (`algorithms.path_fidelity`) — the end-to-end fidelity of a swap chain,
  verified to fall with hops.
- **Reach before threshold** (`algorithms.hops_before_threshold`) — the number of swaps before
  the fidelity drops below a target, verified to shrink with link quality.
- **GHZ distribution** (`algorithms.ghz_distribution_fidelity`) — the fidelity of a distributed
  multipartite GHZ state.
- **Entanglement routing** (`algorithms.entanglement_routing`) — max-fidelity path search across
  a network graph, verified to pick the higher-fidelity route.

## [2.5.0]

Theme: quantum foundations & nonlocality — what makes quantum correlations impossible to
explain classically. The CHSH inequality with its classical (2), Tsirelson (2√2), and
algebraic (4) bounds; multiparty Mermin inequalities with exponential GHZ violation;
Popescu-Rohrlich boxes (super-quantum but no-signaling); EPR steering; and device-independent
randomness certified from the CHSH value — every classical bound checked by brute force over
local strategies and every quantum value against its closed form.

### Added
- **CHSH measurement operator** (`algorithms.measurement_operator`) — the ``cos(a)Z + sin(a)X``
  ``+/-1`` observable in the Bloch ``x-z`` plane.
- **CHSH correlator** (`bell_inequalities.correlator`) — the two-party correlation ``E(a,b)``.
- **CHSH value** (`bell_inequalities.chsh_value`) — the CHSH combination, verified ``2 sqrt2`` for
  a Bell state.
- **Classical CHSH bound** (`algorithms.classical_chsh_bound`) — ``2``, from brute force over all
  deterministic local strategies.
- **Tsirelson bound** (`algorithms.tsirelson_bound`) — the quantum maximum ``2 sqrt2``.
- **Algebraic bound** (`algorithms.algebraic_bound`) — the no-signaling maximum ``4``.
- **CHSH violation** (`algorithms.chsh_violation`) — the amount a state exceeds the classical
  bound.
- **Bell states** (`bell_inequalities.bell_state`) — the four maximally entangled states.
- **PR-box correlations** (`algorithms.pr_box_correlations`) — the ``a XOR b = x AND y`` box.
- **Behaviour correlator** (`algorithms.correlation_value`) — the ``E(x,y)`` of a behaviour.
- **CHSH from a box** (`algorithms.chsh_from_box`) — the CHSH value of a correlation behaviour,
  ``4`` for the PR box.
- **No-signaling test** (`algorithms.is_no_signaling`) — verifies marginals are
  setting-independent (True for the PR box).
- **Local deterministic box** (`algorithms.local_deterministic_box`) — the classical-polytope
  vertices (CHSH ``<= 2``).
- **Super-quantum check** (`algorithms.pr_box_is_superquantum`) — verifies the PR box exceeds
  Tsirelson's bound.
- **GHZ state** (`mermin_multiparty.ghz_state`) — the ``n``-party maximally nonlocal state.
- **Mermin operator** (`algorithms.mermin_operator`) — the recursively built Mermin-Klyshko
  operator.
- **Mermin value** (`algorithms.mermin_value`) — a state's Mermin expectation.
- **Mermin optimal value** (`algorithms.mermin_optimal_value`) — the largest eigenvalue of the
  Mermin operator, the quantum maximum.
- **Mermin quantum bound** (`algorithms.mermin_quantum_bound`) — the closed form ``2^{(n-1)/2}``,
  verified equal to the optimal value.
- **Mermin classical bound** (`algorithms.mermin_classical_bound`) — ``1``, from brute force over
  local strategies.
- **Mermin violation ratio** (`algorithms.mermin_violation_ratio`) — the ``2^{(n-1)/2}``
  exponentially growing multiparty nonlocality.
- **Steering value** (`algorithms.steering_value`) — the three-setting linear steering witness,
  ``sqrt3`` for a Bell state.
- **Steering bound** (`algorithms.steering_bound`) — the unsteerable (local-hidden-state) bound
  of ``1``.
- **Steerability test** (`algorithms.is_steerable`) — verified True for a Bell state, False for a
  separable state.
- **Werner state** (`steering.werner_state`) — the ``p|Phi+><Phi+| + (1-p)I/4`` family probing
  the steering boundary.
- **Werner steering threshold** (`algorithms.werner_steering_threshold`) — the ``p = 1/sqrt3``
  steering boundary, verified.
- **Guessing probability** (`algorithms.guessing_probability`) — the device-independent adversary
  bound ``1/2 + (1/2)sqrt(2 - S^2/4)``, verified 1 at ``S=2`` and 1/2 at Tsirelson.
- **Certified randomness** (`algorithms.certified_randomness`) — the ``-log2 P_guess`` bits per
  run, verified 0 (classical) to 1 (Tsirelson).
- **Randomness certification test** (`algorithms.is_randomness_certified`) — verifies a violation
  (``S > 2``) certifies some randomness.
- **DI key rate** (`algorithms.di_key_rate`) — a device-independent key-rate proxy from the CHSH
  value.
- **Randomness vs. violation** (`algorithms.randomness_vs_violation`) — the certified randomness
  across CHSH values, verified monotonically increasing.

## [2.4.0]

Theme: quantum metrology & sensing — using entanglement to measure better. The quantum
Fisher information and Cramér-Rao bound, the standard-quantum-limit vs. Heisenberg-limit
scaling, entangled probe states (NOON, GHZ) that reach the Heisenberg limit, spin squeezing
for sub-shot-noise sensing (the Wineland parameter and metrological gain), and multiparameter
estimation (the QFI matrix and parameter incompatibility) — every bound verified against its
closed form.

### Added
- **Generator variance** (`algorithms.generator_variance`) — ``<G^2>-<G>^2``, the core of the
  pure-state QFI.
- **Pure-state QFI** (`algorithms.qfi_pure`) — ``4 Var(G)``, the metrological resource.
- **Cramér-Rao bound** (`algorithms.cramer_rao_bound`) — ``1/sqrt(m F_Q)``, the precision floor.
- **Standard quantum limit** (`algorithms.standard_quantum_limit`) — ``1/sqrt(n)``, the
  uncorrelated-probe precision.
- **Heisenberg limit** (`algorithms.heisenberg_limit`) — ``1/n``, verified below the standard
  quantum limit.
- **Metrological advantage** (`algorithms.metrological_advantage`) — the ``sqrt(n)``
  entanglement-enabled gain.
- **Error propagation** (`algorithms.error_propagation`) — ``sqrt(Var S)/|dS/dtheta|``, the
  operational precision of a measured signal, verified Heisenberg for a GHZ fringe.
- **Collective Jz** (`algorithms.collective_jz`) — the interferometer phase generator.
- **Product probe** (`algorithms.product_probe`) — the uncorrelated ``|+>^n`` SQL reference
  probe.
- **GHZ probe** (`algorithms.ghz_probe`) — the entangled Heisenberg-limit reference probe.
- **Probe QFI** (`algorithms.probe_qfi`) — the QFI of a probe under ``J_z``.
- **Product-probe QFI** (`algorithms.product_probe_qfi`) — verified equal to ``n`` (SQL).
- **GHZ-probe QFI** (`algorithms.ghz_probe_qfi`) — verified equal to ``n^2`` (Heisenberg).
- **NOON QFI** (`algorithms.noon_phase_qfi`) — the ``N^2`` phase sensitivity of a NOON state.
- **Ramsey signal** (`algorithms.ramsey_signal`) — the interference fringe, ``n``-times faster
  for a GHZ probe.
- **Collective spin operators** (`algorithms.collective_spin`) — ``J_x, J_y, J_z`` on ``n``
  qubits.
- **Coherent spin state** (`algorithms.coherent_spin_state`) — the ``|+>^n`` SQL reference
  (``xi^2 = 1``).
- **One-axis twisting** (`algorithms.one_axis_twisting_state`) — the ``e^{-i chi t J_z^2}``
  squeezing generator.
- **Wineland squeezing parameter** (`algorithms.wineland_squeezing_parameter`) — ``xi_R^2``,
  verified 1 for the coherent state and ``< 1`` when squeezed.
- **Metrological gain** (`algorithms.metrological_gain`) — the ``1/xi^2`` variance gain of a
  squeezed state.
- **Squeezing test** (`algorithms.is_squeezed`) — the sub-SQL (``xi^2 < 1``) check.
- **Best twisting squeezing** (`algorithms.best_twisting_squeezing`) — the optimal
  one-axis-twisting squeezing, verified below 1.
- **QFI matrix** (`algorithms.qfi_matrix`) — the multiparameter Fisher matrix, verified
  symmetric positive semi-definite.
- **Matrix Cramér-Rao bound** (`algorithms.cramer_rao_matrix`, `total_precision_bound`) — the
  ``F^{-1}`` covariance bound and its trace.
- **Parameter incompatibility** (`algorithms.parameter_incompatibility`) — the mean-commutator
  measure of joint-estimation incompatibility, verified 0 for commuting generators.
- **Signal-to-noise ratio** (`algorithms.signal_to_noise`) — ``sqrt(shots F_Q)``, the sensing
  SNR.
- **Phase precision** (`algorithms.phase_precision`) — the Cramér-Rao phase error ``1/sqrt(shots
  F_Q)``.
- **Frequency precision** (`algorithms.frequency_precision`) — the phase error per interrogation
  time.
- **Entanglement gain** (`algorithms.entanglement_gain`) — the ``sqrt(n)`` precision gain of an
  entangled probe.
- **QFI per particle** (`algorithms.qfi_per_particle`) — ``F_Q/n``, 1 at the SQL and ``n`` at
  Heisenberg.
- **Heisenberg-scaling test** (`algorithms.is_heisenberg_scaling`) — verifies QFI scales as
  ``n^2``, the quantum-advantage signature.

## [2.3.0]

Theme: Hamiltonian simulation & product formulas — the algorithmic core of digital quantum
simulation. First-, second-, and fourth-order Trotter-Suzuki formulas with their exact
error scaling (``t^2/r``, ``t^3/r^2``, ``t^5/r^4``), commutator error bounds, the randomized
qDRIFT protocol (gate count independent of the number of terms), and Taylor-series /
truncation-order simulation — every approximation verified against the exact ``e^{-iHt}``.

### Added
- **Exact evolution** (`algorithms.exact_evolution`) — the reference propagator ``e^{-iHt}``
  every product formula is compared to.
- **First-order Trotter** (`algorithms.first_order_trotter`) — the Lie-Trotter product formula,
  error ``O(t^2/r)``.
- **Second-order Trotter** (`algorithms.second_order_trotter`) — the symmetric Strang formula,
  error ``O(t^3/r^2)``.
- **Fourth-order Suzuki** (`algorithms.fourth_order_suzuki`) — the recursive Suzuki formula,
  error ``O(t^5/r^4)``.
- **Trotter error** (`algorithms.trotter_error`) — the spectral-norm error of a product formula
  against the exact evolution.
- **Randomized Trotter** (`algorithms.randomized_trotter`) — first-order Trotter with a random
  term ordering per step (leading-error cancellation in expectation), verified to approximate
  the exact evolution.
- **State simulation** (`algorithms.simulate_state`) — a product-formula evolution's fidelity to
  the exact state, verified to approach 1 with more steps.
- **Order-scaling slope** (`algorithms.error_scaling_slope`) — the log-log error-vs-steps slope,
  verified ``~ -1/-2/-4`` for orders 1/2/4.
- **Commutator** (`algorithms.commutator`) — ``[A,B]=AB-BA``, the source of Trotter error.
- **Spectral norm** (`algorithms.spectral_norm`) — the operator norm used in the bounds.
- **Commutator sum** (`algorithms.commutator_sum`) — ``sum_{i<j}||[H_i,H_j]||`` controlling the
  first-order error.
- **First-order error bound** (`algorithms.first_order_error_bound`) — ``(t^2/2)sum||[H_i,H_j]||``,
  verified to upper-bound the actual error.
- **Second-order error bound** (`algorithms.second_order_error_bound`) — the nested-commutator
  cubic-in-``t`` bound, verified.
- **Commuting-terms test** (`algorithms.terms_commute`) — verifies the formula is exact when all
  terms commute.
- **qDRIFT distribution** (`algorithms.qdrift_probabilities`) — the importance-sampling
  ``p_k=|c_k|/lambda`` and the ``lambda`` normalization.
- **qDRIFT sample** (`algorithms.qdrift_sample_unitary`) — one random product of ``N`` sampled
  term-rotations.
- **qDRIFT channel** (`algorithms.qdrift_channel`) — the Monte-Carlo-averaged randomized
  evolution.
- **qDRIFT error** (`algorithms.qdrift_error`) — the trace-distance error, verified to decrease
  with the step count ``N``.
- **qDRIFT gate count** (`algorithms.qdrift_gate_count`) — ``~2 lambda^2 t^2/eps``, independent of
  the number of terms.
- **Taylor-series propagator** (`algorithms.taylor_series_unitary`) — the truncated
  ``sum (-iHt)^k/k!`` expansion.
- **Taylor error** (`algorithms.taylor_error`) — the truncation error, verified to fall
  factorially with the order.
- **Taylor truncation order** (`algorithms.taylor_truncation_order`) — the order for precision
  ``eps``, verified to bound the actual error.
- **Hamiltonian assembly** (`algorithms.hamiltonian_from_terms`) — the dense matrix from Pauli
  terms.
- **Series convergence** (`algorithms.series_convergence`) — the Taylor error across truncation
  orders, verified strictly decreasing.
- **Trotter step count** (`algorithms.trotter_first_order_steps`) — the steps for first-order
  precision from the error bound.
- **First-order gate count** (`algorithms.trotter_first_order_gate_count`) — steps times terms,
  the full first-order cost.
- **Second-order step count** (`algorithms.trotter_second_order_steps`) — the ``sqrt`` step count
  of the symmetric formula.
- **Taylor gate count** (`algorithms.taylor_gate_count`) — the ``log(1/eps)`` truncation order,
  exponentially better in precision.
- **qDRIFT-vs-Trotter crossover** (`algorithms.qdrift_beats_trotter`) — verifies qDRIFT wins for
  Hamiltonians with many terms.
- **Method selector** (`algorithms.cheapest_method`) — picks the lowest-gate-count method, e.g.
  Taylor at high precision.

## [2.2.0]

Theme: variational algorithms & QML theory — why (and when) parametrized quantum circuits
train. Exact parameter-shift gradients and Hessians, the barren-plateau phenomenon
(gradient variance vanishing exponentially in qubit number, and the local-cost cure),
ansatz expressibility (fidelity distributions vs. Haar, frame potentials) and entangling
capability (Meyer-Wallach), and the quantum geometric tensor / Fisher information behind
quantum natural gradient — verified against finite-difference gradients and closed forms.

### Added
- **Hardware-efficient ansatz** (`algorithms.hardware_efficient_ansatz`) — the ``Ry`` +
  CNOT-ladder variational circuit.
- **Ansatz parameter count** (`algorithms.ansatz_num_params`) — the ``n*layers`` parameter
  count of the ansatz.
- **Cost observable** (`algorithms.z_observable`) — the diagonal ``Z``-type cost operator.
- **Ansatz expectation** (`algorithms.ansatz_expectation`) — the variational cost
  ``<psi|O|psi>``, the objective the theory acts on.
- **Random parameters** (`algorithms.random_parameters`) — a random point in the training
  landscape.
- **Parameter-shift gradient** (`algorithms.parameter_shift_gradient`) — the exact analytic
  partial derivative from ``+/- pi/2`` shifts, verified against finite differences.
- **Full shift-rule gradient** (`algorithms.parameter_shift_gradient_all`) — the whole
  gradient vector, verified to match finite differences to machine precision.
- **Finite-difference gradient** (`algorithms.finite_difference_gradient`) — the numerical
  reference for the shift rule.
- **Parameter-shift Hessian** (`algorithms.parameter_shift_hessian_diagonal`) — the diagonal
  curvature from a second shift, verified against finite differences.
- **Gradient norm** (`algorithms.gradient_norm`) — the scalar training signal (small in a
  plateau).
- **Gradient variance** (`algorithms.gradient_sample_variance`) — the variance of a gradient
  over random parameters, the barren-plateau diagnostic.
- **Barren-plateau scaling** (`algorithms.barren_plateau_scaling`) — the global-cost gradient
  variance vs. qubit number, verified to shrink as the system grows.
- **Local-cost gradient variance** (`algorithms.local_cost_gradient_variance`) — the gradient
  variance for a single-qubit cost.
- **Global-cost gradient variance** (`algorithms.global_cost_gradient_variance`) — the
  gradient variance for the all-qubit cost.
- **Cost concentration** (`algorithms.cost_concentration`) — the variance of the cost value
  over random parameters, verified to decrease with system size.
- **Haar fidelity density** (`algorithms.haar_fidelity_pdf`) — the ``(N-1)(1-F)^{N-2}``
  reference distribution of Haar-random overlaps.
- **Haar mean fidelity** (`algorithms.haar_mean_fidelity`) — the ``1/N`` frame-potential
  target.
- **Ansatz fidelity sampling** (`algorithms.sample_ansatz_fidelities`) — the empirical overlap
  distribution used for expressibility.
- **Frame potential** (`algorithms.frame_potential`) — the average overlap, verified to
  approach the Haar value ``1/2^n`` for an expressive ansatz.
- **Expressibility (KL)** (`algorithms.expressibility_kl`) — the KL divergence from the Haar
  distribution, verified to decrease as layers are added.
- **Meyer-Wallach entanglement** (`algorithms.meyer_wallach`) — the global multipartite
  entanglement measure, verified 0 for product states and 1 for GHZ.
- **Product-state test** (`algorithms.is_product_state`) — the ``Q=0`` check for
  non-entangled states.
- **Entangling capability** (`algorithms.entangling_capability`) — the ansatz's average
  Meyer-Wallach entanglement, verified to grow with entangling layers.
- **Average entanglement** (`algorithms.average_entanglement`) — the mean Meyer-Wallach
  entanglement over a set of states.
- **Quantum geometric tensor** (`algorithms.quantum_geometric_tensor`) — the Fubini-Study
  metric of the ansatz, verified symmetric positive semi-definite.
- **Quantum Fisher matrix** (`algorithms.quantum_fisher_matrix`) — four times the geometric
  tensor, the metric for natural gradient and estimation.
- **Positive-semidefinite check** (`algorithms.is_positive_semidefinite`) — the metric
  validity test.
- **Quantum natural gradient** (`algorithms.natural_gradient`) — the metric-preconditioned
  update, verified to reduce to the ordinary gradient at an identity metric.
- **Fubini-Study distance** (`algorithms.fubini_study_distance`) — the geodesic distance
  between states, verified ``pi/4`` for product vs. GHZ.
- **Effective quantum dimension** (`algorithms.effective_quantum_dimension`) — the rank of the
  geometric tensor, the number of independent parameter directions.

## [2.1.0]

Theme: quantum optimization & QAOA theory — encoding hard problems as ground states and
solving them. QUBO/Ising encodings of MaxCut, number partitioning, and vertex cover; the
QAOA ansatz with its exact expectation and landscape; adiabatic optimization with the
minimum-gap and adiabatic-runtime bounds; Landau-Zener transitions; transverse-field
annealing; and Grover-based (Dürr-Høyer) minimization — every optimum verified against
brute force and every formula against its closed form.

### Added
- **QUBO objective** (`algorithms.qubo_energy`) — the ``x^T Q x`` binary objective.
- **Ising energy** (`algorithms.ising_energy`) — the spin energy ``sum h s + sum J s s``.
- **QUBO↔Ising conversion** (`algorithms.qubo_to_ising`) — the ``x=(1-s)/2`` map with offset,
  verified energy-equivalent over all assignments.
- **Ising Hamiltonian** (`algorithms.ising_hamiltonian`) — the diagonal quantum Hamiltonian
  whose ground state is the optimizer, verified against brute force.
- **Brute-force Ising** (`algorithms.brute_force_ising`) — the exact spin minimizer by
  enumeration, the verification oracle.
- **Brute-force QUBO** (`algorithms.brute_force_qubo`) — the exact binary minimizer by
  enumeration.
- **MaxCut encoding** (`algorithms.max_cut_qubo`) — the QUBO whose ground state is a maximum
  cut, verified against the true max cut.
- **Number-partition encoding** (`algorithms.number_partition_qubo`) — the balanced-partition
  QUBO, verified to yield an equal-sum split.
- **Vertex-cover encoding** (`algorithms.vertex_cover_qubo`) — the penalty-constrained minimum
  vertex cover, verified to produce a valid cover.
- **QAOA cost diagonal** (`algorithms.cost_diagonal`) — the MaxCut cost operator's diagonal
  (cut counts).
- **QAOA cost layer** (`algorithms.cost_layer`) — the ``e^{-i gamma C}`` phase-separation
  unitary.
- **QAOA mixer layer** (`algorithms.mixer_layer`) — the transverse-field mixer
  ``e^{-i beta sum X}``, verified norm-preserving.
- **QAOA state** (`algorithms.qaoa_state`) — the ``p``-layer ansatz state, normalized.
- **QAOA expectation** (`algorithms.qaoa_expectation`) — the exact cost expectation ``<C>``.
- **QAOA p=1 optimizer** (`algorithms.optimize_qaoa_p1`) — grid-searched best angles and
  approximation ratio, verified to beat random guessing (the ~0.75 ring ratio).
- **QAOA landscape** (`algorithms.qaoa_landscape`) — the ``(gamma, beta)`` energy surface.
- **Transverse-field driver** (`algorithms.transverse_field_driver`) — the ``H0 = -sum X``
  easy Hamiltonian with ground state ``|+>^n``.
- **Interpolating Hamiltonian** (`algorithms.interpolating_hamiltonian`) — the adiabatic path
  ``(1-s)H0 + s H1``.
- **Instantaneous gap** (`algorithms.instantaneous_gap`) — the ground-to-excited gap at a
  path point.
- **Minimum gap** (`algorithms.minimum_gap`) — the bottleneck gap along the path, verified
  positive for a non-crossing path.
- **Adiabatic evolution** (`algorithms.adiabatic_evolve`) — the time-dependent Schrödinger
  sweep of the ground state.
- **Adiabatic success probability** (`algorithms.adiabatic_success_probability`) — the final
  overlap with the target ground state, verified to approach 1 as the runtime grows.
- **Landau-Zener probability** (`algorithms.landau_zener_probability`) — the closed-form
  diabatic transition ``exp(-pi gap^2/4v)``, verified against a two-level sweep simulation.
- **Adiabatic runtime bound** (`algorithms.adiabatic_runtime_bound`) — the ``1/gap_min^2``
  cost scaling.
- **Anneal Hamiltonian** (`algorithms.anneal_hamiltonian`) — the ``A(s)(-sum X) + B(s) H``
  schedule.
- **Anneal gap** (`algorithms.spectral_gap_at`) — the instantaneous gap along the anneal.
- **Quantum anneal** (`algorithms.anneal`) — the linear-schedule anneal evolution.
- **Annealing success** (`algorithms.annealing_success_probability`) — the ground-state
  probability, verified to rise with anneal time.
- **Annealed solution** (`algorithms.annealed_solution`) — the most probable spin
  configuration, verified to match the exact Ising ground state for a slow anneal.
- **Threshold oracle** (`algorithms.threshold_marked`) — the marked set ``f(x) < best`` of
  Dürr-Høyer.
- **Dürr-Høyer minimization** (`algorithms.durr_hoyer_minimize`) — Grover-based minimum
  finding, verified to reach the global optimum with high success.
- **Grover adaptive search** (`algorithms.grover_adaptive_search`) — Dürr-Høyer applied to a
  function oracle, verified to reach the true minimum.
- **Optimization query scaling** (`algorithms.quantum_minimum_queries`,
  `classical_minimum_queries`) — the ``O(sqrt N)`` vs ``O(N)`` query counts.

## [2.0.0]

Theme: quantum compilation & circuit optimization — the milestone 2.0 release. The
transpiler stack that turns an abstract circuit into one a real device can run: a circuit
IR with exact-equivalence checking, peephole optimization (inverse cancellation, rotation
merging, identity removal), gate commutation, qubit routing with SWAP networks for limited
connectivity, two-qubit KAK synthesis and optimal CNOT counts, ASAP scheduling and depth
analysis, and gate-template decompositions (Toffoli → Clifford+T). Every rewrite is
verified to preserve the circuit's unitary.

### Added
- **Circuit IR** (`algorithms.op`, `circuit_unitary`) — the ``(matrix, qubits)`` operation
  representation and its full-unitary builder, the substrate for every compiler pass.
- **Equivalence oracle** (`algorithms.circuits_equivalent`) — tests two circuits for
  equal unitaries up to global phase, the correctness check every pass is verified against.
- **Circuit metrics** (`algorithms.gate_count`, `two_qubit_count`) — the gate and
  two-qubit-gate counts, the primary cost measures.
- **Inverse cancellation** (`algorithms.cancel_inverses`) — remove adjacent ``G, G^dagger``
  pairs, verified to preserve the unitary.
- **Identity removal** (`algorithms.remove_identities`) — delete identity operations.
- **Rotation merging** (`algorithms.merge_rotations`) — fuse consecutive diagonal rotations
  ``Rz(a)Rz(b)=Rz(a+b)``, verified equivalent.
- **Peephole optimizer** (`algorithms.optimize_circuit`) — iterate the local passes to a
  fixed point, verified to shrink the gate count while preserving the unitary.
- **Commutation test** (`algorithms.operations_commute`) — decide whether two operations
  commute (disjoint support or commuting matrices).
- **Commute-forward** (`algorithms.commute_forward`) — bubble an operation earlier through
  commuting neighbours, verified equivalent.
- **Commutation graph** (`algorithms.commutation_graph`) — the pairwise-commutation
  structure a scheduler uses.
- **Coupling map & executability** (`algorithms.coupling_map`, `is_executable`) — the device
  connectivity and the check that every two-qubit gate is on a connected pair.
- **Permutation unitary** (`algorithms.permutation_matrix`) — the unitary of a qubit
  permutation, the routing target.
- **SWAP network** (`algorithms.swap_network`) — decompose a permutation into adjacent SWAPs
  for a linear architecture, verified to compose to the permutation.
- **Linear routing** (`algorithms.route_linear`) — insert SWAPs to make a circuit executable
  on a line, verified executable and equivalent to the original.
- **SWAP template** (`algorithms.swap_decomposition`) — SWAP as three CNOTs, verified.
- **Controlled-Z template** (`algorithms.controlled_z_decomposition`) — CZ as ``H·CNOT·H``,
  verified.
- **Toffoli template** (`algorithms.toffoli_decomposition`, `toffoli_matrix`) — the 6-CNOT
  Clifford+T decomposition, verified equal to the Toffoli unitary.
- **Template verifier** (`algorithms.verify_template`) — check a decomposition's unitary
  against the gate it replaces.
- **Makhlin invariants** (`algorithms.makhlin_invariants`) — the local invariants ``(G1,G2)``
  of a two-qubit gate.
- **Local-gate detection** (`algorithms.is_local`) — recognize tensor-product (zero-CNOT)
  two-qubit gates via the Makhlin invariants, verified.
- **Local equivalence** (`algorithms.locally_equivalent`) — decide whether two gates differ
  only by single-qubit gates (CNOT ~ CZ, not ~ SWAP), verified.
- **Optimal CNOT count** (`algorithms.cnot_count`) — the minimal CNOTs (0-3) for a two-qubit
  gate from its magic-basis spectrum, verified local=0, CNOT/CZ=1, iSWAP=2, SWAP/generic=3.
- **ASAP scheduling** (`algorithms.asap_layers`, `flatten_layers`) — the earliest-layer
  schedule (parallel gates on disjoint qubits), verified to preserve the unitary.
- **Circuit depth** (`algorithms.circuit_depth`, `critical_path_length`) — the scheduled
  depth / critical-path length, verified against serial and parallel circuits.
- **Circuit parallelism** (`algorithms.circuit_parallelism`) — gates per time step, the
  parallelism the scheduler exposes.

## [1.9.0]

Theme: characterization & benchmarking — measuring how good a quantum device really is.
Randomized benchmarking (and interleaved RB for per-gate error), cross-entropy
benchmarking with the Porter-Thomas distribution, quantum volume via heavy outputs,
state tomography and direct fidelity estimation, channel metrics (average-gate /
entanglement fidelity, unitarity, Choi matrices), and mirror benchmarking — every
metric verified against exact channels and closed forms.

### Added
- **RB survival model** (`algorithms.rb_survival`) — the ``A p^m + B`` randomized-benchmarking
  decay with SPAM factored out.
- **RB decay fit** (`algorithms.fit_rb_decay`) — recover the decay rate ``p`` from
  (length, survival) data, verified to match a planted rate.
- **Average gate fidelity from RB** (`algorithms.average_gate_fidelity_from_rb`) —
  ``1 - (1-p)(d-1)/d`` from the decay rate.
- **Error per Clifford** (`algorithms.error_per_clifford`) — the ``(1-p)(d-1)/d`` headline RB
  number.
- **Interleaved RB** (`algorithms.interleaved_rb_gate_error`) — isolate a single gate's error
  from the reference/interleaved decays, verified against a planted error.
- **Porter-Thomas density** (`algorithms.porter_thomas_pdf`) — the ``D e^{-D p}`` speckle law
  of random-circuit outputs, verified normalized with mean ``1/D``.
- **Porter-Thomas sampling** (`algorithms.porter_thomas_samples`) — random probability
  vectors from the PT distribution, a stand-in for random-circuit outputs.
- **Linear XEB fidelity** (`algorithms.linear_xeb_fidelity`) — cross-entropy benchmarking
  ``D <p_ideal> - 1``, verified ~1 for ideal sampling and ~0 for uniform.
- **Speckle purity** (`algorithms.speckle_purity`) — the collision-probability shape check,
  ``~2`` for Porter-Thomas.
- **Cross-entropy fidelity** (`algorithms.cross_entropy_fidelity`) — the distribution-level
  XEB estimator, verified 1 (ideal) / 0 (uniform).
- **Heavy outputs** (`algorithms.heavy_outputs`) — the above-median outcomes a device must
  reproduce.
- **Heavy-output probability** (`algorithms.heavy_output_probability`) — the HOP observable,
  the quantum-volume metric.
- **Quantum-volume pass** (`algorithms.quantum_volume_pass`) — the ``HOP > 2/3`` pass
  criterion.
- **Ideal HOP asymptote** (`algorithms.ideal_heavy_output_probability`) — the ``(1+ln2)/2``
  value a perfect device approaches, verified.
- **Quantum volume** (`algorithms.quantum_volume`) — the ``2^n`` volume of the largest passing
  width.
- **Pauli expectations** (`algorithms.pauli_expectations`) — the full tomographic data set of
  a state.
- **State tomography** (`algorithms.state_tomography`, `is_physical_density_matrix`) — linear
  inversion ``rho = (1/2^n) sum <P> P``, verified to recover a random state exactly.
- **Direct fidelity estimation** (`algorithms.direct_fidelity_estimation`) — the
  Pauli-sampling fidelity estimator, verified equal to ``<psi|rho|psi>`` for a pure target.
- **Choi matrix** (`algorithms.choi_matrix`) — the channel-state dual, verified positive with
  trace ``d``.
- **Entanglement fidelity** (`algorithms.entanglement_fidelity`) — ``(1/d^2) sum |Tr(U†K)|^2``,
  the channel-to-unitary closeness, verified 1 for an exact gate.
- **Average gate fidelity** (`algorithms.average_gate_fidelity`) — the Haar-averaged
  ``(d F_e + 1)/(d+1)`` fidelity, verified 1 for an exact gate.
- **Pauli transfer matrix** (`algorithms.pauli_transfer_matrix`) — the real Pauli-basis
  representation of a channel.
- **Unitarity** (`algorithms.unitarity`) — the coherence of a channel from the PTM, verified
  1 for unitaries and ``decay^2`` for depolarizing.
- **Mirror benchmarking** (`algorithms.mirror_survival`, `depolarizing_layer`) — the
  circuit-then-inverse survival probability, verified 1 noiseless and decaying under noise.
- **Mirror decay curve** (`algorithms.mirror_fidelity_decay`) — the survival vs. depth curve,
  verified monotonically decreasing.

## [1.8.0]

Theme: continuous-variable & bosonic quantum computing — qubits are not the only way.
The Gaussian formalism (covariance matrices, symplectic transforms, Williamson
eigenvalues, purity and entropy), the Fock-space operators (creation/annihilation,
displacement, squeezing, coherent states), Wigner quasiprobability and its negativity,
bosonic error-correcting cat codes, and boson sampling (the matrix permanent, Hong-Ou-
Mandel interference) — verified against the closed forms of the harmonic oscillator.

### Added
- **Vacuum covariance** (`algorithms.vacuum_covariance`) — the identity covariance of the
  vacuum/coherent states, the reference for the ``sigma >= I`` uncertainty bound.
- **Squeezed covariance** (`algorithms.squeezed_covariance`) — squeezed-vacuum covariance
  ``diag(e^{-2r}, e^{2r})``, verified pure (symplectic eigenvalue 1).
- **Thermal covariance** (`algorithms.thermal_covariance`) — ``(2 n_bar + 1) I``, verified
  symplectic eigenvalue ``2 n_bar + 1`` and purity ``1/(2 n_bar + 1)``.
- **Symplectic eigenvalues** (`algorithms.symplectic_eigenvalues`) — the Williamson
  invariants from ``i Omega sigma``, the physicality and entropy inputs.
- **Physicality test** (`algorithms.is_physical_covariance`) — checks all symplectic
  eigenvalues ``>= 1`` (the uncertainty principle); rejects sub-vacuum noise.
- **Gaussian purity** (`algorithms.purity_gaussian`) — ``1/prod nu`` from the symplectic
  spectrum, verified 1 for pure states and ``1/(2 n_bar+1)`` for thermal.
- **Gaussian entropy** (`algorithms.gaussian_entropy`) — the von Neumann entropy of a
  Gaussian state, verified 0 for pure and positive for thermal.
- **Symplectic check** (`algorithms.is_symplectic`) — verifies ``S Omega S^T = Omega`` for a
  Gaussian transform.
- **Phase-rotation symplectic** (`algorithms.phase_rotation_symplectic`) — the passive phase
  shifter, verified symplectic.
- **Squeezing symplectic** (`algorithms.squeezing_symplectic`) — the active single-mode
  squeezer, verified symplectic.
- **Beamsplitter symplectic** (`algorithms.beamsplitter_symplectic`) — the two-mode passive
  mixer, verified symplectic.
- **Two-mode squeezing** (`algorithms.two_mode_squeezing_symplectic`, `apply_symplectic`) —
  the entangling EPR transform and covariance update, verified to create cross-mode
  correlations while staying physical.
- **Ladder operators** (`algorithms.annihilation_operator`, `creation_operator`,
  `number_operator_fock`) — the truncated Fock operators, verified ``[a,a^dagger]=I`` and
  ``N=a^dagger a``.
- **Coherent states** (`algorithms.coherent_state_fock`, `mean_photon_number`) — eigenstates
  of ``a`` with Poissonian statistics, verified ``a|alpha>=alpha|alpha>`` and
  ``<n>=|alpha|^2``.
- **Displacement operator** (`algorithms.displacement_operator`) — ``exp(alpha a^dagger -
  alpha^* a)``, verified to map the vacuum to ``|alpha>``.
- **Squeeze operator** (`algorithms.squeeze_operator`) — ``exp((r/2)(a^2 - a^{dagger 2}))``,
  verified to produce even-photon squeezed vacuum.
- **Wigner function** (`algorithms.wigner_point`, `wigner_grid`) — the displaced-parity
  quasiprobability, verified to match the analytic vacuum Gaussian.
- **Wigner normalization** (`algorithms.wigner_integral`) — the phase-space integral,
  verified to equal 1.
- **Wigner negativity** (`algorithms.wigner_negativity`) — the non-classicality witness,
  verified ~0 for the vacuum and positive for a cat state.
- **Husimi Q** (`algorithms.husimi_q`) — the non-negative coherent-state quasiprobability,
  verified ``1/pi`` at the vacuum peak.
- **Matrix permanent** (`algorithms.permanent`) — Ryser's #P-hard permanent, verified
  ``perm(ones_n)=n!`` and ``perm(I)=1``.
- **Boson-sampling probabilities** (`algorithms.boson_sampling_probability`,
  `beamsplitter_unitary`) — the ``|perm|^2`` output distribution, verified to normalize to 1.
- **Hong-Ou-Mandel effect** (`algorithms.hong_ou_mandel`) — two-photon interference,
  verified to bunch (coincidence 0) at the 50:50 beamsplitter.
- **Cat states** (`algorithms.cat_state`, `parity_operator`, `parity_expectation`) — even/odd
  Schrödinger cats, verified parity eigenstates of ``(-1)^N``.
- **Cat code** (`algorithms.cat_code_words`, `photon_loss`, `loss_flips_parity`) — the
  bosonic logical code words, verified orthogonal with photon loss flipping the parity (a
  detectable error).

## [1.7.0]

Theme: advanced quantum algorithms — the primitives beyond the textbook set. Quantum
walks (continuous- and discrete-time, Szegedy quantization) with their ballistic
spreading and spatial search, amplitude estimation without phase estimation (maximum
likelihood and iterative) at Heisenberg scaling, Markov-chain quantization and quantum
PageRank, and phase-estimation variants (Kitaev, robust) — verified against exact
evolution and closed forms.

### Added
- **Continuous-time walk propagator** (`algorithms.continuous_time_walk_operator`) — the
  unitary ``e^{-iAt}`` on a graph adjacency, verified unitary.
- **CTQW distribution** (`algorithms.ctqw_distribution`) — the walker's position
  probabilities, verified to conserve total probability.
- **Ballistic spreading** (`algorithms.position_variance`) — the walk's position variance,
  verified to grow as ``t^2`` (quadratically faster than the classical ``t``).
- **Path-graph adjacency** (`algorithms.line_adjacency`) — the line graph the walks run on.
- **Discrete-time quantum walk** (`algorithms.discrete_time_walk_line`) — the coined walk on
  a line, verified to give the ballistic twin-peaked distribution.
- **Szegedy walk** (`algorithms.szegedy_walk_operator`) — the unitary quantization of a
  Markov chain, verified unitary.
- **Spatial search** (`algorithms.spatial_search_ctqw`) — CTQW search for a marked vertex,
  verified to reach high success on the complete graph (the quadratic speedup).
- **Grover signal** (`algorithms.grover_probability`) — the ``sin^2((2m+1)theta)`` good-state
  probability that amplitude estimation fits.
- **Maximum-likelihood AE** (`algorithms.maximum_likelihood_ae`) — MLQAE without a
  phase-estimation register, verified to recover the amplitude with error shrinking as more
  Grover powers are added.
- **Iterative AE** (`algorithms.iterative_ae`) — branch-refining IQAE, verified to converge
  to the true amplitude at the Heisenberg limit.
- **Canonical AE** (`algorithms.canonical_qae`) — phase-estimation amplitude estimation,
  verified to reach ``O(2^-bits)`` precision.
- **Classical estimation error** (`algorithms.classical_monte_carlo_error`) — the
  ``1/sqrt(M)`` Monte-Carlo baseline rate.
- **Heisenberg-limited error** (`algorithms.heisenberg_scaling_error`) — the ``1/M`` quantum
  rate, the quadratic improvement.
- **Stochastic-matrix check** (`algorithms.is_stochastic`) — verifies non-negativity and
  unit line sums.
- **Stationary distribution** (`algorithms.stationary_distribution`) — the Perron
  eigenvector of a Markov chain, verified a fixed point summing to 1.
- **PageRank Google matrix** (`algorithms.google_matrix`) — the damped-surfer transition
  matrix, verified row-stochastic.
- **Classical PageRank** (`algorithms.classical_pagerank`) — node importance as the Google
  matrix's stationary distribution.
- **Detailed balance** (`algorithms.detailed_balance`) — the Markov-chain reversibility
  test.
- **Quantum PageRank** (`algorithms.quantum_pagerank`) — the Szegedy-walk (Paparo-Martin-
  Delgado) ranking, verified a valid distribution ranking the same top node as classical.
- **Kitaev phase estimation** (`algorithms.kitaev_phase_estimation`) — single-ancilla
  bit-by-bit phase readout, verified exact for dyadic phases and ``2^-bits``-precise.
- **Robust phase estimation** (`algorithms.robust_phase_estimation`) — two-basis
  generational estimation with branch unwrapping, verified to recover a known phase.
- **Phase-estimation resolution** (`algorithms.phase_estimation_error`) — the ``2^-bits``
  Heisenberg-limited precision.
- **Mean-encoding amplitude** (`algorithms.mean_amplitude`) — ``sqrt(E[f])``, the amplitude
  whose square is the expectation.
- **Quantum mean estimation** (`algorithms.quantum_mean_estimation`) — Monte-Carlo
  expectation via amplitude estimation, verified to recover the mean at Heisenberg scaling.
- **Monte-Carlo speedup** (`algorithms.classical_samples_for_precision`,
  `quantum_samples_for_precision`, `monte_carlo_speedup`) — the ``1/eps^2`` vs ``1/eps``
  sample counts and their quadratic ratio.

## [1.6.0]

Theme: fault tolerance & logical compilation — turning noisy physical qubits into
reliable logical ones. Magic-state distillation and its cubic error suppression,
gate teleportation and T-injection, transversal logical gates (and the Eastin-Knill
obstruction to a universal transversal set), code concatenation with double-exponential
error suppression below threshold, and Clifford+T / Solovay-Kitaev gate synthesis —
verified against closed forms and by logical-action checks on real codewords.

### Added
- **T and H magic states** (`algorithms.t_state`, `h_magic_state`) — the non-stabilizer
  resource states that inject non-Clifford gates.
- **Stabilizer fidelity** (`algorithms.stabilizer_fidelity`) — the maximum overlap with a
  stabilizer state, a magic monotone; ``cos^2(pi/8)`` for the T state (verified).
- **15-to-1 distillation error** (`algorithms.distillation_15to1_error`) — the analytic
  ``35 p^3`` output error, verified cubic and below-input for ``p < 1/sqrt(35)``.
- **Distillation threshold** (`algorithms.distillation_threshold`) — the ``1/sqrt(35)``
  break-even input error below which distillation converges.
- **Distillation round count** (`algorithms.distillation_rounds_to_target`) — the number of
  15-to-1 rounds to reach a target error (``-1`` above threshold).
- **One-level concatenation** (`algorithms.one_level_logical_error`) — the ``A p^2`` map of
  a distance-3 code.
- **Concatenated logical error** (`algorithms.concatenated_logical_error`) — the recursive
  logical error after ``L`` levels of concatenation.
- **Double-exponential check** (`algorithms.double_exponential_check`) — verifies the
  recursion equals the closed form ``p_th (p/p_th)^{2^L}`` (the threshold theorem).
- **Concatenation pseudothreshold** (`algorithms.pseudothreshold`) — the ``1/A`` crossover
  below which errors shrink per level.
- **Levels for a target** (`algorithms.levels_for_target`) — the concatenation depth needed
  for a target error (``-1`` above threshold).
- **Qubit overhead** (`algorithms.qubit_overhead`) — ``block^levels`` physical qubits per
  logical qubit under concatenation.
- **Transversal gate builder** (`algorithms.transversal_gate`) — ``g^{⊗n}``, the fault-safe
  logical-gate form.
- **Steane code words** (`algorithms.steane_codewords`) — the ``|0_L>, |1_L>`` logical basis
  from the stabilizer projector.
- **Code-space preservation** (`algorithms.preserves_code_space`) — checks a gate keeps the
  logical subspace (prerequisite for being a logical operation).
- **Logical action read-off** (`algorithms.logical_action`) — the ``2x2`` logical gate a
  transversal operation enacts on the code words.
- **Transversal Hadamard** (`algorithms.steane_transversal_hadamard_is_logical_h`) —
  confirms ``H^{⊗7}`` enacts the logical Hadamard on the Steane code.
- **Transversal phase gate** (`algorithms.steane_transversal_s_is_logical_phase`) — confirms
  ``S^{⊗7}`` enacts a logical phase gate.
- **Eastin-Knill obstruction** (`algorithms.eastin_knill_obstruction`) — demonstrates that
  ``T^{⊗7}`` leaves the Steane code space, so no transversal ``T`` exists (no universal
  transversal set).
- **Gate-teleportation resource** (`algorithms.resource_state`) — the ``(I⊗U)|Phi+>``
  offline state that carries a gate onto the data.
- **Gate teleportation** (`algorithms.gate_teleportation`) — teleport a Clifford gate via a
  Bell measurement, verified recoverable with a Pauli correction (and correctly *not* for
  non-Clifford ``T``).
- **T-injection** (`algorithms.t_injection`) — inject a logical ``T`` from a magic state
  with an adaptive ``S`` correction; verified to produce ``T|psi>`` — the route to
  universality past Eastin-Knill.
- **Clifford+T net** (`algorithms.enumerate_clifford_t`) — enumerate Clifford+T words
  deduplicated up to global phase, the finite Solovay-Kitaev net.
- **Gate synthesis** (`algorithms.synthesize`, `synthesize_rz`) — the best Clifford+T
  approximation of a target gate; verified exact for ``pi/4`` multiples and any reachable
  gate.
- **Gate distance** (`algorithms.gate_distance`) — the phase-invariant process-fidelity
  metric between single-qubit gates.
- **T-count & gate-set check** (`algorithms.t_count`, `is_clifford_t_word`, `rz`) — the
  fault-tolerant ``T``-cost, the Clifford+T membership test, and the ``Rz`` target.

## [1.5.0]

Theme: quantum information & resource theories — how to *quantify* quantum resources.
State-distinguishability (trace distance, Uhlmann fidelity, Bures metric, relative
entropy), the entropy family (von Neumann, Rényi, Tsallis, conditional, mutual
information), coherence measures (l1, relative entropy, robustness), entanglement
measures (concurrence, entanglement of formation, tangle, realignment/CCNR witness),
and the majorization order behind LOCC convertibility (Nielsen's theorem) — every
measure verified against Bell/Werner/product states and closed forms.

### Added
- **Trace distance** (`algorithms.trace_distance`) — ``(1/2)||rho-sigma||_1``, the optimal
  distinguishing bias; verified 1 for orthogonal states, 0 for equal.
- **Uhlmann fidelity** (`algorithms.uhlmann_fidelity`) — ``(Tr sqrt(sqrt(rho) sigma
  sqrt(rho)))^2``; reduces to ``|<psi|phi>|^2`` for pure states (verified).
- **Bures distance & angle** (`algorithms.bures_distance`, `bures_angle`) — the
  fidelity-induced metric and geodesic angle on state space.
- **Hilbert-Schmidt distance** (`algorithms.hilbert_schmidt_distance`) — the ``L2`` metric
  ``sqrt(Tr[(rho-sigma)^2])``.
- **Fuchs-van de Graaf bounds** (`algorithms.fuchs_van_de_graaf`) — the inequalities
  ``1-sqrt(F) <= T <= sqrt(1-F)``, verified on random state pairs.
- **Quantum relative entropy** (`algorithms.quantum_relative_entropy`) —
  ``Tr rho(log rho - log sigma)``, non-negative by Klein's inequality (verified), ``+inf``
  on support mismatch.
- **von Neumann entropy** (`algorithms.von_neumann_entropy`) — ``-Tr rho log rho``; 0 for
  pure, ``log d`` for maximally mixed.
- **Rényi entropy** (`algorithms.renyi_entropy`) — the ``alpha``-family, verified to
  recover von Neumann as ``alpha->1`` and ``log rank`` as ``alpha->0``.
- **Tsallis entropy** (`algorithms.tsallis_entropy`) — the non-additive ``q``-entropy,
  reducing to von Neumann as ``q->1``.
- **Conditional entropy** (`algorithms.conditional_entropy`) — ``S(A|B)=S(AB)-S(B)``,
  verified negative (``-1``) for a Bell state — a signature of entanglement.
- **Quantum mutual information** (`algorithms.quantum_mutual_information`) —
  ``S(A)+S(B)-S(AB)``, total correlations; ``2`` bits for a Bell pair (verified).
- **Bipartite entanglement entropy** (`algorithms.entanglement_entropy_pure`) — the
  reduced-state entropy of a pure state, from its Schmidt spectrum.
- **l1 coherence** (`algorithms.l1_coherence`) — summed off-diagonal magnitude; ``d-1`` for
  a maximally coherent state, 0 for a diagonal one (verified).
- **Relative entropy of coherence** (`algorithms.relative_entropy_of_coherence`) —
  ``S(rho_diag)-S(rho)``, the distillable coherence; ``log d`` for maximal coherence.
- **Robustness of coherence** (`algorithms.robustness_of_coherence`) — the minimal mixing
  that destroys coherence (``2|rho_01|`` for a qubit).
- **Incoherence test & dephasing** (`algorithms.is_incoherent`, `dephase`) — the diagonal
  (incoherent) projection and its check.
- **Wootters concurrence** (`algorithms.concurrence`) — closed-form two-qubit
  entanglement; verified 1 for Bell, 0 for product, and matching the Werner ``(3p-1)/2``.
- **Entanglement of formation** (`algorithms.entanglement_of_formation`) — from the
  concurrence via the binary entropy; ``1`` bit for a Bell pair.
- **Tangle** (`algorithms.tangle`) — concurrence squared, the CKW-monogamous measure.
- **Schmidt decomposition** (`algorithms.schmidt_coefficients`, `schmidt_rank`) — the
  bipartite pure-state coefficients and rank (1 iff a product state).
- **Majorization test** (`algorithms.majorizes`) — the ``x > y`` partial order behind
  resource monotones, verified on peaked/flat distributions.
- **Nielsen's theorem** (`algorithms.nielsen_convertible`) — pure-state LOCC
  convertibility via Schmidt-vector majorization; verified directional (max-entangled
  converts down, not up).
- **Schur-concavity entropy bound** (`algorithms.majorization_entropy_bound`) — the entropy
  ordering implied by majorization.
- **Entanglement witnesses** (`algorithms.witness_expectation`, `bell_witness`) — a
  Hermitian operator whose negative expectation proves entanglement; verified on Bell vs.
  maximally mixed.
- **Realignment (CCNR) criterion** (`algorithms.realignment_criterion`, `realign`,
  `realignment_norm`) — the computable cross-norm test ``||R(rho)||_1 > 1``; verified to
  fire on a Bell state (norm 2) and not on the mixed state.

## [1.4.0]

Theme: quantum chemistry & electronic structure — the flagship near-term application.
Fermion-to-qubit mappings (Jordan-Wigner, parity, Bravyi-Kitaev), second-quantized
molecular Hamiltonians with published STO-3G integrals, particle-number-conserving
ansätze (Hartree-Fock, Givens rotations, UCCSD), Z2 qubit tapering and measurement
grouping, and excited-state / adaptive solvers (SSVQE, ADAPT-VQE) — every energy
verified against exact diagonalization or published FCI values.

### Added
- **Jordan-Wigner mapping** (`algorithms.jordan_wigner_annihilation`,
  `fock_annihilation`) — the fermionic annihilation operator with its parity-``Z`` string,
  verified to satisfy the canonical anticommutation relations.
- **Parity mapping** (`algorithms.parity_annihilation`, `parity_matrix`) — the
  partial-sum encoding, verified to satisfy the CAR and give an identical spectrum to
  Jordan-Wigner.
- **Bravyi-Kitaev mapping** (`algorithms.bravyi_kitaev_annihilation`,
  `bravyi_kitaev_matrix`) — the Fenwick-tree encoding, verified to satisfy the CAR, match
  the spectrum, and reduce operator locality (Pauli weight) versus Jordan-Wigner.
- **General fermion encoding** (`algorithms.encoded_annihilation`) — any invertible
  GF(2) encoding matrix ``beta`` as a basis change of the physical operators.
- **CAR verification** (`algorithms.satisfies_car`) — checks
  ``{a_i, a_j^dagger} = delta_ij`` and ``{a_i, a_j} = 0`` for a set of operators.
- **Operator locality** (`algorithms.pauli_weight`) — the maximum Pauli weight of an
  operator, the metric behind the Bravyi-Kitaev locality improvement.
- **Second-quantized molecular Hamiltonian** (`algorithms.molecular_hamiltonian`) —
  assemble ``sum h_pq a_p^d a_q + sum h_pqrs a_p^d a_q^d a_r a_s`` on qubits under any
  mapping; verified against the non-interacting closed form (sum of lowest orbital
  energies) and the Hubbard dimer.
- **Particle-number operator** (`algorithms.number_operator`) — ``N = sum a_j^d a_j``,
  used to project onto electron-number sectors.
- **Full-CI ground energy** (`algorithms.fci_energy`) — the exact lowest eigenvalue in a
  fixed particle-number sector; matches the analytic Hubbard-dimer energy
  ``(U - sqrt(U^2+16t^2))/2`` to machine precision across all three mappings.
- **Hartree-Fock energy** (`algorithms.hartree_fock_energy`) — the mean-field (single
  determinant) energy, verified to be a variational upper bound on FCI.
- **Hubbard dimer** (`algorithms.hubbard_dimer_hamiltonian`) — the two-site
  closed-form-solvable model that anchors the molecular-builder verification.
- **Hartree-Fock reference state** (`algorithms.hartree_fock_state`) — the occupation
  determinant with the lowest orbitals filled; verified at the right electron count.
- **Givens rotations** (`algorithms.givens_rotation`) — orbital-rotation single
  excitations ``exp(theta(a_p^d a_q - h.c.))``, verified unitary and particle-conserving.
- **UCCSD ansatz** (`algorithms.uccsd_operator`) — the unitary coupled-cluster
  singles-and-doubles operator ``exp(T - T^dagger)``, verified unitary and
  number-conserving on a Hartree-Fock input.
- **Ansatz symmetry checks** (`algorithms.conserves_particle_number`, `is_unitary`) — the
  ``[U,N]=0`` and unitarity tests every chemistry ansatz must pass.
- **One-particle RDM** (`algorithms.one_particle_rdm`) — ``D_pq = <a_p^d a_q>``, verified
  Hermitian with trace equal to the particle number.
- **Two-particle RDM** (`algorithms.two_particle_rdm`) — ``d_pqrs = <a_p^d a_q^d a_r a_s>``,
  the source of the electron-repulsion energy.
- **Energy from RDMs** (`algorithms.energy_from_rdm`) — reconstruct the molecular energy
  from the one- and two-particle RDMs; verified equal to the direct expectation ``<H>``.
- **Natural-orbital occupations** (`algorithms.natural_orbital_occupations`) — the 1-RDM
  eigenvalues in ``[0,1]``, a correlation diagnostic (0/1 for a single determinant).
- **Z2 symmetry finder** (`algorithms.z2_symmetry_generators`) — the Pauli symmetries of a
  Hamiltonian from the GF(2) kernel of its term matrix; verified to commute with ``H`` and
  square to the identity.
- **Qubit tapering** (`algorithms.taper_energy`, `sector_projector`,
  `spectrum_is_union_of_sectors`) — remove a qubit per Z2 symmetry by fixing a ``+/-1``
  sector; verified that the full spectrum equals the union of sector spectra.
- **Qubit-wise commuting groups** (`algorithms.qubit_wise_commuting_groups`) — partition
  Pauli terms into single-rotation-measurable groups; verified valid and covering.
- **General commuting groups** (`algorithms.commuting_groups`) — coarser commuting
  partitions (never more groups than QWC), verified.
- **Measurement reduction report** (`algorithms.measurement_reduction`,
  `is_valid_grouping`) — terms vs. QWC vs. commuting settings, the shot-cost saving of
  grouping.
- **Folded-spectrum targeting** (`algorithms.folded_spectrum_operator`,
  `nearest_eigenstate`) — reach an interior eigenstate by minimizing ``(H-omega)^2``;
  verified to return the exact eigenpair nearest ``omega``.
- **Rayleigh-Ritz subspace energies** (`algorithms.subspace_energies`) — variational
  eigenvalue estimates from a trial subspace, exact on an invariant subspace (verified).
- **SSVQE cost** (`algorithms.ssvqe_cost`) — the weighted-energy objective of
  subspace-search VQE, verified minimized by the lowest eigenstates.
- **Variational deflation** (`algorithms.deflation_hamiltonian`,
  `excited_spectrum_by_deflation`) — penalize found states to reach the next excited one;
  verified to recover the exact low-lying spectrum in order.

## [1.3.0]

Theme: topological codes & scalable QEC — beyond the original roadmap. The surface /
toric code family on the stabilizer engine: lattice stabilizers, logical operators,
syndrome extraction, and decoding, verified against the code's known properties.

### Added
- **General CSS code constructor** (`algorithms.CSSCode`) — a code from any pair of
  classical checks `Hx, Hz` with `Hx Hz^T = 0`; computes `all_commute`, the parameters
  `k = n - rank(Hx) - rank(Hz)`, and validates the CSS condition. Verified on the Steane
  `[[7,1,3]]` and `[[4,2,2]]` codes.
- **GF(2) linear algebra** (`algorithms.gf2_rank`, `gf2_nullspace`, `gf2_rref`) — binary
  row reduction, rank, and null-space bases — the engine under every stabilizer-code
  computation; verified `M v = 0` for null-space vectors.
- **CSS logical operators** (`CSSCode.logical_operators`) — representative `Xbar`/`Zbar`
  from the GF(2) kernels modulo the stabilizer row space; verified to anticommute in
  pairs and commute with all stabilizers.
- **CSS code distance** (`CSSCode.distance`) — the minimum weight of a nontrivial logical
  operator by exhaustive kernel search; verified `d = 3` for Steane, `d = 2` for
  `[[4,2,2]]`.
- **CSS syndromes** (`CSSCode.x_syndrome`, `z_syndrome`) — X errors detected by the
  Z-checks and vice versa, splitting decoding into two classical problems.
- **Minimum-weight CSS decoder** (`CSSCode.decode_min_weight`) — the lowest-weight error
  matching a syndrome within a search radius (optimal within it); verified to correct
  every error up to `(d-1)//2`.
- **CSS syndrome lookup table** (`CSSCode.decode_lookup`) — the full minimum-weight
  syndrome→correction table for small codes, the reference optimal decoder.
- **Self-dual CSS from a classical code** (`algorithms.css_from_classical`) — builds
  `Hx = Hz = H` from a weakly self-dual `H` (`H H^T = 0`); the family with a transversal
  Hadamard (Steane / color codes), verified to reproduce Steane.
- **Hypergraph-product codes** (`algorithms.hypergraph_product`) — the Tillich-Zemor
  construction turning any two classical codes into a quantum LDPC code, CSS by
  construction; verified `Hx Hz^T = 0` and used to build the surface code.
- **Repetition & Hamming check matrices** (`algorithms.repetition_check_matrix`,
  `hamming_check_matrix`) — the classical seeds of the surface (repetition) and color
  (Hamming) codes.
- **Planar surface code** (`algorithms.planar_surface_code`) — the distance-`d`
  `[[d^2+(d-1)^2, 1, d]]` code as the hypergraph product of two repetition codes;
  verified to have exactly the advertised parameters (`[[13,1,3]]`, `[[41,1,5]]`) and CSS
  commutation.
- **Surface-code parameters** (`algorithms.surface_code_parameters`) — the closed-form
  `[[n, k, d]]` of the distance-`d` planar code.
- **Weight-`t` correction proof** (`algorithms.corrects_all_errors_up_to`) — exhaustively
  verifies a code's minimum-weight decoder returns every error up to a given weight to
  the code space with no residual logical — the operational meaning of the distance.
- **Steane color code** (`algorithms.steane_color_code`) — the `[[7,1,3]]` code as the
  smallest 2D (triangular) color code, a self-dual CSS code.
- **Self-duality test** (`algorithms.is_self_dual_css`) — checks `rowspace(Hx) =
  rowspace(Hz)`, the exact condition for a transversal Hadamard; verified true for the
  color code and false for the surface code.
- **Transversal Hadamard verification** (`algorithms.transversal_hadamard_valid`) —
  confirms `H^{⊗n}` preserves the stabilizer group and exchanges `Xbar <-> Zbar` on a
  self-dual code — the color code's headline advantage.
- **Transversal CNOT verification** (`algorithms.transversal_cnot_valid`) — confirms the
  transversal CNOT between two blocks preserves the joint stabilizer group (true for
  every CSS code), checked via GF(2) row-space membership.
- **Toric code parameters** (`ToricCode.code_parameters`) — the `[[2L^2, 2, L]]`
  parameters of the `L x L` toric code; verified for `L = 3, 4, 5`.
- **Toric logical operators** (`ToricCode.logical_operators`) — the tracked
  non-contractible `Xbar`/`Zbar` loop pair, commuting with the stabilizers and
  anticommuting with each other.
- **Logical-error classification** (`ToricCode.logical_class`) — classifies a syndrome-free
  residual as `I / X / Y / Z` from its symplectic overlap with the logical operators;
  verified that a stabilizer maps to `I` and each logical to its own class.
- **Class-aware decoding** (`ToricCode.decode_z_class`) — decodes a `Z` error and reports
  the logical class of the residual — the direct test of decoder *success* (`I`) versus a
  logical fault; verified that every weight-1 error decodes to `I` and a pure logical
  loop is detected as a fault.
- **Combined CSS decoder** (`ToricCode.decode_pauli`) — decode a general Pauli error
  (its `X` and `Z` parts, a `Y` setting both) by running the independent `X` and `Z`
  decoders, as the CSS structure allows. Verified to correct every single-qubit
  Pauli error (X, Y, Z on any qubit) for L = 3, 4 (54/54, 96/96), with a `Y` error
  correctly triggering both the star and plaquette syndromes.
- **Toric-code X-error decoder** (`ToricCode.x_syndrome`, `decode_x`) — the dual of
  the Z decoder: `X` errors light up plaquette (face) defects, matched on the dual
  lattice, with logical `X` flips detected against the logical `Z` loop. Verified to
  correct every weight-1 `X` error for L = 3, 4, 5, with a whole star (X-stabilizer)
  giving no syndrome and a logical loop correctly flagged — completing correction for
  both error types.
- **Toric-code decoder** (`ToricCode.z_syndrome`, `decode_z`) — the practical heart of
  surface-code QEC: a `Z`-error lights up the star defects at its string endpoints
  (always an even number); the decoder pairs them by exact minimum-weight perfect
  matching on the torus and applies the shortest-path recovery, then checks whether
  error + correction is a harmless stabilizer or a logical flip. Verified: **every**
  weight-1 error is corrected for L = 3, 4, 5 (18/18, 32/32, 50/50), a stabilizer
  (whole plaquette) triggers no syndrome, and a full logical loop is correctly flagged
  as an uncorrectable logical error with a trivial syndrome.
- **Toric code** (`algorithms.ToricCode`) — Kitaev's topological code on an `L x L`
  periodic lattice (`2L^2` edge qubits): local star (`X`) and plaquette (`Z`)
  stabilizers, built from the binary symplectic check matrix. Verified against the
  code's defining properties for L = 2, 3, 4: every stabilizer commutes, the two
  product constraints reduce the rank to `2L^2 - 2` so the code always encodes exactly
  **2 logical qubits**, the logical operators (non-contractible loops) commute with all
  stabilizers but anticommute with each other, and the code distance equals `L` — the
  foundation of surface-code fault tolerance.

## [1.2.0]

Theme: hardware realism & error mitigation — the NISQ capstone that completes the
roadmap. The full toolbox for squeezing signal out of noisy hardware, each technique
verified to recover the noise-free expectation on the density-matrix engine:
**readout-error mitigation** (assignment-matrix inversion), **virtual distillation**
(purification by `rho^m`), **symmetry verification** (post-selection onto the right
sector), **probabilistic error cancellation** (quasi-probability channel inverse),
**zero-noise extrapolation** (noise folding + extrapolation), **Pauli twirling**
(tailoring coherent noise into stochastic form), and **Clifford Data Regression**
(learning the correction from classically-simulable training circuits). With this,
the original v0.8 → v1.2 roadmap is complete.

### Added
- **Richardson extrapolation for ZNE** (`algorithms.richardson_extrapolate`) — the
  degree-`(n-1)` polynomial through `n` noise-scaled points evaluated at zero noise
  (Lagrange at 0); recovers the `lambda=0` value of any polynomial of matching degree
  exactly.
- **Least-squares polynomial ZNE** (`algorithms.polynomial_extrapolate`) — an
  over-determined polynomial fit for noisy data, exact for a polynomial of the fitted
  degree.
- **Exponential ZNE** (`algorithms.exponential_extrapolate`) — fits
  `A + B e^{-c lambda}`, the geometric decay of a depolarizing-like channel, and returns
  the zero-noise value; inverts the ansatz exactly.
- **Adaptive ZNE model selection** (`algorithms.adaptive_extrapolate`) — scores the
  linear/quadratic/exponential fits by leave-one-out error and returns the best, so the
  extrapolation model is chosen by the data instead of assumed.
- **Global unitary folding** (`algorithms.fold_global`, `noise_scale_factor`) — the noise
  amplifier `G -> G (G† G)^k` that scales error by the odd factor `2k+1` while leaving the
  ideal action untouched (verified equal to `G` to machine precision) — the front end ZNE
  extrapolates over.
- **Local gate folding** (`algorithms.fold_gate_sequence`) — folds individual gates
  (`G -> G, G†, G`) for fine-grained, non-integer noise scaling; verified to preserve the
  overall unitary.
- **Folded noisy-layer model** (`algorithms.folded_channel_expectation`) — the
  density-matrix expectation with the noise channel applied `2k+1` times, the data ZNE
  fits; verified to reproduce the geometric noise amplification.
- **Tensored readout calibration** (`algorithms.tensored_assignment_matrix`,
  `tensored_mitigate`) — factorized per-qubit calibration `⊗_q A_q` inverted as a product
  of `2x2` inverses (never forming the exponential full matrix); recovers the true
  distribution exactly for independent readout noise.
- **Iterative Bayesian unfolding** (`algorithms.iterative_bayesian_unfolding`) — an
  expectation-maximization readout corrector that stays a valid probability vector
  (nonnegative, normalized) at every step, unlike a raw matrix inverse; converges to the
  true distribution.
- **Constrained least-squares readout** (`algorithms.constrained_readout_mitigate`) —
  readout correction as non-negative least squares with a normalization constraint,
  always returning a physical distribution; recovers the exact input.
- **Readout calibration from data** (`algorithms.calibrate_assignment_matrix`) — builds
  the assignment matrix column-by-column from prepare-and-measure calibration data;
  recovers the true matrix exactly.
- **Channel Pauli transfer matrix** (`algorithms.channel_ptm`, `invert_channel_ptm`) — the
  real `4x4` PTM of a single-qubit channel from its Kraus operators and its inverse (the
  quasiprobability cancellation map); verified `N^{-1} N = I`.
- **PEC sampling overhead** (`algorithms.pec_sampling_overhead`,
  `pauli_quasiprobabilities`, `depolarizing_overhead`) — the one-norm `gamma = sum_i|c_i|`
  of the inverse channel's Pauli-quasiprobability decomposition (the shot-cost of
  cancelling the noise), `1` for the identity and matching the closed form
  `(1+p/2)/(1-p)` for depolarizing.
- **PEC by inverse-PTM cancellation** (`algorithms.pec_mitigate_ptm`) — applies the
  inverse PTM to the noisy state's Pauli vector to recover an observable's exact noiseless
  expectation; verified against the ideal value.
- **CPMG dynamical decoupling** (`algorithms.cpmg_sequence`) — `n` equally spaced
  pi-pulses that refocus quasi-static dephasing (zero-mean switching function) and, by
  repetition, noise with a finite correlation time.
- **XY4 dynamical decoupling** (`algorithms.xy4_sequence`) — alternating `X, Y, X, Y`
  pulses that decouple a *general* single-qubit system-bath coupling and are robust to
  pulse errors — the hardware workhorse.
- **Uhrig dynamical decoupling (UDD)** (`algorithms.udd_sequence`) — the optimal pulse
  timings `sin^2(pi j/(2n+2))` that cancel the first `n` moments of the dephasing,
  suppressing decay to order `T^{n+1}` — verified to achieve decoupling order exactly `n`.
- **DD switching-function analysis** (`algorithms.switching_function_moments`,
  `suppression_order`) — the moments `M_m = ∫ s(t) t^m dt` whose leading zeros give a
  sequence's decoupling order, the closed-form test behind the UDD/CPMG verification.
- **DD coherence model** (`algorithms.dd_coherence`) — the ensemble-averaged `|+>`
  coherence after a sequence under quasi-static dephasing; equals 1 when the sequence
  refocuses (`M_0=0`) and `exp(-(sigma M_0)^2/2)` otherwise, verified against the closed
  form.
- **Clifford Data Regression (CDR)** (`algorithms.cdr_mitigate`, `fit_cdr_model`,
  `apply_cdr`) — learning-based mitigation that needs no noise model: because
  near-Clifford circuits are classically simulable, fit `ideal ~= slope*noisy +
  intercept` on training states where both values are known, then correct the real
  circuit's noisy result. Verified: the fit recovers an exact linear relation
  (`R^2 = 1`), a global-depolarizing channel gives a pure rescaling (`slope > 1`,
  `intercept ~ 0`), and applying the learned model corrects a Bell-state target from
  raw error > 0.1 to < 1e-6.
- **Pauli twirling** (`algorithms.pauli_twirl`, `coherent_error_kraus`) — tailor
  hard-to-handle coherent noise into stochastic Pauli noise by averaging over
  Pauli conjugations, `N_twirled = (1/4^n) sum_P P† N(P . P†) P`. Verified: the twirled
  channel is always a Pauli channel (diagonal PTM) — a coherent `Rx(theta)`
  over-rotation becomes exactly `cos^2(theta/2) I + sin^2(theta/2) X`, amplitude
  damping becomes Pauli too — while the average gate fidelity is preserved, and an
  already-Pauli channel (depolarizing) is a fixed point. Rounds out the mitigation
  capstone: readout, virtual distillation, symmetry verification, PEC, ZNE, and now
  noise tailoring.
- **Zero-noise extrapolation (ZNE)** (`algorithms.zero_noise_extrapolation`,
  `extrapolate_zero_noise`, `fold_noise_expectation`) — the flagship mitigation
  method: amplify the noise by folding (apply the noise layer `c` times), measure the
  observable at each scale, and extrapolate to the zero-noise limit (linear/Richardson
  or exponential). Verified on a depolarized Bell state where `<ZZ>` decays exactly
  geometrically — the exponential fit recovers the ideal to 1e-9 (raw error 0.19),
  linear extrapolation beats the raw value, and the amplified values decrease
  monotonically with noise scale. Complements the mitigation suite: readout, virtual
  distillation, symmetry verification, PEC, and now ZNE.
- **Probabilistic error cancellation (PEC)** (`algorithms.invert_pauli_channel`,
  `pec_mitigate`, `depolarizing_coeffs`, `apply_pauli_channel`) — invert a noise
  channel as a signed quasi-probability over Paulis (`N^{-1} = sum b_i P_i . P_i`,
  `sum b_i = 1`, some `b_i < 0`) with the sampling overhead `gamma = sum |b_i|`.
  Verified: the inverse exactly cancels depolarizing noise at every strength (recovering
  the density matrix and the noise-free expectation to 1e-9), the quasi-probabilities
  sum to 1, the overhead is `>= 1` and grows with the noise (the `gamma^2` variance
  cost), and zero noise gives the identity inverse.
- **Symmetry verification** (`algorithms.symmetry_project`,
  `symmetry_verified_expectation`) — post-select onto the symmetry sector the ideal
  state belongs to, discarding runs where an error broke the symmetry:
  `rho -> P rho P / Tr(P rho)`. Verified on a bit-flipped Bell state whose single-flip
  errors leave the even-parity sector — post-selecting `ZZ = +1` restores the fidelity
  from 0.745 to 1.0 (acceptance 0.745), the projected state is a valid density matrix
  in the target sector, a perfect state is left untouched, and the wrong sector rejects
  most of the population.
- **Virtual distillation** (`algorithms.virtual_distillation`, `distillation_report`)
  — error mitigation by purification: the corrected expectation `Tr(O rho^m)/Tr(rho^m)`
  concentrates weight on the noisy state's dominant eigenvector, approaching the
  noise-free value without any error correction. Verified on a depolarized Bell state
  (`<ZZ>` error 0.36 raw → 0.058 at `m=2` → 0.008 at `m=3`), higher order reducing the
  error further and converging to the dominant-eigenvector expectation, `m=1`
  recovering the raw value, and a pure state left unchanged.
- **Readout error mitigation** (`algorithms.assignment_matrix`, `mitigate_readout`,
  `mitigate_expectation`, `apply_readout_noise`) — undo measurement bit-flips: build
  the readout assignment matrix from single-qubit flip probabilities and correct a
  noisy histogram by solving `A p_true = p_measured` (then clip + renormalize).
  Verified to recover the exact noise-free distribution (a GHZ readout mitigated to
  0 error vs 0.11 uncorrected), always beat the uncorrected distribution, return a
  valid probability distribution, and reduce to the identity when there is no noise;
  `mitigate_expectation` corrects a diagonal observable's value likewise.

## [1.1.0]

Theme: QSVT & modern algorithm primitives — the unifying framework behind today's
quantum algorithms, built bottom-up and verified at every layer. **Quantum Signal
Processing** (designable polynomials of a scalar, Chebyshev at zero phase); the two
input models — **block encoding** (a matrix in the corner of a unitary) and **LCU**
(a Pauli sum via PREPARE/SELECT) — plus **qubitization** (matrix Chebyshev
polynomials from a quantum walk); **QSVT** itself (verified to apply the same scalar
function eigenvalue-by-eigenvalue — the theorem, to machine precision); and the
headline applications built on it: **Hamiltonian simulation** `e^{-iHt}` and
**quantum linear systems** `A^{-1}b`, each matching exact diagonalization. The single
primitive from which amplitude amplification, Hamiltonian simulation, and quantum
linear algebra all descend.

### Added
- **QSVT matrix functions on a sub-interval** (`algorithms.matrix_function_on_interval`)
  — the interval-aware companion to the `[-1,1]` fit: for a function analytic only on a
  positive sub-interval `[a,b]` (roots, log), rescale to `y = (2A-(a+b)I)/(b-a)` and fit
  there so the Chebyshev series stays on the analytic region and converges geometrically.
  Verified against the exact matrix function.
- **Matrix sign function** (`algorithms.matrix_sign_qsvt`) — `sign(A)` (`+1`/`-1` on the
  positive/negative eigenspaces) via an erf-smoothed sign whose sharpness matches the
  spectral gap; verified against the exact sign on gapped spectra (`~1e-5`).
- **Spectral projectors & eigenvalue thresholding** (`algorithms.spectral_projector_qsvt`)
  — `(I ± sign(A - threshold))/2`, the projector onto eigenvalues above/below a cut;
  verified idempotent and equal to the exact spectral projector.
- **Matrix square root & inverse square root** (`algorithms.matrix_sqrt_qsvt`,
  `matrix_inverse_sqrt_qsvt`) — `sqrt(A)` (with `sqrt(A)^2 = A`) and the whitening
  `A^{-1/2}` (`A^{-1/2} A A^{-1/2} = I`), interval-rescaled; machine-precision against
  `scipy.linalg.sqrtm`.
- **General matrix power** (`algorithms.matrix_power_qsvt`) — `A^p` for any real exponent
  (integer, fractional, negative) of a positive-definite `A`; verified against
  `sum_i lambda_i^p |v_i><v_i|`.
- **Regularized pseudo-inverse** (`algorithms.pseudo_inverse_qsvt`) — the Moore-Penrose
  inverse via the Tikhonov QSVT filter `x/(x^2+eps)`, which annihilates the kernel
  instead of blowing up. The QSVT construction reproduces the regularized filter to
  `< 1e-9`, and the regularized inverse converges to `numpy.linalg.pinv` as `eps -> 0`
  (condition-number-limited, exactly like the QSVT matrix inverse — documented).
- **Real matrix exponential** (`algorithms.matrix_exp_qsvt`) — `exp(A)`, the imaginary-time
  sibling of `e^{-iHt}`; machine-precision against `scipy.linalg.expm`.
- **Matrix logarithm** (`algorithms.matrix_log_qsvt`) — `log(A)` of a positive-definite
  `A`; verified against `scipy.linalg.logm`.
- **Gibbs (thermal) states** (`algorithms.gibbs_state_qsvt`) — `rho = e^{-beta H}/Z` built
  from the QSVT Chebyshev series and trace-normalized; verified against the exact Gibbs
  state, reducing to the maximally mixed state at `beta = 0`.
- **Ground-state projection & filtering** (`algorithms.ground_state_projector_qsvt`) — the
  low-energy spectral filter that projects onto the ground space; applied to (almost) any
  state it yields the ground state. Verified against the exact projector.
- **Gaussian spectral bandpass filter** (`algorithms.bandpass_filter_qsvt`) — a smooth
  window `exp(-((A-center)/width)^2)` keeping the eigenspaces near `center` — eigenstate
  filtering / windowed phase estimation; verified against the exact windowed spectrum.
- **Chebyshev spectral moments** (`algorithms.spectral_moments`) — `mu_k = Tr T_k(A) =
  sum_i T_k(lambda_i)`, the raw data of the Kernel Polynomial Method, each `T_k(A)` from
  the qubitization walk; machine-precision against the spectrum.
- **Trace of a matrix function** (`algorithms.trace_of_function`) — `Tr f(A) = sum_k c_k
  mu_k` from the Chebyshev moments, never forming `f(A)` densely; verified against
  `sum_i f(lambda_i)`.
- **Thermal partition function** (`algorithms.partition_function_qsvt`) — `Z = Tr e^{-beta
  H} = sum_i e^{-beta lambda_i}` from the moments; verified against the exact spectral sum.
- **Density of states (Kernel Polynomial Method)** (`algorithms.density_of_states_kpm`) —
  the spectral density expanded in Jackson-damped Chebyshev moments; verified to integrate
  to the dimension and to peak at the true eigenvalues.
- **Eigenvalue counting in an interval** (`algorithms.eigenvalue_count_in_interval`) — the
  number of eigenvalues in `(a,b)` as the trace of a smoothed spectral window; rounds to
  the exact integer count without diagonalizing.
- **Amplitude amplification as scalar QSVT** (`algorithms.amplitude_amplification_qsvt`) —
  the amplitude `sin((2k+1)theta)` after `k` Grover steps (an odd Chebyshev polynomial of
  the initial amplitude) plus the optimal step count; verified to machine precision against
  an explicit two-dimensional reflection simulation.
- **Chebyshev (near-minimax) approximation** (`algorithms.chebyshev_approximation`) — the
  classical polynomial a QSP phase sequence realizes and QSVT applies to a matrix, with its
  max-norm error; verified to converge geometrically for analytic functions.
- **QSP completion identity** (`algorithms.qsp_complementary_response`) — the achievable
  polynomial `P` and its complement `Q` with `|P(x)|^2 + (1-x^2)|Q(x)|^2 = 1`, the
  algebraic condition deciding which polynomials a phase sequence can realize; verified to
  machine precision.
- **Quantum linear systems via QSVT** (`algorithms.matrix_inverse_qsvt`,
  `solve_linear_system_qsvt`) — the other headline QSVT application: approximate
  `A^{-1}` by fitting `1/x` over the spectral support and building the Chebyshev series
  from the qubitization walk, then solve `Ax = b` — the QSVT form of the quantum
  linear-systems (HHL) problem. Verified against `numpy.linalg.solve`: the inverse
  converges to `< 1e-6` (improving with degree), `A^{-1}·A = I`, the solution matches
  to `< 1e-5` with residual `||Ax-b||` tiny and fidelity ~1. (The `1/x` fit is
  ill-conditioned, so the degree must scale with the condition number — documented.)
- **Matrix functions & Hamiltonian simulation via QSVT**
  (`algorithms.matrix_function_chebyshev`, `hamiltonian_simulation_qsvt`,
  `chebyshev_coefficients`) — the payoff of the QSVT machinery: approximate any smooth
  `f(A)` by the Chebyshev series `sum_k c_k T_k(A)`, with each `T_k(A)` built from the
  qubitization walk. Verified to converge to the exact matrix function (< 1e-8 by
  degree 20 for cos/sin/exp, geometric convergence for a Gaussian, `f(x)=x` giving `A`
  exactly). As the flagship application, `hamiltonian_simulation_qsvt` builds
  `e^{-iHt}` from the expansion of `e^{-ixt}` — matching exact diagonalization to
  < 1e-6, staying unitary, reducing to the identity at `t=0`, and needing higher
  degree for longer times, exactly as the theory predicts.
- **Quantum Singular Value Transformation (QSVT)** (`algorithms.qsvt_transform`,
  `qsvt_scalar_response`) — the capstone unifying QSP and block encoding: apply a QSP
  phase sequence to the qubitization walk of a Hermitian `A` and obtain the matrix
  function `P(A) = sum_i g(lambda_i)|v_i><v_i|` in the top-left block. Verified to
  machine precision that the matrix transform equals the scalar QSVT response applied
  *eigenvalue-by-eigenvalue* (the QSVT theorem itself) across random phase sequences,
  that zero phases reproduce the Chebyshev `T_d(A)`, that the output commutes with `A`
  (it is a genuine function of `A`), and the scalar response stays bounded by 1 — the
  framework that unifies amplitude amplification, Hamiltonian simulation, and quantum
  linear algebra.
- **Linear Combination of Unitaries (LCU)** (`algorithms.lcu_block_encoding`,
  `lcu_matrix`) — block-encode a weighted sum `H = sum alpha_i U_i` from its PREPARE
  (amplitude-loading) and SELECT (controlled-unitary) pieces:
  `PREPARE† SELECT PREPARE` has top-left block `H / lambda` with `lambda = sum alpha_i`.
  Verified the encoding is unitary and its block equals `H/lambda` exactly for Pauli
  sums, multi-qubit operators, and non-power-of-two term counts (ancilla padded with
  identity); the subnormalization equals the coefficient sum, a single term encodes
  its unitary directly, and negative coefficients are rejected — the standard way to
  feed a Hamiltonian into qubitization/QSVT.
- **Block encoding & qubitization** (`algorithms.block_encode`, `is_block_encoding`,
  `qubitization_walk`, `chebyshev_of_matrix`) — the input model of QSVT: hide a
  Hermitian matrix `A` (`||A|| <= 1`) in the corner of a unitary
  (`<0|U|0> = A`, verified unitary with the exact top-left block), then form the
  qubitization walk `W = U(2Π-I)` and realize the Chebyshev polynomials of the
  *matrix*: `<0|W^d|0> = T_d(A)`. Verified against the classical matrix function
  `sum_i T_d(lambda_i)|v_i><v_i|` for degrees 1–6 (with `T_1(A)=A`, `T_2(A)=2A^2-I`,
  and the diagonal case exact) — the quantum-walk route to matrix functions.
- **Quantum Signal Processing** (`algorithms.qsp_unitary`, `qsp_response`,
  `chebyshev_via_qsp`, `signal_operator`) — the one-qubit engine of modern quantum
  algorithms: interleave a signal rotation `W(x)` with tunable `Z` rotations set by a
  phase sequence, and `<0|U(x)|0>` becomes a designable degree-`d` polynomial `P(x)`.
  Verified: zero phases reproduce the Chebyshev polynomials `T_d` exactly (matching
  `cos(d·arccos x)` and `2x^2-1` for `T_2`), a degree-`d` sequence yields a polynomial
  of the correct parity (`d mod 2`) bounded by 1, and the QSP operator is unitary at
  every signal value — the foundation the QSVT features build on.

## [1.0.0]

Theme: scale & tensor networks — breaking the exponential state-vector wall. The
headline is a full **matrix product state** engine (`quantum_debugger.mps.MPS`):
construction from a state vector or a `QuantumCircuit`, exact single-qubit and
SVD-truncated two-qubit gates (nearest-neighbour and long-range via SWAP networks),
and a complete `O(n·chi^2)` readout toolkit — expectation values, arbitrary
Pauli-string and Pauli-sum-Hamiltonian energies, correlations, entanglement entropy
across every bond, overlap/fidelity between states, and exact Born-rule sampling —
none of which ever forms the dense state. On top of it, TEBD gives real-time dynamics
and imaginary-time DMRG-style ground states. Every MPS operation is verified against
the state-vector simulator; the engine scales to 100-qubit GHZ states, 40-qubit
quenches, and 24-qubit ground states — moving the library from "≤25 qubits exactly"
to "hundreds of qubits when entanglement allows." (The major-version bump the
tensor-network capability earns.)

### Added
- **MPS two-site expectation** (`MPS.two_site_expectation`) — the expectation of any
  two-qubit operator (4x4) via the two-qubit reduced density matrix `Tr(O rho_ab)`,
  matching the dense value and `<ZZ>` correlations — the primitive for bond energies.
- **MPS truncation error & normalization** (`MPS.truncation_error`, `MPS.normalize`) —
  the weight lost when compressing to a target bond dimension (`1 - fidelity`, exactly
  0 for a GHZ at bond ≥ 2, decreasing as the bond grows) and in-place unit
  normalization — the diagnostics that make bond-dimension choices principled.
- **MPS two-qubit correlations** (`MPS.two_qubit_rdm`, `MPS.mutual_information`,
  `MPS.concurrence`) — the reduced density matrix of any qubit pair assembled from
  their 16 two-qubit Pauli expectations (scalable, matching the dense partial trace),
  and the pairwise mutual information and Wootters concurrence from it (a Bell pair
  giving 2 bits and concurrence 1, a product pair giving 0).
- **MPS amplitudes & basis states** (`MPS.amplitude`, `MPS.probability`,
  `MPS.from_bitstring`, `MPS.most_probable`) — the amplitude `<bits|psi>` of any
  computational-basis string by contracting fixed-bit tensor slices (`O(n·chi^2)`,
  matching the dense value, probabilities summing to 1), a basis-state constructor,
  and the most-probable outcome from sampling (a GHZ returning `0000`/`1111` at
  probability 0.5).
- **Heisenberg MPO** (`mpo.heisenberg_mpo`) — the bond-dimension-5 matrix product
  operator for `H = J sum (XX + YY + ZZ)`, verified to contract to the exact dense
  Heisenberg Hamiltonian.
- **MPS Bloch vectors & purity profile** (`MPS.bloch_vector`, `MPS.purity_profile`) —
  each qubit's `(<X>,<Y>,<Z>)` and its purity `Tr(rho_i^2)` (a GHZ giving zero Bloch
  vectors and 0.5 purity everywhere, a product state giving unit purity) — a local
  read of how entangled each site is.
- **MPS structure factor & magnetization** (`MPS.structure_factor`,
  `MPS.total_magnetization`, `MPS.schmidt_gap`) — the static structure factor
  `S(k) = (1/n) sum e^{ik(i-j)} <O_i O_j>` (verified against the dense computation and
  peaking at `S(0)=n` for a ferromagnet), the summed magnetization, and the
  entanglement-spectrum Schmidt gap (an order parameter that closes at a transition).
- **Apply an MPO to an MPS** (`MPS.apply_mpo`, `MPS.expectation_mpo`) — compute
  `H|psi>` by contracting a matrix product operator into the state (bond dimensions
  multiply, optionally recompressed), verified to match the dense `H·psi`; plus a
  convenience `expectation_mpo` matching `MPS.energy`.
- **MPS reduced density matrix & entanglement spectrum** (`MPS.single_qubit_rdm`,
  `MPS.entanglement_spectrum`) — a qubit's reduced density matrix from its Pauli
  expectations (scalable, matching the dense partial trace) and the full Schmidt
  spectrum across any bond (a Bell cut giving `[0.707, 0.707]`, squares summing to 1).
- **Matrix Product Operators** (`quantum_debugger.mpo`: `tfim_mpo`, `mpo_expectation`,
  `mpo_to_matrix`) — the operator analogue of an MPS: a Hamiltonian as a chain of
  rank-4 tensors (the TFIM needs only bond dimension 3), so `<psi|H|psi>` on a large
  MPS costs `O(n·chi^2·D^2)` with no dense operator. Verified: the MPO contracts to the
  exact dense TFIM Hamiltonian, its expectation matches both the dense and the
  `MPS.energy` value, and a 30-qubit GHZ gives the exact `-J(n-1)`.
- **MPS construction helpers** (`MPS.from_product`, `MPS.random`) — build a product
  state from per-qubit amplitudes (bond dimension 1) or a reproducible random MPS at a
  target bond dimension; verified normalized with the expected structure.
- **MPS linear algebra** (`MPS.add`, `MPS.compress`) — sum two MPS by the
  direct-sum-of-bonds construction (matching the dense `(a+b)`), and recompress to a
  smaller bond dimension (a GHZ compresses to bond 2 losslessly, fidelity 1).
- **MPS magnetization & correlation profiles** (`MPS.magnetization_profile`,
  `MPS.correlation_profile`) — `<O_i>` on every site and the spatial correlation
  function `<O_a(ref) O_b(j)>` by contraction; a GHZ gives zero magnetization and unit
  correlation across the chain.
- **MPS energy variance** (`MPS.variance`) — `<H^2> - <H>^2` of a Pauli-sum
  Hamiltonian, exactly 0 on an eigenstate and positive off it — the convergence check
  for tensor-network ground-state methods.
- **MPS Renyi entanglement entropy** (`MPS.renyi_entropy`) — Renyi-`alpha` entropy
  across any bond from the canonicalized Schmidt spectrum (`alpha=1` recovers von
  Neumann, `alpha=2` the collision entropy), verified non-increasing in `alpha`.
- **MPS Hamiltonian energy** (`MPS.energy`) — evaluate `<psi|H|psi>` for any
  Hamiltonian given as `(coefficient, pauli_string)` terms (the `pauli_decompose` /
  VQE format) on a matrix product state, summing Pauli-string expectations by
  contraction. Verified against dense for TFIM and a Pauli-decomposed Fermi-Hubbard
  Hamiltonian, and a GHZ gives the exact `-J(n-1)` — connecting the chemistry/spin
  Hamiltonians of 0.9 to the large-scale MPS engine.
- **MPS Pauli-string expectation** (`MPS.expectation_pauli`) — the expectation of any
  multi-qubit Pauli observable `<psi|P|psi>` on a matrix product state by
  `O(n·chi^3)` contraction. Verified against the dense value for all 256 Pauli strings
  on 4 qubits, and a 20-qubit GHZ correctly returns `<X^20> = 1` (its stabilizer) —
  measuring arbitrary observables on systems too large to store densely.
- **Circuit → MPS runner** (`MPS.from_circuit`) — run an existing `QuantumCircuit` on
  the tensor-network engine: single-qubit gates applied exactly, two-qubit gates via
  the long-range SWAP path (either control/target ordering handled by re-indexing the
  4x4 matrix), three-plus-qubit gates rejected with a clear message to decompose first.
  Verified to reproduce the state-vector result exactly on mixed random circuits and
  reversed-control CNOTs, with a GHZ circuit staying at bond dimension 2. (Note: the
  scale ceiling here is the `QuantumCircuit` object itself, which allocates a dense
  state; to exceed it, drive the `MPS` directly.)
- **MPS long-range two-qubit gates** (`MPS.apply_two_long_range`) — apply a two-qubit
  gate to *any* pair of qubits (not just neighbours) via a nearest-neighbour SWAP
  ladder: swap the qubits together, apply the gate, swap back. Verified against the
  state-vector simulator for all pairs and asymmetric random unitaries, correctly
  delegating for adjacent qubits, and building a long-range Bell pair between qubits 0
  and 9 — so arbitrary-connectivity circuits run on the MPS engine.
- **MPS overlap & fidelity** (`MPS.overlap`, `MPS.fidelity`) — the inner product
  `<phi|psi>` of two matrix product states by the double-layer `O(n·chi^3)`
  contraction, and the state fidelity from it. Verified to match the dense inner
  product exactly, self-fidelity is 1 (including a 40-qubit GHZ), and orthogonal states
  give zero overlap — comparing tensor-network states without ever forming them
  densely.
- **MPS entanglement entropy** (`MPS.bond_entropies`, `MPS.entanglement_entropy`) —
  the entanglement entropy across every bond, read from the Schmidt spectrum by
  canonicalizing the network (right-to-left then left-to-right SVD sweeps), scaling to
  large `n` with no dense state. Verified to match the dense density-matrix
  entanglement entropy exactly at every cut; a product state gives 0, a GHZ exactly 1
  bit across every bond — including a 60-qubit GHZ whose full entropy profile is
  computed instantly.
- **MPS measurement sampling** (`MPS.sample`) — draw computational-basis shots from a
  matrix product state by exact sequential conditional sampling with precomputed right
  environments, `O(shots·n·chi^2)`, never forming the dense state. Verified: the
  empirical distribution matches the dense Born rule to within shot noise on random
  states, Bell/GHZ give only their correlated outcomes, a product state is
  deterministic, and shot counts are conserved — measurement statistics from systems
  far too large to store as a state vector.
- **Imaginary-time TEBD ground states** (`algorithms.imaginary_tebd_ground_state`,
  `tfim_mps_energy`) — DMRG-style ground-state search on the MPS: apply imaginary-time
  bond gates `e^{-h dtau}` (cooling), renormalize, and settle into the ground state.
  Verified against exact diagonalization (error < 5e-3 for n = 4/6/8, improving with
  finer steps), respects the variational lower bound, and finds the ground state of a
  **24-qubit** chain that no dense diagonalizer could reach — with the energy per site
  extensive across sizes. `tfim_mps_energy` reads the TFIM energy off any MPS by
  contraction, matching the dense value exactly.
- **TEBD time evolution** (`algorithms.tebd_tfim`, `tebd_magnetization`,
  `tfim_bond_gate`) — real-time many-body dynamics on the MPS: Trotterize
  `e^{-iHt}` into two-site gates, apply them even-then-odd, and let the SVD truncation
  bound the bond dimension. Verified to match exact state-vector evolution to fidelity
  > 0.9999 on small TFIM chains (finer Trotter steps improving it), runs a 30-qubit
  quench beyond the dense simulator's reach, keeps the bond capped at `max_bond`, and
  reproduces the physics — a vanishing field freezes the magnetization (`|0...0>` is an
  eigenstate) while a transverse field tilts the spins.
- **Matrix Product State simulator** (`quantum_debugger.mps.MPS`) — the 1.0 flagship:
  a tensor-network engine that breaks the exponential state-vector wall for
  low-entanglement states. Represents an n-qubit state as a chain of rank-3 tensors
  with bond dimension `chi` (`O(n·chi^2)` memory instead of `2^n`), applies
  single-qubit gates exactly and neighbouring two-qubit gates by SVD with truncation
  to `max_bond` (the DMRG/TEBD approximation), and computes norms, expectation values,
  and two-point correlations by `O(n·chi^3)` contraction — never forming the dense
  state. Verified: exact state-vector roundtrip, single- and two-qubit gates
  (including asymmetric random unitaries) match the state-vector simulator to 1e-10,
  bond dimensions correctly detect structure (product → 1, GHZ → 2), and a **100-qubit
  GHZ** builds instantly at bond dimension 2 with correct `<Z0 Z99> = 1`, `<X0> = 0` —
  a `2^100`-amplitude state held in a handful of small tensors.

## [0.9.0]

Theme: quantum chemistry, many-body physics & advanced simulation. Fermionic systems
(Jordan-Wigner, Fermi-Hubbard, the Kitaev topological chain), ground- and
excited-state solvers (chemistry-via-VQE with Pauli decomposition, imaginary-time
cooling, Krylov/Lanczos, adiabatic evolution), finite-temperature physics (Gibbs
states & thermodynamics), quantum dynamics (Trotter error scaling, Loschmidt echo &
DQPTs, out-of-time-order correlators, entanglement growth), quantum chaos (level-
spacing statistics), metrology (spin squeezing, mixed-state QFI), and the modern
measurement/tensor-network toolkit (classical shadows, Schmidt decomposition & the
area law). Every routine verified against a closed form or an independent
computation. (Open systems, noise, and fault tolerance landed in 0.8.0.)

### Added
- **SSH topological insulator** (`algorithms.ssh_hamiltonian`) — the Su-Schrieffer-Heeger
  chain with alternating hoppings `v, w`, the textbook 1D topological insulator; the
  single-particle Hamiltonian is exactly diagonalized and verified to have a
  chiral-symmetric spectrum.
- **SSH winding number** (`algorithms.ssh_winding_number`) — the bulk `Z` invariant of the
  chiral class BDI: `1` (topological) when `|w| > |v|`, `0` (trivial) otherwise.
- **SSH edge modes** (`algorithms.ssh_zero_modes`, `ssh_edge_polarization`) — the
  bulk-boundary correspondence made concrete: `2` protected zero-energy modes localized on
  the ends in the topological phase, `0` in the trivial phase, verified against the exact
  spectrum and eigenvectors.
- **Ground-state fidelity** (`algorithms.ground_state_fidelity`) — the overlap
  `|<psi(lambda)|psi(lambda+dlambda)>|` between neighbouring ground states, near 1 inside a
  phase and dipping sharply at a quantum phase transition.
- **Fidelity susceptibility** (`algorithms.fidelity_susceptibility`, `tfim_critical_field`)
  — the intensive response `chi_F = 2(1-F)/dlambda^2` that peaks at a critical point;
  verified to locate the transverse-field Ising transition, its finite-size peak drifting
  toward the exact `h_c = 1` as the system grows.
- **Connected correlation functions** (`algorithms.connected_correlation`) —
  `<O_i O_j> - <O_i><O_j>`, the probe of correlations beyond mean field; verified `1` on a
  GHZ state and `0` on a product state.
- **Correlation length** (`algorithms.correlation_length`) — `xi` from the exponential
  decay of the connected correlator; verified `0` for a product state and growing toward
  criticality for the TFIM ground state.
- **Static structure factor** (`algorithms.structure_factor`) — `S(k)` from the spatial
  correlations, the Fourier probe of order; verified to Bragg-peak at `k=0` for a
  ferromagnet and `k=pi` for an antiferromagnet.
- **Entanglement negativity** (`algorithms.negativity`, `logarithmic_negativity`) — the
  computable mixed-state entanglement measure from the partial transpose; verified
  `E_N = 1` for a Bell pair, `0` for a product state.
- **Peres-Horodecki (PPT) criterion** (`algorithms.partial_transpose`, `is_entangled_ppt`)
  — the partial transpose and its negative-eigenvalue entanglement witness; verified to
  reproduce the Werner-state entanglement threshold `p > 1/3`.
- **Schmidt decomposition & the area law** (`algorithms.schmidt_decomposition`,
  `truncation_fidelity`, `area_law_compressibility`) — the tensor-network bridge:
  write any bipartite pure state as `sum lambda_i |i>_A|i>_B` via SVD. Verified that a
  Bell pair gives two equal Schmidt values (1 bit), a product state rank 1, the values
  are normalized and descending, and the Schmidt entropy matches the density-matrix
  entanglement entropy exactly. The headline result: a gapped 1D ground state (TFIM)
  keeps > 99% of its weight in a handful of Schmidt values (area law → compressible to
  a low-bond-dimension MPS), while a random volume-law state has a flat spectrum that
  refuses to compress — exactly why matrix product states work.
- **Classical shadows** (`algorithms.collect_shadows`, `estimate_observable`,
  `shadow_estimates`) — estimate many observables from few measurements
  (Huang-Kueng-Preskill): measure each qubit in a random Pauli basis, build the
  unbiased single-shot snapshot `prod_q (3|b_q><b_q| - I)`, and read off `<O> =
  Tr(O rho_hat)` for *any* observable from the *same* dataset. Verified: Bell-pair
  correlators (`<XX>=1`, `<YY>=-1`, `<ZZ>=1`, `<ZI>=0`) all recovered from one
  collection, the error shrinks with shot count, `<I...I>=1` exactly per snapshot, and
  a shadow set is reusable across observables — the cost set by observable locality,
  not Hilbert-space dimension.
- **Spin squeezing (one-axis twisting)** (`algorithms.one_axis_twisting`,
  `best_squeezing`) — metrologically useful entanglement that beats the standard
  quantum limit. Evolving a coherent spin state under `H = chi J_z^2` (Kitagawa-Ueda)
  redistributes the transverse noise; the Wineland parameter `xi^2 = N min Var(J_perp)
  / |<J>|^2` (minimum variance computed in closed form from the 2x2 covariance matrix)
  drops below 1. Verified: `xi^2 = 1` exactly at zero twisting (the SQL), squeezing
  reaches -2.9 to -4.5 dB, improves with atom number, and `1/xi^2` gives the
  phase-sensitivity gain — the interferometric payoff of the entanglement.
- **Kitaev chain (topological superconductor)** (`algorithms.kitaev_chain_hamiltonian`,
  `kitaev_ground_degeneracy`) — the simplest model with Majorana edge modes, built on
  the Jordan-Wigner operators: `-mu sum n_j - t sum hopping + Delta sum pairing`.
  Verified the topological hallmarks — for `|mu| < 2t` the ground state is doubly
  degenerate (splitting < 1e-9 at `mu = 0`) with the bulk gap staying open, while for
  `|mu| > 2t` it is unique and gapped; the topological flag flips exactly at the
  `|mu| = 2t` transition; fermion parity is conserved; and the ground-state splitting
  decays *exponentially* with chain length (halving per site) — the localization of
  the two Majorana modes at the chain ends, the nonlocal storage behind topological
  qubits.
- **Level-spacing statistics (quantum chaos)** (`algorithms.level_spacing_ratio`,
  `goe_reference`, `poisson_reference`, `classify_spectrum`) — the symmetry-free
  Oganesyan-Huse gap-ratio `<r>` that distinguishes integrable from chaotic spectra
  without unfolding. Validated against both defining ensembles: Gaussian Orthogonal
  Ensemble spectra give `<r> ~ 0.531` (Wigner-Dyson level repulsion) and uncorrelated
  Poisson spectra give `~ 0.386`, with a rigid equally-spaced spectrum giving exactly
  1. `classify_spectrum` labels a spectrum against these universal values.
  Honestly documented: physical Hamiltonians only show the clean values within a
  single symmetry sector (mixed sectors bias toward Poisson).
- **Entanglement growth after a quench** (`algorithms.entanglement_growth`) — how
  isolated systems thermalize: start in a product state, evolve under an entangling
  Hamiltonian, and watch a subregion's entanglement entropy grow and saturate near
  the volume-law value. Verified against the analytic two-qubit case (an `X x X`
  quench of `|00>` gives exactly the binary entropy `h(sin^2(gt))`, reaching 1 bit at
  a quarter period), and for larger TFIM/Heisenberg quenches the entropy starts at 0,
  grows, saturates below its `min(|A|, n-|A|)` bound, and stays static for an energy
  eigenstate.
- **Out-of-time-order correlators (scrambling)** (`algorithms.otoc`,
  `scrambling_time`) — the butterfly effect of quantum chaos: the growth of
  `C(t) = <|[W(t), V]|^2>` as a local operator spreads across the lattice. Verified
  the exact structure — `C(0) = 0` for spatially-separated operators (they commute),
  `C(0) = 4` for anticommuting same-site operators, `C(t) >= 0` always, and the exact
  identity `C(t) = 2(1 - Re F(t))` with the OTOC `F(0) = 1`. `scrambling_time` tracks
  a perturbation from one edge to the other and finds when it arrives — the far qubit
  lagging the near one, the operator light cone made quantitative.
- **Loschmidt echo & dynamical quantum phase transitions**
  (`algorithms.loschmidt_echo`, `rate_function`, `quench_dynamics`) — quench a state
  under a Hamiltonian and track `L(t) = |<psi_0|e^{-iHt}|psi_0>|^2` and its rate
  function `-ln L / N`, whose non-analytic cusps mark DQPTs. Verified: an eigenstate
  never dephases (`L = 1`), a two-level superposition reproduces the analytic
  `1 - sin^2(2θ) sin^2(Δt/2)` exactly, the rate function peaks precisely where the
  echo dips, and at `θ = π/4` the echo hits zero — a genuine dynamical phase
  transition where the evolved state becomes orthogonal to the start.
- **Krylov subspace diagonalization (Lanczos)** (`algorithms.krylov_spectrum`,
  `krylov_ground_energy`) — build a small subspace `span{|psi>, H|psi>, ...,
  H^{m-1}|psi>}` and diagonalize `H` inside it. The Ritz values converge to the exact
  extreme eigenvalues — ground energy to machine precision by `m = 8` on TFIM
  (Fermi-Hubbard, Heisenberg too), and, unlike imaginary-time evolution, the lowest
  Ritz values recover the low-lying *excited* states as well. Solved through a
  thresholded generalized eigenproblem for stability against the near-parallel Krylov
  vectors; Ritz values are provably bracketed by the exact spectrum.
- **Adiabatic quantum computation** (`algorithms.adiabatic_evolution`) — the
  alternative computing paradigm: start in the easy ground state of a driver
  Hamiltonian and slowly interpolate `H(s) = (1-s)H_i + s H_f` to the problem
  Hamiltonian, ending in *its* ground state. Verified across both regimes of the
  adiabatic theorem: a slow sweep (T=50) reaches the target ground state at fidelity
  > 0.99, a fast one (T=0.5) is left excited at < 0.5 (diabatic transition), fidelity
  is monotone in the total time, and the minimum spectral gap along the path is
  tracked — the quantity that sets how slow "slow enough" must be.
- **Trotter error scaling** (`algorithms.trotter_unitary`,
  `trotter_error_scaling`) — assemble the full Trotterized evolution operator and
  measure how its error `|| U_trotter - exp(-iHt) ||` shrinks with the step count.
  Verified against the theoretical rates: the first-order formula converges as
  `~ t^2/n` (measured log-log slope -1.03) and the symmetric second-order Suzuki
  formula as `~ t^3/n^2` (slope -2.02) on TFIM and Heisenberg Hamiltonians, with
  second order strictly beating first at fixed step count — quantifying the accuracy
  of Hamiltonian-simulation circuits.
- **Imaginary-time evolution** (`algorithms.imaginary_time_evolution`) — cool any
  state to a Hamiltonian's ground state via normalized `e^{-tau H}`, the engine
  behind QITE and projector Monte Carlo — no optimizer, no local minima. Verified to
  converge to the exact ground energy (Fermi-Hubbard, TFIM, Heisenberg) with the
  energy decreasing monotonically and the converged state a true ground eigenstate.
  Honestly bounded: because the ground component decays slowest, even a start made
  orthogonal to the ground state still cools *to* it (its ~1e-16 residual overlap is
  re-amplified) — so plain ITE targets the ground state, never an excited level.
- **Gibbs states & quantum thermodynamics** (`algorithms.gibbs_state`,
  `partition_function`, `thermal_properties`) — finite-temperature physics of any
  Hamiltonian: `rho(beta) = e^{-beta H}/Z` and its thermodynamic potentials. Verified
  the full set of identities — `beta -> 0` gives the maximally mixed `I/d` (entropy
  `ln d`), `beta -> infinity` projects onto the ground state (entropy 0), the
  Helmholtz free energy satisfies `F = -ln Z / beta = E - S/beta` exactly, entropy is
  monotone in temperature, heat capacity is non-negative, and a single spin
  reproduces the analytic `<H> = -tanh(beta)`, `Z = 2 cosh(beta)`. Applied to the
  Fermi-Hubbard Hamiltonian, this gives its thermal state directly.
- **Pauli decomposition + chemistry-via-VQE**
  (`algorithms.pauli_decompose`) — decompose any Hermitian matrix into weighted
  Pauli strings (`c_P = Tr(P H)/2^n`), the step that turns a dense molecular or
  Fermi-Hubbard Hamiltonian into something a gate-based algorithm can run. Verified
  to round-trip random Hermitian operators exactly and to preserve the full
  spectrum; feeding the decomposed Fermi-Hubbard dimer (and a hopping chain) to the
  existing VQE solver recovers the exact ground energy to ~1e-11 — the complete
  fermion → qubit → variational-ground-state pipeline.
- **Fermi-Hubbard model** (`algorithms.fermi_hubbard_hamiltonian`,
  `hubbard_ground_energy`, `hubbard_dimer_energy`) — interacting electrons on a
  lattice, built on the Jordan-Wigner operators: hopping `t` vs on-site repulsion
  `U`, two spin-orbitals per site. Verified: the Hamiltonian conserves total and
  per-spin particle number, and the exactly-solvable half-filled two-site dimer
  reproduces the analytic ground energy `(U - sqrt(U^2 + 16t^2))/2` at every `U`,
  interpolating from the non-interacting `-2t` (`U = 0`) to the Heisenberg
  antiferromagnet `-4t^2/U` (large `U`) — the Mott physics in miniature.
- **Jordan-Wigner transformation** (`algorithms.jw_annihilation`, `jw_creation`,
  `jw_number`, `jw_total_number`, `hopping_hamiltonian`, `anticommutation_error`) —
  the bridge from fermions to qubits that makes quantum chemistry simulable. Mode
  `j` maps to `(prod_{k<j} Z_k) sigma_j^-`; verified that the operators satisfy the
  fermionic algebra `{a_i, a_j} = 0`, `{a_i, a_j^dagger} = delta_ij` exactly, that
  number operators are {0,1} projectors, that `(a^dagger)^2 = 0` (Pauli exclusion),
  and that the tight-binding hopping Hamiltonian reproduces the exact band
  `-2t cos(k)` (open chain and ring) while conserving particle number.

## [0.8.0]

Theme: a comprehensive quantum-information-theory layer on the two simulation
engines — open systems & noise (Lindblad, channel metrics, Stinespring dilation,
process tomography), fault tolerance & QEC ([[5,1,3]], Steane [[7,1,3]] with
transversal gates, [[4,2,2]], magic-state injection, Petz recovery), quantum
networking (BBPSSW/DEJMPS distillation, noisy swapping, repeater chains),
noise-protection without QEC (DFS, spin echo, Zeno), and foundational measures
(negativity, concurrence, discord, mutual information, Horodecki nonlocality,
contextuality, geometric phase, uncertainty relations, weak values, Holevo,
channel capacity, state discrimination, no-cloning, magic, MBQC). Every routine
verified against a closed form or an independent computation.

### Added
- **Petz recovery map (approximate QEC)** (`algorithms.petz_recovery`,
  `petz_code_recovery`) — the canonical "best-effort" recovery for noise that has no
  perfect correction: `R_sigma(rho) = sigma^{1/2} N^dagger(N(sigma)^{-1/2} rho
  N(sigma)^{-1/2}) sigma^{1/2}`. Verified on three fronts: it recovers *correctable*
  errors perfectly (bit-flip errors on the 3-qubit code, fidelity 1.0 from 0.75 —
  reproducing the syndrome decoder); it gives genuine *approximate* recovery for
  uncorrectable amplitude damping (0.82 → 0.93, degrading with damping strength);
  and it satisfies the defining identity `R_sigma(N(sigma)) = sigma` exactly while
  preserving trace.
- **Weak values (Aharonov-Albert-Vaidman)** (`algorithms.weak_value`,
  `weak_measurement_shift`, `weak_value_demo`) — pre- and post-selection let a
  weakly-measured observable read `A_w = <phi|A|psi>/<phi|psi>`, which can sit far
  outside its spectrum or be complex. Verified both ways: `A_w` reduces to the
  eigenvalue/expectation in the appropriate limits, reaches ~ -20 for an observable
  with eigenvalues +/-1 under near-orthogonal selection (the amplification effect),
  and — running the actual pointer-qubit weak measurement `exp(-i g A x Y/2)` — the
  post-selected pointer's `<X>/g` shift converges to `Re(A_w)` in the weak-coupling
  limit.
- **Quantum process tomography** (`density_matrix.process_tomography`) —
  reconstruct an unknown single-qubit channel's full Choi matrix from its
  input/output behavior alone: probe the black box on the four
  informationally-complete states `|0>, |1>, |+>, |+i>`, recover the off-diagonal
  image by linear combination, and assemble `J = sum_ij |i><j| x N(|i><j|)`.
  Verified to recover the exact `choi_matrix` for every standard channel and for
  unitary channels, with the reconstruction certified CPTP (positive Choi, partial
  trace = I). A channel is fully characterized by how it acts, not how it is built.
- **Stabilizer entanglement entropy from the tableau**
  (`StabilizerSimulator.entanglement_entropy`) — the entropy across any cut of a
  stabilizer state in `O(n^3)` directly from the binary tableau (Fattal et al.:
  `S_A = rank_GF2(G_B) - |B|`), no `2^n` state vector — so it works on the hundreds
  of qubits the Clifford engine reaches (verified on a 200-qubit GHZ cut, instant).
  Matches the dense density-matrix entanglement entropy exactly on random Clifford
  states across many cuts; always an integer number of bits; 1 bit for Bell/GHZ
  cuts, 0 for product cuts.
- **Stinespring dilation** (`density_matrix.stinespring_isometry`,
  `apply_channel_dilated`) — the constructive proof that all noise is entanglement
  with an environment: any Kraus channel `N(rho) = sum_k K_k rho K_k^dagger` is
  realized as an isometry `V|psi> = sum_k K_k|psi>|k>_env` followed by discarding
  the environment. Verified that `Tr_env(V rho V^dagger)` reproduces every standard
  channel exactly, that `V^dagger V = I` (trace preservation), that a unitary
  channel dilates to itself (env dimension 1), and that the dilated global state is
  pure — the environment *purifies* the noise.
- **Measurement-based quantum computation** (`algorithms.mbqc_rotation`,
  `cluster_pair`) — the opposite of the circuit model: compute by *measuring* a
  fixed entangled resource. Measuring one qubit of a two-qubit cluster state in the
  `alpha`-tilted basis teleports `X^s H Rz(-alpha)|psi>` onto the ancilla — verified
  to fidelity 1 on 200+ random inputs against the exact byproduct law. Applying the
  outcome-conditioned `X^s` correction turns it into a *deterministic* gate
  `H Rz(-alpha)` (exactly `H` at `alpha = 0`), a genuine unitary enacted purely by
  measurement, with the outcome unbiased and both branches occurring.
- **[[4,2,2]] error-detecting code** (`algorithms.four_two_two_codewords`,
  `detect_single_errors`, `postselected_memory`) — the smallest useful stabilizer
  code: 4 qubits, 2 logical qubits, distance 2, stabilizers `XXXX`/`ZZZZ`.
  Verified: orthonormal stabilized codewords, all 12 single-qubit Pauli errors
  anticommute with a stabilizer (detected), and detect-and-discard memory under
  depolarizing noise gives post-selected infidelity O(p^2) (ratio 4.02 on p
  doubling, 330x below a bare qubit at p = 0.002) at an O(p) rejection cost — the
  strategy behind many early fault-tolerance experiments.
- **Dense coding with a noisy resource** (`algorithms.dense_coding_capacity`) —
  superdense coding meets reality: encoding 2 bits by local Paulis on half a
  Werner pair gives an ensemble whose Holevo capacity (computed directly with
  `holevo_bound`) equals `2 - S(rho_W)` exactly at every fidelity. A perfect Bell
  pair delivers 2 bits, the maximally mixed resource exactly 0, capacity is
  monotone in F, and the *quantum advantage* (beating the 1 classical bit) is lost
  well before entanglement is — another resource-hierarchy gap, quantified.
- **Magic measures: stabilizer Renyi entropy**
  (`algorithms.stabilizer_renyi_entropy`, `magic_of_t_states`) — quantify the
  resource that takes computation beyond classically-simulable Clifford circuits:
  `M_2 = -log2(sum_P <P>^4 / d)` over all `4^n` Pauli strings (Leone et al., PRL
  128, 050402). Verified: exactly 0 on all six single-qubit stabilizer states,
  Bell, GHZ, and random Clifford-orbit states (via the stabilizer engine's
  `to_statevector`); exactly `log2(4/3)` on the T-magic state; invariant under H,
  S, and entangling CNOT (Clifford invariance); and exactly additive over parallel
  T states — connecting the magic-state injection arc to a measurable resource.
- **Mixed-state quantum Fisher information** (`algorithms.qfi_mixed`) — precision
  metrology for realistic (noisy) probes: the SLD spectral formula
  `F_Q = 2 sum (l_i-l_j)^2/(l_i+l_j) |<i|G|j>|^2`. Triple-verified: reduces to
  `4 Var(G)` on pure states, hits the Heisenberg limit `N^2` on a GHZ probe, and
  matches an *independent* numerical Bures-fidelity derivative
  (`8(1-sqrt(F))/dphi^2`) on random mixed states. Mixing monotonically destroys
  Fisher information, down to exactly 0 for the maximally mixed (phase-blind)
  state.
- **Uncertainty relations** (`algorithms.robertson_bound`,
  `entropic_uncertainty`) — Heisenberg made precise, twice. Robertson:
  `dA dB >= |<[A,B]>|/2`, verified on random observables/states and *tight* on a Z
  eigenstate for (X, Y); its weakness — the bound degenerating to zero on an X
  eigenstate — is demonstrated too. Maassen-Uffink entropic form:
  `H(A) + H(B) >= -log2 max|<a_i|b_j>|^2` = exactly 1 bit for the mutually
  unbiased X/Z pair on ANY state, with equality precisely on the eigenstates —
  complementarity that never degenerates.
- **Geometric (Pancharatnam-Berry) phase** (`algorithms.berry_phase_triangle`,
  `pancharatnam_phase`, `bloch_spinor`, `solid_angle`) — the phase that depends
  only on the path: transporting a qubit around a geodesic Bloch triangle gives
  `gamma = arg(<n1|n2><n2|n3><n3|n1>) = Omega/2` (mod 2pi), verified against the
  solid angle computed *independently* by classical spherical trigonometry
  (L'Huilier's excess) — exact agreement on 50/50 random triangles, the octant
  giving exactly `pi/4`. Gauge invariance (re-phasing any state changes nothing),
  orientation-oddness (reversing the loop flips the sign), and the degenerate-loop
  zero are all confirmed. The working principle of holonomic quantum gates.
- **Quantum contextuality: the Peres-Mermin magic square**
  (`algorithms.mermin_peres_square`, `classical_assignment_maximum`,
  `quantum_context_measurement`) — a complete 2-qubit Kochen-Specker proof. The 3x3
  grid of two-qubit Paulis is verified operator-by-operator (every row/column
  mutually commutes; row products `+I,+I,+I`, column products `+I,+I,-I`);
  brute-forcing all 512 non-contextual value assignments shows at most **5 of 6**
  constraints can ever hold classically; yet sequential projective measurement of
  any context on ANY state gives outcomes whose product equals the context's sign
  deterministically — all 6 constraints at once, on 120 randomized context
  measurements, with the individual outcomes still random. Measurement outcomes
  cannot be pre-existing context-independent values.
- **Optimal universal quantum cloning (Buzek-Hillery)**
  (`algorithms.universal_clone`) — no-cloning made quantitative: the exact 1 -> 2
  cloning machine (a verified 8x2 isometry with two clones + ancilla) copies ANY
  unknown qubit with fidelity exactly 5/6 — the proven optimum — for every input
  state (universality confirmed on random states to 1e-12), with the two clones
  identical. Beats the best classical measure-and-prepare strategy (2/3) while
  respecting the no-cloning bound (< 1).
- **Logical qubit lifetime under repeated QEC cycles**
  (`algorithms.repeated_qec_cycles`) — the fault-tolerance payoff, exact: each
  (noise -> recovery) cycle of the 3-qubit bit-flip code acts on the code space as a
  *logical* bit-flip channel with `q = 3p^2 - 2p^3` (weight-2/3 errors decode to
  exactly `X_L`), so k cycles give `F_k = (1 + (1-2q)^k)/2` — matched by the
  simulation to machine precision at every cycle. The encoded qubit outlives a bare
  one by `lifetime_gain ~ 1/(3p)` (33.9x at p = 0.01), the gain exceeds 1 for every
  `p < 1/2` with the fixed point exactly at threshold, and `|+_L>` never decays at
  all.
- **Quantum state discrimination** (`algorithms.helstrom_bound`,
  `helstrom_measurement`, `unambiguous_discrimination`) — the two optimal ways to
  tell non-orthogonal states apart. Helstrom minimum-error:
  `P_err = (1 - ||p0 rho0 - p1 rho1||_1)/2`, with the optimal measurement
  constructed explicitly (positive-eigenspace projector) and achieving the bound to
  machine precision, including mixed states and unequal priors
  (`(1-sqrt(1-4 p0 p1 s^2))/2` verified). Unambiguous (IDP): a 3-outcome POVM that
  is *never* wrong (error exactly 0), succeeding with exactly `1 - |<psi0|psi1>|`
  and paying the difference in inconclusive outcomes — strictly below the Helstrom
  success rate, the price of certainty.
- **Holevo bound & accessible information** (`algorithms.holevo_bound`,
  `accessible_information`, `holevo_gap`) — why a qubit carries at most one
  classical bit, and why non-orthogonal states can't even deliver that:
  `chi = S(avg) - sum p_i S(rho_i)` vs the best measurement's mutual information
  (optimized over the Bloch sphere). Verified against the exact two-pure-state
  closed forms `chi = h((1+cos t)/2)` and `I_acc = 1 - h((1+sin t)/2)` (Levitin),
  with a strictly positive gap for non-orthogonal states; the BB84 ensemble gives
  exactly `chi = 1` but accessible information exactly `1/2` — the eavesdropper's
  fundamental limit that makes QKD secure.
- **Channel coherent information & quantum capacity**
  (`algorithms.coherent_information`, `amplitude_damping_capacity`) — quantum
  Shannon theory from first principles: `I_c = S(N(rho)) - S(E)` computed by
  genuinely purifying the input, sending the system half through the channel, and
  reading the environment entropy off the joint output. Verified against the known
  amplitude-damping closed form `h((1-g)p) - h(gp)` at every tested `(g, p)`, the
  identity channel gives `I_c = S(rho)`, and the AD capacity behaves exactly as
  Shannon theory demands: 1 at `g = 0`, monotone decreasing, and **exactly zero
  from `g = 1/2`** — the antidegradable point where the environment learns as much
  as the receiver (with the exact antisymmetry `I_c(g) = -I_c(1-g)` confirmed).
- **Wootters concurrence & entanglement of formation**
  (`DensityMatrix.concurrence`, `entanglement_of_formation`) — the exact two-qubit
  entanglement measure for ANY mixed state: `C = max(0, l1-l2-l3-l4)` from the
  spin-flipped spectrum (computed in a Hermitian-similar form for eigvalsh
  precision), and `E = h((1+sqrt(1-C^2))/2)` — the cost in Bell pairs of preparing
  the state. Verified: pure states match `C = 2|ad-bc|` and EoF equals the
  entanglement entropy; Bell-diagonal states match `C = max(0, 2 max(lam) - 1)`;
  Werner states give `2F - 1` above the `F = 1/2` separability threshold and exactly
  0 below it.
- **CHSH nonlocality of mixed states — the Horodecki criterion**
  (`algorithms.chsh_maximum`, `chsh_maximum_optimized`, `correlation_matrix`,
  `werner_nonlocality`) — the exact maximal CHSH value of ANY two-qubit state:
  `S_max = 2 sqrt(u1 + u2)` from the correlation matrix `T`. Verified: matches
  brute-force optimization over all measurement angles on random mixed states, a
  Bell pair reaches Tsirelson's `2 sqrt(2)`, Werner states follow
  `2 sqrt(2)|4F-1|/3` with `S = 2` exactly at `F = (1+3/sqrt(2))/4 ≈ 0.7803` — and
  the **entangled-but-local window** `1/2 < F < 0.7803` is demonstrated: states
  whose entanglement is certified by negativity, yet no CHSH experiment on them can
  ever violate a Bell inequality. Entanglement and nonlocality are different
  resources.
- **Steane code under continuous depolarizing noise**
  (`algorithms.steane_code_noisy`) — the distance-3 promise demonstrated exactly on
  the 7-qubit density matrix: independent `depolarizing(p)` on every physical qubit,
  then the exact 64-syndrome CPTP recovery. Doubling `p` quadruples the logical
  error (measured ratio 3.98 — quadratic suppression, `1-F ~ O(p^2)` vs `O(p)`
  bare), the logical error at `p = 0.002` is 24x below the bare qubit's, the exact
  fidelity always exceeds the weight-1 floor `(1-p)^7 + 7p(1-p)^6`, and the
  pseudo-threshold is visible: encoding wins below `p ~ 0.05` and loses at 0.25.
- **T1/T2 relaxation times** (`density_matrix.relaxation_times`) — extract a qubit's
  datasheet numbers from exact Lindblad evolution (amplitude damping + pure
  dephasing) and verify the fundamental relation `1/T2 = 1/(2 T1) + 1/T_phi`, hence
  `T2 <= 2 T1` always, with equality iff there is no pure dephasing. Includes the
  dephasing-dominated regime (`T2 < T1`).
- **Quantum discord** (`density_matrix.quantum_discord`) — the quantum correlation
  that survives *without* entanglement: `D = S(B) - S(AB) + min_M sum p_k S(A|k)`,
  minimized over all projective measurements (grid-seeded Nelder-Mead). Verified: a
  Bell state carries exactly 1 bit, classical and product states exactly 0, pure
  states reduce to the entanglement entropy, random Bell-diagonal states match Luo's
  closed form (PRA 77, 042303) to 1e-5 — and a *separable* Werner state (negativity
  0) still has discord 0.049, quantum correlation with no entanglement at all.
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
