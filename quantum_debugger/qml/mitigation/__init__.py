"""
Error Mitigation Module

Advanced error mitigation techniques for quantum machine learning,
including PEC and CDR for production-ready quantum ML on noisy hardware.
"""

from .pec import PEC, apply_pec
from .cdr import CDR, apply_cdr
from .noise_models import (
    NoiseModel,
    DepolarizingNoise,
    AmplitudeDampingNoise,
    PhaseDampingNoise,
    CompositeNoise
)
from .error_characterization import (
    characterize_readout_error,
    estimate_gate_fidelity,
    measure_gate_errors
)

__all__ = [
    # PEC
    'PEC',
    'apply_pec',
    
    # CDR
    'CDR',
    'apply_cdr',
    
    # Noise models
    'NoiseModel',
    'DepolarizingNoise',
    'AmplitudeDampingNoise',
    'PhaseDampingNoise',
    'CompositeNoise',
    
    # Error characterization
    'characterize_readout_error',
    'estimate_gate_fidelity',
    'measure_gate_errors'
]
