"""
Quantum Algorithms Library

Genuine, gate-based quantum algorithms on the state-vector simulator, each verified
against its known outcome. Includes:

  * Textbook algorithms -- QFT, Grover, Quantum Phase Estimation (+ iterative),
    Bernstein-Vazirani, Deutsch-Jozsa, quantum walk, quantum counting, amplitude
    estimation/amplification, HHL, swap test.
  * Shor's period finding & factoring; Simon's algorithm.
  * Quantum error correction (bit-flip, phase-flip, 9-qubit Shor code).
  * Hamiltonian simulation (Trotter-Suzuki) and a variational ground-state solver.
  * Gate decomposition (ZYZ, ABC, two-qubit KAK) and randomized benchmarking.
  * Quantum arithmetic (Draper adder), QAOA MaxCut and Grover SAT solvers.
  * Entangled state preparation (GHZ / W / graph), teleportation, superdense coding.
  * Foundations -- Bell/CHSH test, GHZ quantum metrology, BB84 key distribution.

See also ``quantum_debugger.stabilizer`` for the Clifford tableau simulator and
``quantum_debugger.tomography`` for state tomography.
"""

from .qft import qft, apply_qft, apply_inverse_qft, qft_matrix
from .grover import grover, grover_search, optimal_iterations
from .phase_estimation import (
    phase_estimation_circuit,
    estimate_phase,
    iterative_phase_estimation,
)
from .oracles import (
    bernstein_vazirani,
    bernstein_vazirani_circuit,
    deutsch,
    deutsch_jozsa,
    deutsch_jozsa_circuit,
    constant_oracle,
    balanced_oracle,
)
from .quantum_walk import quantum_walk
from .quantum_counting import quantum_counting
from .amplitude_estimation import amplitude_estimation
from .amplitude_amplification import (
    amplitude_amplification,
    optimal_amplification_iterations,
)
from .hhl import hhl
from .swap_test import swap_test
from .protocols import teleport, superdense_coding, entanglement_swap
from .shor import period_finding, shor_factor
from .error_correction import bit_flip_code, phase_flip_code, shor_code
from .hamiltonian_simulation import (
    trotter_evolve,
    trotter_circuit,
    hamiltonian_matrix,
    pauli_term_matrix,
    pauli_decompose,
    trotter_unitary,
    trotter_error_scaling,
)
from .decomposition import (
    zyz_decompose,
    abc_decomposition,
    kak_decompose,
    canonical_coordinates,
)
from .randomized_benchmarking import (
    randomized_benchmarking,
    single_qubit_clifford_group,
)
from .arithmetic import (
    qft_add,
    quantum_adder,
    qft_subtract,
    quantum_compare,
    ripple_carry_add,
    ripple_carry_subtract,
    quantum_multiply,
)
from .maxcut import solve_maxcut, brute_force_maxcut
from .state_preparation import ghz_state, w_state, graph_state
from .simon import simon, simon_oracle
from .metrology import (
    phase_sensitivity,
    parity_signal,
    quantum_fisher_information,
    qfi_mixed,
)
from .bell_test import chsh_value, correlator, bell_state, chsh_game, mermin_ghz_test
from .bb84 import bb84
from .vqe_solver import (
    variational_ground_state,
    tfim_hamiltonian,
    heisenberg_hamiltonian,
)
from .sat_solver import grover_solve
from .multicontrol import toffoli_gates, fredkin_gates, mcx_gates, apply_gates
from .grover_optimize import grover_minimize
from .qec_threshold import repetition_code_error_rate
from .qec_noise import (
    bit_flip_code_noisy,
    phase_flip_code_noisy,
    syndrome_extraction_cycle,
    repetition_code_logical_error,
    repeated_qec_cycles,
)
from .perfect_code import five_qubit_code, five_qubit_stabilizers
from .toric_code import ToricCode
from .css_code import (
    CSSCode,
    gf2_rank,
    gf2_nullspace,
    gf2_rref,
    css_from_classical,
    hypergraph_product,
)
from .surface_code import (
    repetition_check_matrix,
    hamming_check_matrix,
    planar_surface_code,
    surface_code_parameters,
    corrects_all_errors_up_to,
)
from .color_code import (
    steane_color_code,
    is_self_dual_css,
    transversal_hadamard_valid,
    transversal_cnot_valid,
)
from .steane_code import (
    steane_code,
    steane_stabilizers,
    steane_transversal,
    steane_transversal_cnot,
    steane_code_noisy,
)
from .magic_state import t_magic_state, inject_t_gate
from .distillation import (
    werner_state,
    bbpssw_distill,
    distillation_rounds,
    entanglement_swap_noisy,
    repeater_chain,
    bell_diagonal_state,
    dejmps_distill,
    dejmps_recurrence,
    dejmps_rounds,
)
from .decoherence_free import collective_dephasing, dfs_encode, dfs_protection
from .dynamical_decoupling import (
    spin_echo,
    echo_state_fidelity,
    cpmg_sequence,
    xy4_sequence,
    udd_sequence,
    switching_function_moments,
    suppression_order,
    dd_coherence,
)
from .zeno import quantum_zeno, zeno_postselected
from .loss_robustness import loss_robustness
from .nonlocality import (
    correlation_matrix,
    chsh_maximum,
    chsh_maximum_optimized,
    werner_nonlocality,
)
from .channel_capacity import coherent_information, amplitude_damping_capacity
from .holevo import (
    holevo_bound,
    accessible_information,
    holevo_gap,
    dense_coding_capacity,
)
from .discrimination import (
    helstrom_bound,
    helstrom_measurement,
    unambiguous_discrimination,
)
from .cloning import universal_clone
from .contextuality import (
    mermin_peres_square,
    classical_assignment_maximum,
    quantum_context_measurement,
)
from .geometric_phase import (
    bloch_spinor,
    pancharatnam_phase,
    solid_angle,
    berry_phase_triangle,
)
from .uncertainty import robertson_bound, entropic_uncertainty
from .magic_measures import stabilizer_renyi_entropy, magic_of_t_states
from .error_detection import (
    four_two_two_codewords,
    detect_single_errors,
    postselected_memory,
)
from .mbqc import cluster_pair, mbqc_rotation
from .weak_values import weak_value, weak_measurement_shift, weak_value_demo
from .petz import petz_recovery, petz_code_recovery
from .jordan_wigner import (
    jw_annihilation,
    jw_creation,
    jw_number,
    jw_total_number,
    hopping_hamiltonian,
    anticommutation_error,
)
from .hubbard import (
    fermi_hubbard_hamiltonian,
    hubbard_ground_energy,
    hubbard_dimer_energy,
)
from .thermal import (
    gibbs_state,
    partition_function,
    thermal_properties,
)
from .imaginary_time import imaginary_time_evolution
from .adiabatic import adiabatic_evolution
from .krylov import krylov_spectrum, krylov_ground_energy
from .loschmidt import loschmidt_echo, rate_function, quench_dynamics
from .otoc import otoc, scrambling_time
from .entanglement_growth import entanglement_growth
from .level_statistics import (
    level_spacing_ratio,
    goe_reference,
    poisson_reference,
    classify_spectrum,
)
from .kitaev_chain import kitaev_chain_hamiltonian, kitaev_ground_degeneracy
from .spin_squeezing import one_axis_twisting, best_squeezing
from .classical_shadows import (
    collect_shadows,
    estimate_observable,
    shadow_estimates,
)
from .schmidt import (
    schmidt_decomposition,
    truncation_fidelity,
    area_law_compressibility,
)
from .tebd import (
    tfim_bond_gate,
    tebd_tfim,
    tebd_magnetization,
    tfim_mps_energy,
    imaginary_tebd_ground_state,
)
from .qsp import (
    signal_operator,
    qsp_unitary,
    qsp_response,
    chebyshev_via_qsp,
    qsp_complementary_response,
)
from .block_encoding import (
    block_encode,
    top_left_block,
    is_block_encoding,
    qubitization_walk,
    chebyshev_of_matrix,
    qsvt_scalar_response,
    qsvt_transform,
)
from .lcu import lcu_block_encoding, lcu_matrix
from .matrix_functions import (
    chebyshev_coefficients,
    matrix_function_chebyshev,
    hamiltonian_simulation_qsvt,
    matrix_inverse_qsvt,
    solve_linear_system_qsvt,
)
from .qsvt_applications import (
    matrix_function_on_interval,
    matrix_sign_qsvt,
    spectral_projector_qsvt,
    matrix_sqrt_qsvt,
    matrix_inverse_sqrt_qsvt,
    matrix_power_qsvt,
    pseudo_inverse_qsvt,
    bandpass_filter_qsvt,
    matrix_exp_qsvt,
    matrix_log_qsvt,
    gibbs_state_qsvt,
    ground_state_projector_qsvt,
)
from .chebyshev_spectral import (
    spectral_moments,
    trace_of_function,
    partition_function_qsvt,
    density_of_states_kpm,
    eigenvalue_count_in_interval,
)
from .qsvt_amplification import (
    amplitude_amplification_qsvt,
    grover_amplitude_simulated,
    chebyshev_approximation,
)
from .ssh_model import (
    ssh_hamiltonian,
    ssh_winding_number,
    ssh_zero_modes,
    ssh_edge_polarization,
)
from .quantum_phase_transition import (
    ground_state_fidelity,
    fidelity_susceptibility,
    tfim_critical_field,
)
from .many_body_correlations import (
    connected_correlation,
    correlation_length,
    structure_factor,
    expectation,
)
from .entanglement_negativity import (
    partial_transpose,
    negativity,
    logarithmic_negativity,
    is_entangled_ppt,
)
from .fermion_mappings import (
    fock_annihilation,
    jordan_wigner_annihilation,
    parity_annihilation,
    bravyi_kitaev_annihilation,
    encoded_annihilation,
    jordan_wigner_matrix,
    parity_matrix,
    bravyi_kitaev_matrix,
    satisfies_car,
    pauli_weight,
)
from .molecular_hamiltonian import (
    molecular_hamiltonian,
    number_operator,
    fci_energy,
    hartree_fock_energy,
    hubbard_dimer_hamiltonian,
)
from .chemistry_ansatze import (
    hartree_fock_state,
    givens_rotation,
    uccsd_operator,
    conserves_particle_number,
    is_unitary,
    apply_ansatz,
)
from .rdm import (
    one_particle_rdm,
    two_particle_rdm,
    energy_from_rdm,
    natural_orbital_occupations,
)
from .qubit_tapering import (
    z2_symmetry_generators,
    is_symmetry,
    sector_projector,
    taper_energy,
    spectrum_is_union_of_sectors,
)
from .measurement_grouping import (
    qubit_wise_commuting_groups,
    commuting_groups,
    is_valid_grouping,
    measurement_reduction,
)
from .excited_states import (
    folded_spectrum_operator,
    nearest_eigenstate,
    subspace_energies,
    ssvqe_cost,
    deflation_hamiltonian,
    excited_spectrum_by_deflation,
)
from .quantum_distances import (
    trace_distance,
    uhlmann_fidelity,
    bures_distance,
    bures_angle,
    hilbert_schmidt_distance,
    fuchs_van_de_graaf,
    quantum_relative_entropy,
)
from .quantum_entropies import (
    von_neumann_entropy,
    renyi_entropy,
    tsallis_entropy,
    conditional_entropy,
    quantum_mutual_information,
    entanglement_entropy_pure,
)
from .coherence import (
    l1_coherence,
    relative_entropy_of_coherence,
    robustness_of_coherence,
    is_incoherent,
    dephase,
)
from .entanglement_measures import (
    concurrence,
    entanglement_of_formation,
    tangle,
    schmidt_coefficients,
    schmidt_rank,
)
from .majorization import (
    majorizes,
    nielsen_convertible,
    majorization_entropy_bound,
)
from .entanglement_witness import (
    witness_expectation,
    bell_witness,
    realign,
    realignment_norm,
    realignment_criterion,
)
from .magic_states import (
    t_state,
    h_magic_state,
    stabilizer_fidelity,
    distillation_15to1_error,
    distillation_threshold,
    distillation_rounds_to_target,
)
from .concatenation import (
    one_level_logical_error,
    concatenated_logical_error,
    pseudothreshold,
    levels_for_target,
    qubit_overhead,
    double_exponential_check,
)
from .transversal_gates import (
    transversal_gate,
    steane_codewords,
    preserves_code_space,
    logical_action,
    steane_transversal_hadamard_is_logical_h,
    steane_transversal_s_is_logical_phase,
    eastin_knill_obstruction,
)
from .gate_teleportation import resource_state, gate_teleportation, t_injection
from .clifford_t_synthesis import (
    rz,
    gate_distance,
    t_count,
    enumerate_clifford_t,
    synthesize,
    synthesize_rz,
    is_clifford_t_word,
)
from .quantum_walks import (
    continuous_time_walk_operator,
    ctqw_distribution,
    position_variance,
    line_adjacency,
    discrete_time_walk_line,
    szegedy_walk_operator,
    spatial_search_ctqw,
)
from .amplitude_estimation_advanced import (
    grover_probability,
    maximum_likelihood_ae,
    iterative_ae,
    canonical_qae,
    classical_monte_carlo_error,
    heisenberg_scaling_error,
)
from .quantum_markov import (
    is_stochastic,
    stationary_distribution,
    google_matrix,
    classical_pagerank,
    detailed_balance,
    quantum_pagerank,
)
from .phase_estimation_variants import (
    kitaev_phase_estimation,
    robust_phase_estimation,
    phase_estimation_error,
)
from .quantum_mean_estimation import (
    mean_amplitude,
    quantum_mean_estimation,
    classical_samples_for_precision,
    quantum_samples_for_precision,
    monte_carlo_speedup,
)
from .gaussian_states import (
    omega,
    vacuum_covariance,
    squeezed_covariance,
    thermal_covariance,
    symplectic_eigenvalues,
    is_physical_covariance,
    purity_gaussian,
    gaussian_entropy,
)
from .symplectic import (
    is_symplectic,
    phase_rotation_symplectic,
    squeezing_symplectic,
    beamsplitter_symplectic,
    apply_symplectic,
    two_mode_squeezing_symplectic,
)
from .fock_space import (
    annihilation_operator,
    creation_operator,
    number_operator_fock,
    coherent_state_fock,
    displacement_operator,
    squeeze_operator,
    mean_photon_number,
)
from .wigner import (
    wigner_point,
    wigner_grid,
    wigner_negativity,
    wigner_integral,
    husimi_q,
)
from .boson_sampling import (
    permanent,
    boson_sampling_probability,
    beamsplitter_unitary,
    hong_ou_mandel,
)
from .bosonic_codes import (
    cat_state,
    parity_operator,
    parity_expectation,
    cat_code_words,
    photon_loss,
    loss_flips_parity,
)
from .randomized_benchmarking_advanced import (
    rb_survival,
    fit_rb_decay,
    average_gate_fidelity_from_rb,
    error_per_clifford,
    interleaved_rb_gate_error,
)
from .xeb import (
    porter_thomas_pdf,
    porter_thomas_samples,
    linear_xeb_fidelity,
    speckle_purity,
    cross_entropy_fidelity,
)
from .quantum_volume import (
    heavy_outputs,
    heavy_output_probability,
    quantum_volume_pass,
    ideal_heavy_output_probability,
    quantum_volume,
)
from .tomography_dfe import (
    pauli_expectations,
    state_tomography,
    is_physical_density_matrix,
    direct_fidelity_estimation,
)
from .channel_metrics import (
    choi_matrix,
    entanglement_fidelity,
    average_gate_fidelity,
    pauli_transfer_matrix,
    unitarity,
)
from .mirror_benchmarking import (
    mirror_survival,
    depolarizing_layer,
    mirror_fidelity_decay,
)
from .circuit_ir import (
    op,
    circuit_unitary,
    circuits_equivalent,
    gate_count,
    two_qubit_count,
)
from .gate_optimization import (
    cancel_inverses,
    remove_identities,
    merge_rotations,
    optimize_circuit,
)
from .commutation import (
    operations_commute,
    commute_forward,
    commutation_graph,
)
from .qubit_routing import (
    coupling_map,
    is_executable,
    permutation_matrix,
    swap_network,
    route_linear,
)
from .gate_templates import (
    swap_decomposition,
    controlled_z_decomposition,
    toffoli_decomposition,
    toffoli_matrix,
    verify_template,
)
from .two_qubit_synthesis import (
    makhlin_invariants,
    is_local,
    locally_equivalent,
    cnot_count,
)
from .scheduling import (
    asap_layers,
    circuit_depth,
    circuit_parallelism,
    flatten_layers,
    critical_path_length,
)
from .qubo import (
    qubo_energy,
    ising_energy,
    qubo_to_ising,
    ising_hamiltonian,
    brute_force_ising,
    brute_force_qubo,
    max_cut_qubo,
    number_partition_qubo,
    vertex_cover_qubo,
)
from .qaoa_theory import (
    cost_diagonal,
    cost_layer,
    mixer_layer,
    qaoa_state,
    qaoa_expectation,
    optimize_qaoa_p1,
    qaoa_landscape,
)
from .adiabatic_optimization import (
    transverse_field_driver,
    interpolating_hamiltonian,
    instantaneous_gap,
    minimum_gap,
    adiabatic_evolve,
    adiabatic_success_probability,
    landau_zener_probability,
    adiabatic_runtime_bound,
)
from .quantum_annealing import (
    anneal_hamiltonian,
    anneal,
    annealing_success_probability,
    annealed_solution,
    spectral_gap_at,
)
from .grover_optimization import (
    threshold_marked,
    durr_hoyer_minimize,
    grover_adaptive_search,
    quantum_minimum_queries,
    classical_minimum_queries,
)
from .variational_ansatz import (
    hardware_efficient_ansatz,
    ansatz_num_params,
    z_observable,
    ansatz_expectation,
    random_parameters,
)
from .parameter_shift import (
    parameter_shift_gradient,
    parameter_shift_gradient_all,
    finite_difference_gradient,
    parameter_shift_hessian_diagonal,
    gradient_norm,
)
from .barren_plateaus import (
    gradient_sample_variance,
    barren_plateau_scaling,
    local_cost_gradient_variance,
    global_cost_gradient_variance,
    cost_concentration,
)
from .expressibility import (
    haar_fidelity_pdf,
    haar_mean_fidelity,
    sample_ansatz_fidelities,
    frame_potential,
    expressibility_kl,
)
from .entangling_capability import (
    meyer_wallach,
    entangling_capability,
    average_entanglement,
    is_product_state,
)
from .quantum_natural_gradient import (
    quantum_geometric_tensor,
    quantum_fisher_matrix,
    is_positive_semidefinite,
    natural_gradient,
    fubini_study_distance,
    effective_quantum_dimension,
)
from .product_formulas import (
    exact_evolution,
    first_order_trotter,
    second_order_trotter,
    fourth_order_suzuki,
    trotter_error,
    randomized_trotter,
    simulate_state,
    error_scaling_slope,
)
from .trotter_bounds import (
    commutator,
    spectral_norm,
    commutator_sum,
    first_order_error_bound,
    second_order_error_bound,
    terms_commute,
)
from .qdrift import (
    qdrift_probabilities,
    qdrift_sample_unitary,
    qdrift_channel,
    qdrift_error,
    qdrift_gate_count,
)
from .taylor_simulation import (
    taylor_series_unitary,
    taylor_error,
    taylor_truncation_order,
    hamiltonian_from_terms,
    series_convergence,
)
from .simulation_complexity import (
    trotter_first_order_steps,
    trotter_first_order_gate_count,
    trotter_second_order_steps,
    taylor_gate_count,
    qdrift_beats_trotter,
    cheapest_method,
)
from .quantum_metrology import (
    generator_variance,
    qfi_pure,
    cramer_rao_bound,
    standard_quantum_limit,
    heisenberg_limit,
    metrological_advantage,
    error_propagation,
)
from .interferometry import (
    collective_jz,
    product_probe,
    ghz_probe,
    probe_qfi,
    product_probe_qfi,
    ghz_probe_qfi,
    noon_phase_qfi,
    ramsey_signal,
)
from .spin_squeezing_metrology import (
    collective_spin,
    coherent_spin_state,
    one_axis_twisting_state,
    wineland_squeezing_parameter,
    metrological_gain,
    is_squeezed,
    best_twisting_squeezing,
)
from .multiparameter_estimation import (
    qfi_matrix,
    cramer_rao_matrix,
    parameter_incompatibility,
    total_precision_bound,
)
from .sensing_protocols import (
    signal_to_noise,
    phase_precision,
    frequency_precision,
    entanglement_gain,
    qfi_per_particle,
    is_heisenberg_scaling,
)
from .bell_inequalities import (
    measurement_operator,
    classical_chsh_bound,
    tsirelson_bound,
    algebraic_bound,
    chsh_violation,
)
from .pr_box import (
    pr_box_correlations,
    correlation_value,
    chsh_from_box,
    is_no_signaling,
    local_deterministic_box,
    pr_box_is_superquantum,
)
from .mermin_multiparty import (
    mermin_operator,
    mermin_value,
    mermin_optimal_value,
    mermin_quantum_bound,
    mermin_classical_bound,
    mermin_violation_ratio,
)
from .steering import (
    steering_value,
    steering_bound,
    is_steerable,
    werner_steering_threshold,
)
from .device_independent import (
    guessing_probability,
    certified_randomness,
    is_randomness_certified,
    di_key_rate,
    randomness_vs_violation,
)
from .quantum_channels_advanced import (
    binary_entropy,
    depolarizing_kraus,
    dephasing_kraus,
    amplitude_damping_kraus,
    apply_channel,
    entanglement_assisted_capacity,
    erasure_quantum_capacity,
    dephasing_quantum_capacity,
    holevo_information,
    channel_fidelity,
)
from .qkd_advanced import (
    bb84_key_rate,
    bb84_threshold,
    six_state_key_rate,
    six_state_threshold,
    qber_from_chsh,
    e91_key_rate,
    secret_fraction,
    sifting_ratio,
    decoy_state_gain,
)
from .quantum_networks import (
    werner_fidelity,
    swap_werner,
    entanglement_swapping_fidelity,
    repeater_werner,
    repeater_rate,
    purified_fidelity,
    path_fidelity,
    hops_before_threshold,
    ghz_distribution_fidelity,
    entanglement_routing,
)
from .tensor_contraction import (
    contract_pair,
    pairwise_cost,
    contract_chain,
    matrix_chain_left_cost,
    matrix_chain_optimal_cost,
    matrix_chain_optimal_order,
    svd_bond_truncation,
    contraction_speedup,
)
from .peps import (
    product_peps,
    bond_dimension,
    is_product_peps,
    contract_2x2,
    cluster_peps_statevector,
    cluster_state_reference,
)
from .mera import (
    disentangler,
    isometry,
    is_isometry,
    descending_superoperator,
    ascending_superoperator,
    causal_cone_width,
    ternary_isometry,
    renormalize_operator,
    coarse_grain_state,
)
from .entanglement_scaling import (
    bipartite_entropy,
    max_entanglement,
    page_average_entropy,
    random_state_entropy,
    entanglement_spectrum,
    renyi2_entropy,
    is_area_law,
    volume_law_slope,
)
from .graph_states import (
    graph_state_stabilizers,
    verify_stabilizers,
    linear_cluster_edges,
    cluster_2d_edges,
    complete_graph_edges,
    star_graph_edges,
    graph_state_entanglement,
    local_complementation,
    local_clifford_equivalent,
)
from .one_way_computing import (
    rz,
    xy_measurement_states,
    teleport_step,
    expected_step_unitary,
    expected_rotation_unitary,
    mbqc_identity,
    measurement_probability,
    byproduct_operator,
)
from .measurement_calculus import (
    measurement_pattern,
    causal_flow,
    verify_flow,
    has_flow,
    pattern_depth,
)
from .mbqc_two_qubit import (
    native_cz,
    mbqc_hadamard,
    hadamard_is_teleport,
    cnot_decomposition,
    verify_cnot_decomposition,
    mbqc_cnot,
)
from .quantum_thermodynamics import (
    free_energy,
    internal_energy,
    quench_work,
    heat_exchanged,
    nonequilibrium_free_energy,
    heat_capacity,
    thermal_entropy,
    entropy_production,
)
from .fluctuation_theorems import (
    two_point_work_distribution,
    jarzynski_average,
    free_energy_difference,
    average_work,
    work_variance,
    dissipated_work,
    verify_jarzynski,
    landauer_bound,
    crooks_ratio,
)
from .quantum_otto_cycle import (
    otto_cycle,
    otto_efficiency,
    carnot_efficiency,
    is_engine,
    efficiency_below_carnot,
)
from .passive_states import (
    passive_state,
    ergotropy,
    is_passive,
    max_extractable_work,
    bound_energy,
    gibbs_is_passive,
)
from .boolean_complexity import (
    truth_table,
    sensitivity_at,
    max_sensitivity,
    block_sensitivity,
    certificate_complexity,
    decision_tree_complexity,
    polynomial_degree,
    sensitivity_hierarchy_holds,
)
from .fourier_analysis import (
    to_pm1,
    fourier_coefficients,
    parseval,
    influence,
    total_influence,
    noise_stability,
    fourier_weight_above_degree,
    degree_from_fourier,
)
from .query_complexity import (
    deutsch_jozsa_queries,
    simon_queries,
    grover_queries,
    parity_queries,
    quantum_speedup,
    polynomial_method_bound,
    is_exponential_separation,
    grover_is_optimal,
)
from .communication_complexity import (
    equality_deterministic,
    equality_randomized,
    quantum_fingerprint_length,
    inner_product_complexity,
    disjointness_complexity,
    equality_exponential_saving,
    has_quantum_advantage,
)
from .complexity_classes import (
    known_containments,
    contains,
    problem_class,
    in_bqp,
    is_open_separation,
    hierarchy_is_consistent,
)
from .spectroscopy import unitary_eigenphase, hermitian_eigenvalue
from .readout_mitigation import (
    assignment_matrix,
    apply_readout_noise,
    mitigate_readout,
    mitigate_expectation,
)
from .virtual_distillation import virtual_distillation, distillation_report
from .symmetry_verification import (
    symmetry_project,
    symmetry_verified_expectation,
)
from .pec import (
    invert_pauli_channel,
    depolarizing_coeffs,
    apply_pauli_channel,
    pec_mitigate,
)
from .zne import (
    fold_noise_expectation,
    extrapolate_zero_noise,
    zero_noise_extrapolation,
)
from .pauli_twirling import pauli_twirl, coherent_error_kraus
from .cdr import fit_cdr_model, apply_cdr, cdr_mitigate
from .zne_extrapolation import (
    richardson_extrapolate,
    polynomial_extrapolate,
    exponential_extrapolate,
    adaptive_extrapolate,
)
from .unitary_folding import (
    fold_global,
    noise_scale_factor,
    fold_gate_sequence,
    folded_channel_expectation,
)
from .readout_advanced import (
    tensored_assignment_matrix,
    tensored_mitigate,
    iterative_bayesian_unfolding,
    constrained_readout_mitigate,
    calibrate_assignment_matrix,
)
from .pec_ptm import (
    channel_ptm,
    invert_channel_ptm,
    pauli_quasiprobabilities,
    pec_sampling_overhead,
    depolarizing_overhead,
    pec_mitigate_ptm,
)
# Open quantum systems & Lindblad dynamics (v3.1)
from .lindblad import (
    vectorize,
    unvectorize,
    left_multiply,
    right_multiply,
    dissipator_superoperator,
    apply_dissipator,
    lindbladian,
    lindblad_derivative,
    evolve_lindblad,
    is_trace_preserving,
    liouvillian_spectrum,
    spectral_gap,
    steady_state,
    amplitude_damping_jump,
    dephasing_jump,
)
from .quantum_trajectories import (
    effective_hamiltonian,
    jump_rates,
    quantum_jump_trajectory,
    trajectory_ensemble,
    trajectory_lindblad_error,
    mean_photon_emissions,
)
# NOTE: nonmarkovianity.trace_distance collides with quantum_distances.trace_distance;
# it is available via the submodule (quantum_debugger.algorithms.nonmarkovianity).
from .nonmarkovianity import (
    dephasing_map,
    coherence_trace_distance,
    markovian_coherence,
    nonmarkovian_coherence,
    distinguishability_backflow,
    blp_measure,
    is_markovian,
    revival_count,
)
from .collision_model import (
    partial_swap,
    thermal_qubit,
    collision_step,
    repeated_collisions,
    thermalize,
    fixed_point_error,
    full_swap_is_one_step,
)
from .open_qubit import (
    bloch_vector,
    density_from_bloch,
    t2_from_t1_tphi,
    t2_upper_bound,
    relaxation_times,
    bloch_decay,
    bloch_decay_matches_lindblad,
    purity,
)
# Quantum optimal control & pulse engineering (v3.2)
from .optimal_control import (
    control_hamiltonian,
    slice_propagators,
    piecewise_propagator,
    gate_fidelity,
    state_fidelity,
    grape_gradient,
    grape_optimize,
    grape_state_transfer,
    control_fluence,
    pauli,
)
from .controllability import (
    lie_bracket,
    lie_closure,
    dla_dimension,
    su_dimension,
    u_dimension,
    is_controllable,
    gate_reachable,
)
from .quantum_speed_limit import (
    mean_energy,
    energy_variance,
    energy_uncertainty,
    mandelstam_tamm_time,
    margolus_levitin_time,
    quantum_speed_limit_time,
    evolution_overlap,
    orthogonalization_time,
    saturates_mandelstam_tamm,
)
from .pulse_shapes import (
    square_pulse,
    gaussian_pulse,
    drag_pulse,
    pulse_area,
    gaussian_area,
    rotation_from_area,
    pi_pulse_amplitude,
    pulse_unitary,
    pi_pulse_is_bit_flip,
    square_pulse_unitary,
)
# LDPC codes & message-passing decoding (v3.3)
from .ldpc_codes import (
    repetition_check,
    hamming_code_check,
    syndrome,
    is_codeword,
    all_codewords,
    code_dimension,
    code_rate,
    code_parameters,
    minimum_distance,
    tanner_graph,
    column_weights,
    row_weights,
    is_regular,
    tanner_girth,
    random_regular_ldpc,
)
# NOTE: syndrome_decoding.corrects_all_errors_up_to collides with surface_code's; use the submodule.
from .syndrome_decoding import (
    syndrome_table,
    coset_leader,
    ml_decode,
    error_correcting_capability,
)
from .belief_propagation import (
    bsc_llr,
    sum_product_decode,
    min_sum_decode,
    bp_decode_error,
    bp_corrects,
    bp_matches_ml_on_weight1,
)
from .bit_flipping_decoder import (
    unsatisfied_checks,
    unsatisfied_count_per_bit,
    gallager_bit_flip,
    bit_flip_corrects,
    bit_flip_corrects_all_weight1,
    min_column_weight,
)
# ZX-calculus (v3.4)
from .zx_spiders import (
    hadamard_matrix,
    z_spider_tensor,
    spider_to_matrix,
    z_spider_matrix,
    x_spider_tensor,
    x_spider_matrix,
    is_hadamard_self_inverse,
    green_phase,
    red_phase,
)
from .zx_rewrite import (
    spider_fusion_z,
    spider_fusion_multi,
    spider_fusion_x,
    identity_rule,
    color_change_rule,
    copy_rule,
    pi_copy_rule,
    hopf_rule,
)
from .zx_gates import (
    hadamard_gate,
    z_phase_gate,
    x_phase_gate,
    z_gate,
    x_gate,
    s_gate,
    t_gate,
    cnot_zx,
    cz_zx,
    gate_equals,
    cnot_zx_is_cnot,
    cz_zx_is_cz,
)
# NOTE: phase_gadgets.rz collides with the one_way_computing/clifford_t rz; use the submodule.
from .phase_gadgets import (
    zz_phase_exact,
    zz_gadget,
    phase_gadget_exact,
    phase_gadget,
    gadget_matches_exact,
)
# Quantum chaos & scrambling (v3.5)
from .random_matrix import (
    goe_matrix,
    gue_matrix,
    wigner_surmise,
    poisson_spacing_pdf,
    semicircle_density,
    unfolded_spacings,
    level_spacing_ratios,
    mean_ratio,
    surmise_normalization,
    surmise_mean,
)
from .spectral_form_factor import (
    spectral_form_factor,
    connected_sff,
    sff_curve,
    sff_at_zero,
    plateau_value,
    long_time_average,
    reaches_plateau,
    normalized_sff,
)
from .krylov_complexity import (
    liouvillian,
    operator_inner_product,
    operator_norm,
    lanczos_coefficients,
    autocorrelation,
    reconstruct_autocorrelation,
    krylov_wavefunction,
    krylov_complexity,
    krylov_dimension,
    moment,
)
from .eth import (
    eigenbasis,
    observable_matrix,
    diagonal_elements,
    offdiagonal_elements,
    eigenstate_expectation,
    microcanonical_average,
    eth_diagonal_fluctuation,
    eth_offdiagonal_variance,
    eigenstate_matches_microcanonical,
    thermalizes,
)

