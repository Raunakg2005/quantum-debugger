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
    # Quantum spectroscopy
    "unitary_eigenphase",
    "hermitian_eigenvalue",
]
