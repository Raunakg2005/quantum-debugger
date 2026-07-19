"""
Quantum Machine Learning (QML) Module
"""

# Core gates
from .gates.parameterized import ParameterizedGate, RXGate, RYGate, RZGate

# Algorithms
from .algorithms.vqe import VQE
from .algorithms.vqd import VQD
from .algorithms.qaoa import QAOA
from .algorithms.policy_gradient import QuantumPolicyGradient
from .algorithms.dqn import QuantumDQN
from .algorithms.actor_critic import QuantumActorCritic

# Advanced QML (data re-uploading, autoencoder, QCNN, VQC, ansatz analysis)
from .advanced import (
    DataReuploadingClassifier,
    QuantumAutoencoder,
    QCNN,
    VariationalQuantumClassifier,
    expressibility,
    entangling_capability,
    gradient_variance,
)

# Hamiltonians
from .hamiltonians.molecular import h2_hamiltonian

# Note: Ansatz and Optimizers should be imported directly from their submodules
# to avoid circular dependencies:
#   from quantum_debugger.qml.ansatz import real_amplitudes
#   from quantum_debugger.qml.optimizers import AdamOptimizer

__all__ = [
    # Gates
    "ParameterizedGate",
    "RXGate",
    "RYGate",
    "RZGate",
    # Algorithms
    "VQE",
    "VQD",
    "QAOA",
    "QuantumPolicyGradient",
    "QuantumDQN",
    "QuantumActorCritic",
    # Advanced QML
    "DataReuploadingClassifier",
    "QuantumAutoencoder",
    "QCNN",
    "VariationalQuantumClassifier",
    "expressibility",
    "entangling_capability",
    "gradient_variance",
    # Hamiltonians
    "h2_hamiltonian",
]
