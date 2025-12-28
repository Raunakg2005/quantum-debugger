"""
Quantum Machine Learning (QML) Module
"""

# Core gates
from .gates.parameterized import ParameterizedGate, RXGate, RYGate, RZGate

# Algorithms
from .algorithms.vqe import VQE
from .algorithms.qaoa import QAOA

# Hamiltonians
from .hamiltonians.molecular import h2_hamiltonian

# Note: Ansatz and Optimizers should be imported directly from their submodules
# to avoid circular dependencies: 
#   from quantum_debugger.qml.ansatz import real_amplitudes
#   from quantum_debugger.qml.optimizers import AdamOptimizer

__all__ = [
    # Gates
    'ParameterizedGate', 'RXGate', 'RYGate', 'RZGate',
    # Algorithms
    'VQE', 'QAOA',
    # Hamiltonians
    'h2_hamiltonian',
]
