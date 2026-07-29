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
from .dynamical_decoupling import spin_echo, echo_state_fidelity
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
    # Quantum spectroscopy
    "unitary_eigenphase",
    "hermitian_eigenvalue",
]
