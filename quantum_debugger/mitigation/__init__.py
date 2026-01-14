"""
Quantum Error Mitigation Module

Implements techniques to reduce quantum noise without additional qubits:
- Zero-Noise Extrapolation (ZNE)
- Circuit Folding (noise amplification)
- Richardson/Polynomial/Exponential extrapolation

Author: QuantumDebugger Team
Version: 0.4.0
"""

from .zne import zero_noise_extrapolation
from .core.folder import CircuitFolder, global_fold, local_fold, adaptive_fold
from .core.extrapolator import Extrapolator

# Alias for convenience
apply_zne = zero_noise_extrapolation

__all__ = [
    "zero_noise_extrapolation",
    "apply_zne",  # Alias
    "CircuitFolder",
    "global_fold",
    "local_fold",
    "adaptive_fold",
    "Extrapolator",
]
