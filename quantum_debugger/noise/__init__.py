"""
Quantum noise simulation module
"""

from quantum_debugger.noise.noise_models import (
    NoiseModel,
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation
)

from quantum_debugger.noise.noise_helpers import QuantumState

from quantum_debugger.noise.composite_noise import CompositeNoise

from quantum_debugger.noise.hardware_profiles import (
    HardwareProfile,
    # Existing 2025 profiles
    IBM_PERTH_2025,
    GOOGLE_SYCAMORE_2025,
    IONQ_ARIA_2025,
    RIGETTI_ASPEN_2025,
    # AWS Braket
    IONQ_HARMONY_AWS,
    RIGETTI_ASPEN_M3_AWS,
    # Azure Quantum
    QUANTINUUM_H1_AZURE,
    HONEYWELL_H2_AZURE,
    # 2025 Updates
    IBM_HERON_2025,
    GOOGLE_WILLOW_2025,
    IONQ_FORTE_2025,
    # Utilities
    HARDWARE_PROFILES,
    get_hardware_profile,
    list_hardware_profiles
)

__all__ = [
    # Noise models
    'NoiseModel',
    'DepolarizingNoise',
    'AmplitudeDamping',
    'PhaseDamping',
    'ThermalRelaxation',
    'CompositeNoise',
    # State wrapper
    'QuantumState',
    # Hardware profiles
    'HardwareProfile',
    'IBM_PERTH_2025',
    'GOOGLE_SYCAMORE_2025',
    'IONQ_ARIA_2025',
    'RIGETTI_ASPEN_2025',
    # AWS Braket
    'IONQ_HARMONY_AWS',
    'RIGETTI_ASPEN_M3_AWS',
    # Azure Quantum
    'QUANTINUUM_H1_AZURE',
    'HONEYWELL_H2_AZURE',
    # 2025 Updates
    'IBM_HERON_2025',
    'GOOGLE_WILLOW_2025',
    'IONQ_FORTE_2025',
    # Utilities
    'HARDWARE_PROFILES',
    'get_hardware_profile',
    'list_hardware_profiles',
]
