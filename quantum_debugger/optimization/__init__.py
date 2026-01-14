"""
Circuit Optimization Module

Quantum circuit optimization including gate reduction, compilation,
and transpilation for efficient quantum machine learning execution.
"""

from .gate_reduction import GateOptimizer, optimize_circuit
from .circuit_compiler import CircuitCompiler, compile_circuit
from .transpiler import Transpiler, transpile_circuit
from .optimization_passes import (
    depth_reduction_pass,
    gate_count_reduction_pass,
    cancellation_pass,
    merge_rotations_pass
)

__all__ = [
    # Gate optimization
    'GateOptimizer',
    'optimize_circuit',
    
    # Compilation
    'CircuitCompiler',
    'compile_circuit',
    
    # Transpilation
    'Transpiler',
    'transpile_circuit',
    
    # Optimization passes
    'depth_reduction_pass',
    'gate_count_reduction_pass',
    'cancellation_pass',
    'merge_rotations_pass'
]
