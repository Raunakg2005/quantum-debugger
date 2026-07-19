"""
Quantum Algorithms Library

Textbook quantum algorithms implemented on the state-vector simulator:
QFT, Quantum Phase Estimation, Grover search, Bernstein-Vazirani, Deutsch-Jozsa.
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
from .protocols import teleport, superdense_coding
from .shor import period_finding, shor_factor
from .error_correction import bit_flip_code, phase_flip_code, shor_code
from .hamiltonian_simulation import (
    trotter_evolve,
    trotter_circuit,
    hamiltonian_matrix,
    pauli_term_matrix,
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

__all__ = [
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
    # Gate decomposition
    "zyz_decompose",
    "abc_decomposition",
    "kak_decompose",
    "canonical_coordinates",
    # Randomized benchmarking
    "randomized_benchmarking",
    "single_qubit_clifford_group",
]
