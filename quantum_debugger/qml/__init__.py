"""
Quantum Machine Learning Module
================================

Parameterized gates, variational algorithms, and quantum ML tools.
"""

from .gates.parameterized import RXGate, RYGate, RZGate, ParameterizedGate
from .algorithms.vqe import VQE
from .algorithms.qaoa import QAOA
from .hamiltonians.molecular import h2_hamiltonian, lih_hamiltonian
from .ansatz import (
    hardware_efficient_ansatz,
    real_amplitudes_ansatz,
    ucc_singlet_ansatz,
    alternating_layered_ansatz,
    num_parameters
)

__all__ = [
    # Gates
    'RXGate', 'RYGate', 'RZGate', 'ParameterizedGate',
    # Algorithms
    'VQE', 'QAOA',
    # Hamiltonians
    'h2_hamiltonian', 'lih_hamiltonian',
    # Ansatz
    'hardware_efficient_ansatz', 'real_amplitudes_ansatz',
    'ucc_singlet_ansatz', 'alternating_layered_ansatz',
    'num_parameters'
]
