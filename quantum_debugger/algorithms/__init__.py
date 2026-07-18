"""
Quantum Algorithms Library

Textbook quantum algorithms implemented on the state-vector simulator:
QFT, Quantum Phase Estimation, Grover search, Bernstein-Vazirani, Deutsch-Jozsa.
"""

from .qft import qft, apply_qft, apply_inverse_qft, qft_matrix
from .grover import grover, grover_search, optimal_iterations
from .phase_estimation import phase_estimation_circuit, estimate_phase
from .oracles import (
    bernstein_vazirani,
    bernstein_vazirani_circuit,
    deutsch_jozsa,
    deutsch_jozsa_circuit,
    constant_oracle,
    balanced_oracle,
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
    # Oracle algorithms
    "bernstein_vazirani",
    "bernstein_vazirani_circuit",
    "deutsch_jozsa",
    "deutsch_jozsa_circuit",
    "constant_oracle",
    "balanced_oracle",
]