__all__ = [
    "assignment_matrix",
    "apply_readout_noise",
    "mitigate_readout",
    "mitigate_expectation",
    "virtual_distillation",
    "distillation_report",
    "symmetry_project",
    "symmetry_verified_expectation",
    "invert_pauli_channel",
    "depolarizing_coeffs",
    "apply_pauli_channel",
    "pec_mitigate",
    "fold_noise_expectation",
    "extrapolate_zero_noise",
    "zero_noise_extrapolation",
    "pauli_twirl",
    "coherent_error_kraus",
    "fit_cdr_model",
    "apply_cdr",
    "cdr_mitigate",
    "richardson_extrapolate",
    "polynomial_extrapolate",
    "exponential_extrapolate",
    "adaptive_extrapolate",
    "fold_global",
    "noise_scale_factor",
    "fold_gate_sequence",
    "folded_channel_expectation",
    "tensored_assignment_matrix",
    "tensored_mitigate",
    "iterative_bayesian_unfolding",
    "constrained_readout_mitigate",
    "calibrate_assignment_matrix",
    "channel_ptm",
    "invert_channel_ptm",
    "pauli_quasiprobabilities",
    "pec_sampling_overhead",
    "depolarizing_overhead",
    "pec_mitigate_ptm",
    "cpmg_sequence",
    "xy4_sequence",
    "udd_sequence",
    "switching_function_moments",
    "suppression_order",
    "dd_coherence",
    # QFT
    "qft",
    "apply_qft",
    "apply_inverse_qft",
    "qft_matrix",
    # Grover
    "grover",
    "grover_search",
    "optimal_iterations",
    # Phase estimation
    "phase_estimation_circuit",
    "estimate_phase",
    "iterative_phase_estimation",
    # Oracle algorithms
    "bernstein_vazirani",
    "bernstein_vazirani_circuit",
    "deutsch",
    "deutsch_jozsa",
    "deutsch_jozsa_circuit",
    "constant_oracle",
    "balanced_oracle",
    # Walk, counting & estimation
    "quantum_walk",
    "quantum_counting",
    "amplitude_estimation",
    "amplitude_amplification",
    "optimal_amplification_iterations",
    # Linear systems
    "hhl",
    # Overlap / fidelity
    "swap_test",
    # Protocols
    "teleport",
    "superdense_coding",
    "entanglement_swap",
    # Shor
    "period_finding",
    "shor_factor",
    # Error correction
    "bit_flip_code",
    "phase_flip_code",
    "shor_code",
    # Hamiltonian simulation
    "trotter_evolve",
    "trotter_circuit",
    "hamiltonian_matrix",
    "pauli_term_matrix",
    "pauli_decompose",
    "trotter_unitary",
    "trotter_error_scaling",
    # Gate decomposition
    "zyz_decompose",
    "abc_decomposition",
    "kak_decompose",
    "canonical_coordinates",
    # Randomized benchmarking
    "randomized_benchmarking",
    "single_qubit_clifford_group",
    # Quantum arithmetic
    "qft_add",
    "quantum_adder",
    "qft_subtract",
    "quantum_compare",
    "ripple_carry_add",
    "ripple_carry_subtract",
    "quantum_multiply",
    # QAOA MaxCut solver
    "solve_maxcut",
    "brute_force_maxcut",
    # State preparation
    "ghz_state",
    "w_state",
    "graph_state",
    # Simon's algorithm
    "simon",
    "simon_oracle",
    # Quantum metrology
    "phase_sensitivity",
    "parity_signal",
    "quantum_fisher_information",
    "qfi_mixed",
    # Bell / CHSH test
    "chsh_value",
    "correlator",
    "bell_state",
    "chsh_game",
    "mermin_ghz_test",
    # BB84 QKD
    "bb84",
    # Variational ground-state solver
    "variational_ground_state",
    "tfim_hamiltonian",
    "heisenberg_hamiltonian",
    # Grover SAT solver
    "grover_solve",
    # Multi-controlled-X synthesis
    "toffoli_gates",
    "fredkin_gates",
    "mcx_gates",
    "apply_gates",
    # Grover adaptive minimization
    "grover_minimize",
    # QEC threshold
    "repetition_code_error_rate",
    "bit_flip_code_noisy",
    "phase_flip_code_noisy",
    "syndrome_extraction_cycle",
    "repetition_code_logical_error",
    "repeated_qec_cycles",
    "five_qubit_code",
    "five_qubit_stabilizers",
    "ToricCode",
    "CSSCode",
    "gf2_rank",
    "gf2_nullspace",
    "gf2_rref",
    "css_from_classical",
    "hypergraph_product",
    "repetition_check_matrix",
    "hamming_check_matrix",
    "planar_surface_code",
    "surface_code_parameters",
    "corrects_all_errors_up_to",
    "steane_color_code",
    "is_self_dual_css",
    "transversal_hadamard_valid",
    "transversal_cnot_valid",
    "steane_code",
    "steane_stabilizers",
    "steane_transversal",
    "steane_transversal_cnot",
    "steane_code_noisy",
    "t_magic_state",
    "inject_t_gate",
    "werner_state",
    "bbpssw_distill",
    "distillation_rounds",
    "entanglement_swap_noisy",
    "repeater_chain",
    "bell_diagonal_state",
    "dejmps_distill",
    "dejmps_recurrence",
    "dejmps_rounds",
    "collective_dephasing",
    "dfs_encode",
    "dfs_protection",
    "spin_echo",
    "echo_state_fidelity",
    "quantum_zeno",
    "zeno_postselected",
    "loss_robustness",
    "correlation_matrix",
    "chsh_maximum",
    "chsh_maximum_optimized",
    "werner_nonlocality",
    "coherent_information",
    "amplitude_damping_capacity",
    "holevo_bound",
    "accessible_information",
    "holevo_gap",
    "dense_coding_capacity",
    "helstrom_bound",
    "helstrom_measurement",
    "unambiguous_discrimination",
    "universal_clone",
    "mermin_peres_square",
    "classical_assignment_maximum",
    "quantum_context_measurement",
    "bloch_spinor",
    "pancharatnam_phase",
    "solid_angle",
    "berry_phase_triangle",
    "robertson_bound",
    "entropic_uncertainty",
    "stabilizer_renyi_entropy",
    "magic_of_t_states",
    "four_two_two_codewords",
    "detect_single_errors",
    "postselected_memory",
    "cluster_pair",
    "mbqc_rotation",
    "weak_value",
    "weak_measurement_shift",
    "weak_value_demo",
    "petz_recovery",
    "petz_code_recovery",
    "jw_annihilation",
    "jw_creation",
    "jw_number",
    "jw_total_number",
    "hopping_hamiltonian",
    "anticommutation_error",
    "fermi_hubbard_hamiltonian",
    "hubbard_ground_energy",
    "hubbard_dimer_energy",
    "gibbs_state",
    "partition_function",
    "thermal_properties",
    "imaginary_time_evolution",
    "adiabatic_evolution",
    "krylov_spectrum",
    "krylov_ground_energy",
    "loschmidt_echo",
    "rate_function",
    "quench_dynamics",
    "otoc",
    "scrambling_time",
    "entanglement_growth",
    "level_spacing_ratio",
    "goe_reference",
    "poisson_reference",
    "classify_spectrum",
    "kitaev_chain_hamiltonian",
    "kitaev_ground_degeneracy",
    "one_axis_twisting",
    "best_squeezing",
    "collect_shadows",
    "estimate_observable",
    "shadow_estimates",
    "schmidt_decomposition",
    "truncation_fidelity",
    "area_law_compressibility",
    "tfim_bond_gate",
    "tebd_tfim",
    "tebd_magnetization",
    "tfim_mps_energy",
    "imaginary_tebd_ground_state",
    "signal_operator",
    "qsp_unitary",
    "qsp_response",
    "chebyshev_via_qsp",
    "qsp_complementary_response",
    "block_encode",
    "top_left_block",
    "is_block_encoding",
    "qubitization_walk",
    "chebyshev_of_matrix",
    "qsvt_scalar_response",
    "qsvt_transform",
    "lcu_block_encoding",
    "lcu_matrix",
    "chebyshev_coefficients",
    "matrix_function_chebyshev",
    "hamiltonian_simulation_qsvt",
    "matrix_inverse_qsvt",
    "solve_linear_system_qsvt",
    "matrix_function_on_interval",
    "matrix_sign_qsvt",
    "spectral_projector_qsvt",
    "matrix_sqrt_qsvt",
    "matrix_inverse_sqrt_qsvt",
    "matrix_power_qsvt",
    "pseudo_inverse_qsvt",
    "bandpass_filter_qsvt",
    "matrix_exp_qsvt",
    "matrix_log_qsvt",
    "gibbs_state_qsvt",
    "ground_state_projector_qsvt",
    "spectral_moments",
    "trace_of_function",
    "partition_function_qsvt",
    "density_of_states_kpm",
    "eigenvalue_count_in_interval",
    "amplitude_amplification_qsvt",
    "grover_amplitude_simulated",
    "chebyshev_approximation",
    # SSH topological insulator
    "ssh_hamiltonian",
    "ssh_winding_number",
    "ssh_zero_modes",
    "ssh_edge_polarization",
    # Quantum phase transitions (fidelity)
    "ground_state_fidelity",
    "fidelity_susceptibility",
    "tfim_critical_field",
    # Many-body correlations
    "connected_correlation",
    "correlation_length",
    "structure_factor",
    "expectation",
    # Entanglement negativity
    "partial_transpose",
    "negativity",
    "logarithmic_negativity",
    "is_entangled_ppt",
    # Quantum chemistry — fermion mappings
    "fock_annihilation",
    "jordan_wigner_annihilation",
    "parity_annihilation",
    "bravyi_kitaev_annihilation",
    "encoded_annihilation",
    "jordan_wigner_matrix",
    "parity_matrix",
    "bravyi_kitaev_matrix",
    "satisfies_car",
    "pauli_weight",
    # Quantum chemistry — molecular Hamiltonians
    "molecular_hamiltonian",
    "number_operator",
    "fci_energy",
    "hartree_fock_energy",
    "hubbard_dimer_hamiltonian",
    # Quantum chemistry — ansätze
    "hartree_fock_state",
    "givens_rotation",
    "uccsd_operator",
    "conserves_particle_number",
    "is_unitary",
    "apply_ansatz",
    # Quantum chemistry — RDMs
    "one_particle_rdm",
    "two_particle_rdm",
    "energy_from_rdm",
    "natural_orbital_occupations",
    # Quantum chemistry — qubit tapering
    "z2_symmetry_generators",
    "is_symmetry",
    "sector_projector",
    "taper_energy",
    "spectrum_is_union_of_sectors",
    # Quantum chemistry — measurement grouping
    "qubit_wise_commuting_groups",
    "commuting_groups",
    "is_valid_grouping",
    "measurement_reduction",
    # Quantum chemistry — excited states
    "folded_spectrum_operator",
    "nearest_eigenstate",
    "subspace_energies",
    "ssvqe_cost",
    "deflation_hamiltonian",
    "excited_spectrum_by_deflation",
    # Quantum information — distances
    "trace_distance",
    "uhlmann_fidelity",
    "bures_distance",
    "bures_angle",
    "hilbert_schmidt_distance",
    "fuchs_van_de_graaf",
    "quantum_relative_entropy",
    # Quantum information — entropies
    "von_neumann_entropy",
    "renyi_entropy",
    "tsallis_entropy",
    "conditional_entropy",
    "quantum_mutual_information",
    "entanglement_entropy_pure",
    # Quantum information — coherence
    "l1_coherence",
    "relative_entropy_of_coherence",
    "robustness_of_coherence",
    "is_incoherent",
    "dephase",
    # Quantum information — entanglement measures
    "concurrence",
    "entanglement_of_formation",
    "tangle",
    "schmidt_coefficients",
    "schmidt_rank",
    # Quantum information — majorization
    "majorizes",
    "nielsen_convertible",
    "majorization_entropy_bound",
    # Quantum information — witnesses
    "witness_expectation",
    "bell_witness",
    "realign",
    "realignment_norm",
    "realignment_criterion",
    # Fault tolerance — magic states
    "t_state",
    "h_magic_state",
    "stabilizer_fidelity",
    "distillation_15to1_error",
    "distillation_threshold",
    "distillation_rounds_to_target",
    # Fault tolerance — concatenation
    "one_level_logical_error",
    "concatenated_logical_error",
    "pseudothreshold",
    "levels_for_target",
    "qubit_overhead",
    "double_exponential_check",
    # Fault tolerance — transversal gates
    "transversal_gate",
    "steane_codewords",
    "preserves_code_space",
    "logical_action",
    "steane_transversal_hadamard_is_logical_h",
    "steane_transversal_s_is_logical_phase",
    "eastin_knill_obstruction",
    # Fault tolerance — gate teleportation
    "resource_state",
    "gate_teleportation",
    "t_injection",
    # Fault tolerance — Clifford+T synthesis
    "rz",
    "gate_distance",
    "t_count",
    "enumerate_clifford_t",
    "synthesize",
    "synthesize_rz",
    "is_clifford_t_word",
    # Advanced algorithms — quantum walks
    "continuous_time_walk_operator",
    "ctqw_distribution",
    "position_variance",
    "line_adjacency",
    "discrete_time_walk_line",
    "szegedy_walk_operator",
    "spatial_search_ctqw",
    # Advanced algorithms — amplitude estimation
    "grover_probability",
    "maximum_likelihood_ae",
    "iterative_ae",
    "canonical_qae",
    "classical_monte_carlo_error",
    "heisenberg_scaling_error",
    # Advanced algorithms — Markov & PageRank
    "is_stochastic",
    "stationary_distribution",
    "google_matrix",
    "classical_pagerank",
    "detailed_balance",
    "quantum_pagerank",
    # Advanced algorithms — phase estimation variants
    "kitaev_phase_estimation",
    "robust_phase_estimation",
    "phase_estimation_error",
    # Advanced algorithms — mean estimation
    "mean_amplitude",
    "quantum_mean_estimation",
    "classical_samples_for_precision",
    "quantum_samples_for_precision",
    "monte_carlo_speedup",
    # Continuous variable — Gaussian states
    "omega",
    "vacuum_covariance",
    "squeezed_covariance",
    "thermal_covariance",
    "symplectic_eigenvalues",
    "is_physical_covariance",
    "purity_gaussian",
    "gaussian_entropy",
    # Continuous variable — symplectic transforms
    "is_symplectic",
    "phase_rotation_symplectic",
    "squeezing_symplectic",
    "beamsplitter_symplectic",
    "apply_symplectic",
    "two_mode_squeezing_symplectic",
    # Continuous variable — Fock space
    "annihilation_operator",
    "creation_operator",
    "number_operator_fock",
    "coherent_state_fock",
    "displacement_operator",
    "squeeze_operator",
    "mean_photon_number",
    # Continuous variable — Wigner
    "wigner_point",
    "wigner_grid",
    "wigner_negativity",
    "wigner_integral",
    "husimi_q",
    # Continuous variable — boson sampling
    "permanent",
    "boson_sampling_probability",
    "beamsplitter_unitary",
    "hong_ou_mandel",
    # Continuous variable — bosonic codes
    "cat_state",
    "parity_operator",
    "parity_expectation",
    "cat_code_words",
    "photon_loss",
    "loss_flips_parity",
    # Benchmarking — randomized benchmarking
    "rb_survival",
    "fit_rb_decay",
    "average_gate_fidelity_from_rb",
    "error_per_clifford",
    "interleaved_rb_gate_error",
    # Benchmarking — cross-entropy
    "porter_thomas_pdf",
    "porter_thomas_samples",
    "linear_xeb_fidelity",
    "speckle_purity",
    "cross_entropy_fidelity",
    # Benchmarking — quantum volume
    "heavy_outputs",
    "heavy_output_probability",
    "quantum_volume_pass",
    "ideal_heavy_output_probability",
    "quantum_volume",
    # Benchmarking — tomography & DFE
    "pauli_expectations",
    "state_tomography",
    "is_physical_density_matrix",
    "direct_fidelity_estimation",
    # Benchmarking — channel metrics
    "choi_matrix",
    "entanglement_fidelity",
    "average_gate_fidelity",
    "pauli_transfer_matrix",
    "unitarity",
    # Benchmarking — mirror benchmarking
    "mirror_survival",
    "depolarizing_layer",
    "mirror_fidelity_decay",
    # Compilation — circuit IR
    "op",
    "circuit_unitary",
    "circuits_equivalent",
    "gate_count",
    "two_qubit_count",
    # Compilation — optimization
    "cancel_inverses",
    "remove_identities",
    "merge_rotations",
    "optimize_circuit",
    # Compilation — commutation
    "operations_commute",
    "commute_forward",
    "commutation_graph",
    # Compilation — routing
    "coupling_map",
    "is_executable",
    "permutation_matrix",
    "swap_network",
    "route_linear",
    # Compilation — templates
    "swap_decomposition",
    "controlled_z_decomposition",
    "toffoli_decomposition",
    "toffoli_matrix",
    "verify_template",
    # Compilation — two-qubit synthesis
    "makhlin_invariants",
    "is_local",
    "locally_equivalent",
    "cnot_count",
    # Compilation — scheduling
    "asap_layers",
    "circuit_depth",
    "circuit_parallelism",
    "flatten_layers",
    "critical_path_length",
    # Optimization — QUBO / Ising
    "qubo_energy",
    "ising_energy",
    "qubo_to_ising",
    "ising_hamiltonian",
    "brute_force_ising",
    "brute_force_qubo",
    "max_cut_qubo",
    "number_partition_qubo",
    "vertex_cover_qubo",
    # Optimization — QAOA theory
    "cost_diagonal",
    "cost_layer",
    "mixer_layer",
    "qaoa_state",
    "qaoa_expectation",
    "optimize_qaoa_p1",
    "qaoa_landscape",
    # Optimization — adiabatic
    "transverse_field_driver",
    "interpolating_hamiltonian",
    "instantaneous_gap",
    "minimum_gap",
    "adiabatic_evolve",
    "adiabatic_success_probability",
    "landau_zener_probability",
    "adiabatic_runtime_bound",
    # Optimization — annealing
    "anneal_hamiltonian",
    "anneal",
    "annealing_success_probability",
    "annealed_solution",
    "spectral_gap_at",
    # Optimization — Grover-based
    "threshold_marked",
    "durr_hoyer_minimize",
    "grover_adaptive_search",
    "quantum_minimum_queries",
    "classical_minimum_queries",
    # VQA theory — ansatz
    "hardware_efficient_ansatz",
    "ansatz_num_params",
    "z_observable",
    "ansatz_expectation",
    "random_parameters",
    # VQA theory — parameter-shift gradients
    "parameter_shift_gradient",
    "parameter_shift_gradient_all",
    "finite_difference_gradient",
    "parameter_shift_hessian_diagonal",
    "gradient_norm",
    # VQA theory — barren plateaus
    "gradient_sample_variance",
    "barren_plateau_scaling",
    "local_cost_gradient_variance",
    "global_cost_gradient_variance",
    "cost_concentration",
    # VQA theory — expressibility
    "haar_fidelity_pdf",
    "haar_mean_fidelity",
    "sample_ansatz_fidelities",
    "frame_potential",
    "expressibility_kl",
    # VQA theory — entangling capability
    "meyer_wallach",
    "entangling_capability",
    "average_entanglement",
    "is_product_state",
    # VQA theory — natural gradient
    "quantum_geometric_tensor",
    "quantum_fisher_matrix",
    "is_positive_semidefinite",
    "natural_gradient",
    "fubini_study_distance",
    "effective_quantum_dimension",
    # Hamiltonian simulation — product formulas
    "exact_evolution",
    "first_order_trotter",
    "second_order_trotter",
    "fourth_order_suzuki",
    "trotter_error",
    "randomized_trotter",
    "simulate_state",
    "error_scaling_slope",
    # Hamiltonian simulation — commutator bounds
    "commutator",
    "spectral_norm",
    "commutator_sum",
    "first_order_error_bound",
    "second_order_error_bound",
    "terms_commute",
    # Hamiltonian simulation — qDRIFT
    "qdrift_probabilities",
    "qdrift_sample_unitary",
    "qdrift_channel",
    "qdrift_error",
    "qdrift_gate_count",
    # Hamiltonian simulation — Taylor series
    "taylor_series_unitary",
    "taylor_error",
    "taylor_truncation_order",
    "hamiltonian_from_terms",
    "series_convergence",
    # Hamiltonian simulation — complexity
    "trotter_first_order_steps",
    "trotter_first_order_gate_count",
    "trotter_second_order_steps",
    "taylor_gate_count",
    "qdrift_beats_trotter",
    "cheapest_method",
    # Metrology — quantum Fisher information
    "generator_variance",
    "qfi_pure",
    "cramer_rao_bound",
    "standard_quantum_limit",
    "heisenberg_limit",
    "metrological_advantage",
    "error_propagation",
    # Metrology — interferometry
    "collective_jz",
    "product_probe",
    "ghz_probe",
    "probe_qfi",
    "product_probe_qfi",
    "ghz_probe_qfi",
    "noon_phase_qfi",
    "ramsey_signal",
    # Metrology — spin squeezing
    "collective_spin",
    "coherent_spin_state",
    "one_axis_twisting_state",
    "wineland_squeezing_parameter",
    "metrological_gain",
    "is_squeezed",
    "best_twisting_squeezing",
    # Metrology — multiparameter
    "qfi_matrix",
    "cramer_rao_matrix",
    "parameter_incompatibility",
    "total_precision_bound",
    # Metrology — sensing protocols
    "signal_to_noise",
    "phase_precision",
    "frequency_precision",
    "entanglement_gain",
    "qfi_per_particle",
    "is_heisenberg_scaling",
    # Foundations — CHSH
    "measurement_operator",
    "classical_chsh_bound",
    "tsirelson_bound",
    "algebraic_bound",
    "chsh_violation",
    # Foundations — PR box
    "pr_box_correlations",
    "correlation_value",
    "chsh_from_box",
    "is_no_signaling",
    "local_deterministic_box",
    "pr_box_is_superquantum",
    # Foundations — Mermin
    "mermin_operator",
    "mermin_value",
    "mermin_optimal_value",
    "mermin_quantum_bound",
    "mermin_classical_bound",
    "mermin_violation_ratio",
    # Foundations — steering
    "steering_value",
    "steering_bound",
    "is_steerable",
    "werner_steering_threshold",
    # Foundations — device-independent
    "guessing_probability",
    "certified_randomness",
    "is_randomness_certified",
    "di_key_rate",
    "randomness_vs_violation",
    # Communication — channel capacities
    "binary_entropy",
    "depolarizing_kraus",
    "dephasing_kraus",
    "amplitude_damping_kraus",
    "apply_channel",
    "entanglement_assisted_capacity",
    "erasure_quantum_capacity",
    "dephasing_quantum_capacity",
    "holevo_information",
    "channel_fidelity",
    # Communication — QKD
    "bb84_key_rate",
    "bb84_threshold",
    "six_state_key_rate",
    "six_state_threshold",
    "qber_from_chsh",
    "e91_key_rate",
    "secret_fraction",
    "sifting_ratio",
    "decoy_state_gain",
    # Communication — networks
    "werner_fidelity",
    "swap_werner",
    "entanglement_swapping_fidelity",
    "repeater_werner",
    "repeater_rate",
    "purified_fidelity",
    "path_fidelity",
    "hops_before_threshold",
    "ghz_distribution_fidelity",
    "entanglement_routing",
    # Tensor networks II — contraction
    "contract_pair",
    "pairwise_cost",
    "contract_chain",
    "matrix_chain_left_cost",
    "matrix_chain_optimal_cost",
    "matrix_chain_optimal_order",
    "svd_bond_truncation",
    "contraction_speedup",
    # Tensor networks II — PEPS
    "product_peps",
    "bond_dimension",
    "is_product_peps",
    "contract_2x2",
    "cluster_peps_statevector",
    "cluster_state_reference",
    # Tensor networks II — MERA
    "disentangler",
    "isometry",
    "is_isometry",
    "descending_superoperator",
    "ascending_superoperator",
    "causal_cone_width",
    "ternary_isometry",
    "renormalize_operator",
    "coarse_grain_state",
    # Tensor networks II — entanglement scaling
    "bipartite_entropy",
    "max_entanglement",
    "page_average_entropy",
    "random_state_entropy",
    "entanglement_spectrum",
    "renyi2_entropy",
    "is_area_law",
    "volume_law_slope",
    # MBQC — graph states
    "graph_state_stabilizers",
    "verify_stabilizers",
    "linear_cluster_edges",
    "cluster_2d_edges",
    "complete_graph_edges",
    "star_graph_edges",
    "graph_state_entanglement",
    "local_complementation",
    "local_clifford_equivalent",
    # MBQC — one-way computing
    "rz",
    "xy_measurement_states",
    "teleport_step",
    "expected_step_unitary",
    "expected_rotation_unitary",
    "mbqc_identity",
    "measurement_probability",
    "byproduct_operator",
    # MBQC — measurement calculus
    "measurement_pattern",
    "causal_flow",
    "verify_flow",
    "has_flow",
    "pattern_depth",
    # MBQC — two-qubit gates
    "native_cz",
    "mbqc_hadamard",
    "hadamard_is_teleport",
    "cnot_decomposition",
    "verify_cnot_decomposition",
    "mbqc_cnot",
    # Thermodynamics — work, heat, entropy
    "free_energy",
    "internal_energy",
    "quench_work",
    "heat_exchanged",
    "nonequilibrium_free_energy",
    "heat_capacity",
    "thermal_entropy",
    "entropy_production",
    # Thermodynamics — fluctuation theorems
    "two_point_work_distribution",
    "jarzynski_average",
    "free_energy_difference",
    "average_work",
    "work_variance",
    "dissipated_work",
    "verify_jarzynski",
    "landauer_bound",
    "crooks_ratio",
    # Thermodynamics — Otto engine
    "otto_cycle",
    "otto_efficiency",
    "carnot_efficiency",
    "is_engine",
    "efficiency_below_carnot",
    # Thermodynamics — passive states
    "passive_state",
    "ergotropy",
    "is_passive",
    "max_extractable_work",
    "bound_energy",
    "gibbs_is_passive",
    # Complexity — Boolean functions
    "truth_table",
    "sensitivity_at",
    "max_sensitivity",
    "block_sensitivity",
    "certificate_complexity",
    "decision_tree_complexity",
    "polynomial_degree",
    "sensitivity_hierarchy_holds",
    # Complexity — Fourier analysis
    "to_pm1",
    "fourier_coefficients",
    "parseval",
    "influence",
    "total_influence",
    "noise_stability",
    "fourier_weight_above_degree",
    "degree_from_fourier",
    # Complexity — query complexity
    "deutsch_jozsa_queries",
    "simon_queries",
    "grover_queries",
    "parity_queries",
    "quantum_speedup",
    "polynomial_method_bound",
    "is_exponential_separation",
    "grover_is_optimal",
    # Complexity — communication complexity
    "equality_deterministic",
    "equality_randomized",
    "quantum_fingerprint_length",
    "inner_product_complexity",
    "disjointness_complexity",
    "equality_exponential_saving",
    "has_quantum_advantage",
    # Complexity — complexity classes
    "known_containments",
    "contains",
    "problem_class",
    "in_bqp",
    "is_open_separation",
    "hierarchy_is_consistent",
    # Quantum spectroscopy
    "unitary_eigenphase",
    "hermitian_eigenvalue",
    # Open systems — Lindblad dynamics
    "vectorize",
    "unvectorize",
    "left_multiply",
    "right_multiply",
    "dissipator_superoperator",
    "apply_dissipator",
    "lindbladian",
    "lindblad_derivative",
    "evolve_lindblad",
    "is_trace_preserving",
    "liouvillian_spectrum",
    "spectral_gap",
    "steady_state",
    "amplitude_damping_jump",
    "dephasing_jump",
    # Open systems — quantum trajectories
    "effective_hamiltonian",
    "jump_rates",
    "quantum_jump_trajectory",
    "trajectory_ensemble",
    "trajectory_lindblad_error",
    "mean_photon_emissions",
    # Open systems — non-Markovianity
    "dephasing_map",
    "coherence_trace_distance",
    "markovian_coherence",
    "nonmarkovian_coherence",
    "distinguishability_backflow",
    "blp_measure",
    "is_markovian",
    "revival_count",
    # Open systems — collision models
    "partial_swap",
    "thermal_qubit",
    "collision_step",
    "repeated_collisions",
    "thermalize",
    "fixed_point_error",
    "full_swap_is_one_step",
    # Open systems — qubit relaxation (T1/T2)
    "bloch_vector",
    "density_from_bloch",
    "t2_from_t1_tphi",
    "t2_upper_bound",
    "relaxation_times",
    "bloch_decay",
    "bloch_decay_matches_lindblad",
    "purity",
    # Optimal control — GRAPE
    "control_hamiltonian",
    "slice_propagators",
    "piecewise_propagator",
    "gate_fidelity",
    "state_fidelity",
    "grape_gradient",
    "grape_optimize",
    "grape_state_transfer",
    "control_fluence",
    "pauli",
    # Optimal control — controllability
    "lie_bracket",
    "lie_closure",
    "dla_dimension",
    "su_dimension",
    "u_dimension",
    "is_controllable",
    "gate_reachable",
    # Optimal control — quantum speed limits
    "mean_energy",
    "energy_variance",
    "energy_uncertainty",
    "mandelstam_tamm_time",
    "margolus_levitin_time",
    "quantum_speed_limit_time",
    "evolution_overlap",
    "orthogonalization_time",
    "saturates_mandelstam_tamm",
    # Optimal control — pulse shapes
    "square_pulse",
    "gaussian_pulse",
    "drag_pulse",
    "pulse_area",
    "gaussian_area",
    "rotation_from_area",
    "pi_pulse_amplitude",
    "pulse_unitary",
    "pi_pulse_is_bit_flip",
    "square_pulse_unitary",
    # LDPC codes
    "repetition_check",
    "hamming_code_check",
    "syndrome",
    "is_codeword",
    "all_codewords",
    "code_dimension",
    "code_rate",
    "code_parameters",
    "minimum_distance",
    "tanner_graph",
    "column_weights",
    "row_weights",
    "is_regular",
    "tanner_girth",
    "random_regular_ldpc",
    # LDPC — exact syndrome decoding
    "syndrome_table",
    "coset_leader",
    "ml_decode",
    "error_correcting_capability",
    # LDPC — belief propagation
    "bsc_llr",
    "sum_product_decode",
    "min_sum_decode",
    "bp_decode_error",
    "bp_corrects",
    "bp_matches_ml_on_weight1",
    # LDPC — bit flipping
    "unsatisfied_checks",
    "unsatisfied_count_per_bit",
    "gallager_bit_flip",
    "bit_flip_corrects",
    "bit_flip_corrects_all_weight1",
    "min_column_weight",
    # ZX-calculus — spiders
    "hadamard_matrix",
    "z_spider_tensor",
    "spider_to_matrix",
    "z_spider_matrix",
    "x_spider_tensor",
    "x_spider_matrix",
    "is_hadamard_self_inverse",
    "green_phase",
    "red_phase",
    # ZX-calculus — rewrite rules
    "spider_fusion_z",
    "spider_fusion_multi",
    "spider_fusion_x",
    "identity_rule",
    "color_change_rule",
    "copy_rule",
    "pi_copy_rule",
    "hopf_rule",
    # ZX-calculus — gates
    "hadamard_gate",
    "z_phase_gate",
    "x_phase_gate",
    "z_gate",
    "x_gate",
    "s_gate",
    "t_gate",
    "cnot_zx",
    "cz_zx",
    "gate_equals",
    "cnot_zx_is_cnot",
    "cz_zx_is_cz",
    # ZX-calculus — phase gadgets
    "zz_phase_exact",
    "zz_gadget",
    "phase_gadget_exact",
    "phase_gadget",
    "gadget_matches_exact",
    # Chaos — random-matrix theory
    "goe_matrix",
    "gue_matrix",
    "wigner_surmise",
    "poisson_spacing_pdf",
    "semicircle_density",
    "unfolded_spacings",
    "level_spacing_ratios",
    "mean_ratio",
    "surmise_normalization",
    "surmise_mean",
    # Chaos — spectral form factor
    "spectral_form_factor",
    "connected_sff",
    "sff_curve",
    "sff_at_zero",
    "plateau_value",
    "long_time_average",
    "reaches_plateau",
    "normalized_sff",
    # Chaos — Krylov complexity
    "liouvillian",
    "operator_inner_product",
    "operator_norm",
    "lanczos_coefficients",
    "autocorrelation",
    "reconstruct_autocorrelation",
    "krylov_wavefunction",
    "krylov_complexity",
    "krylov_dimension",
    "moment",
    # Chaos — eigenstate thermalization
    "eigenbasis",
    "observable_matrix",
    "diagonal_elements",
    "offdiagonal_elements",
    "eigenstate_expectation",
    "microcanonical_average",
    "eth_diagonal_fluctuation",
    "eth_offdiagonal_variance",
    "eigenstate_matches_microcanonical",
    "thermalizes",
]
