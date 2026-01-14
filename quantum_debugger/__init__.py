"""
QuantumDebugger - Interactive Quantum Circuit Debugger and Simulator

A comprehensive Python library for quantum circuit debugging, profiling,
and simulation with realistic noise models and error mitigation.

Features:
- Step-through circuit debugging
- State inspection and visualization
- Realistic noise simulation (v0.3.0)
- Zero-noise extrapolation (v0.4.0)
- Qiskit integration
- Hardware profile support

Version: 0.4.0-dev
"""

__version__ = "0.4.2"
__author__ = "warlord9004"
__license__ = "MIT"

from .core.circuit import QuantumCircuit
from .core.quantum_state import QuantumState
from .core.gates import GateLibrary
from .debugger.debugger import QuantumDebugger
from .debugger.breakpoints import Breakpoint, BreakpointManager
from .debugger.inspector import StateInspector
from .profiler.profiler import CircuitProfiler
from .profiler.metrics import CircuitMetrics
from .visualization.state_viz import StateVisualizer
from .visualization.bloch_sphere import BlochSphere

# Noise simulation (v0.3.0)
from .noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation,
    CompositeNoise,
    IBM_PERTH_2025,
    GOOGLE_SYCAMORE_2025,
    IONQ_ARIA_2025,
    RIGETTI_ASPEN_2025,
)

# Error mitigation (v0.4.0)
from .mitigation import (
    zero_noise_extrapolation,
    global_fold,
    local_fold,
    adaptive_fold,
)

# Optional integrations
try:
    from .integrations import QiskitAdapter

    __all_integrations__ = ["QiskitAdapter"]
except ImportError:
    __all_integrations__ = []

__all__ = [
    # Core
    "QuantumCircuit",
    "QuantumState",
    "GateLibrary",
    "QuantumDebugger",
    "Breakpoint",
    "BreakpointManager",
    "StateInspector",
    "CircuitProfiler",
    "CircuitMetrics",
    "StateVisualizer",
    "BlochSphere",
    # Noise Models (v0.3.0)
    "DepolarizingNoise",
    "AmplitudeDamping",
    "PhaseDamping",
    "ThermalRelaxation",
    "CompositeNoise",
    # Hardware Profiles
    "IBM_PERTH_2025",
    "GOOGLE_SYCAMORE_2025",
    "IONQ_ARIA_2025",
    "RIGETTI_ASPEN_2025",
    # Error Mitigation (v0.4.0)
    "zero_noise_extrapolation",
    "global_fold",
    "local_fold",
    "adaptive_fold",
] + __all_integrations__
