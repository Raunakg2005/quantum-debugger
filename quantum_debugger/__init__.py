"""
QuantumDebugger - Interactive debugging and profiling for quantum circuits

A powerful Python library for step-through debugging, state inspection,
and performance analysis of quantum circuits.
"""

__version__ = "0.2.2"
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

# Optional integrations
try:
    from .integrations import QiskitAdapter
    __all_integrations__ = ['QiskitAdapter']
except ImportError:
    __all_integrations__ = []

__all__ = [
    'QuantumCircuit',
    'QuantumState',
    'GateLibrary',
    'QuantumDebugger',
    'Breakpoint',
    'BreakpointManager',
    'StateInspector',
    'CircuitProfiler',
    'CircuitMetrics',
    'StateVisualizer',
    'BlochSphere',
] + __all_integrations__
