"""
Circuit Optimization Benchmarking

Measure performance improvements from circuit optimization.
"""

import time
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def benchmark_optimization(
    circuit_gates: List,
    optimization_level: int = 2
) -> Dict:
    """
    Benchmark circuit optimization performance.
    
    Args:
        circuit_gates: Circuit to optimize
        optimization_level: 0-3
        
    Returns:
        Optimization benchmark results
        
    Examples:
        >>> gates = [('h', 0), ('h', 0), ('x', 1)]
        >>> results = benchmark_optimization(gates, optimization_level=2)
        >>> print(f"Gate reduction: {results['reduction_percentage']:.1f}%")
        >>> print(f"Optimization time: {results['optimization_time']:.4f}s")
    """
    from quantum_debugger.optimization import compile_circuit, GateOptimizer
    
    original_count = len(circuit_gates)
    
    # Benchmark optimization time
    start_time = time.time()
    optimized = compile_circuit(circuit_gates, optimization_level=optimization_level)
    optimization_time = time.time() - start_time
    
    optimized_count = len(optimized)
    reduction = original_count - optimized_count
    reduction_pct = (reduction / original_count * 100) if original_count > 0 else 0
    
    return {
        'original_gates': original_count,
        'optimized_gates': optimized_count,
        'gates_removed': reduction,
        'reduction_percentage': reduction_pct,
        'optimization_level': optimization_level,
        'optimization_time': optimization_time
    }


def benchmark_transpilation(
    circuit_gates: List,
    topology: Dict
) -> Dict:
    """
    Benchmark circuit transpilation for hardware.
    
    Args:
        circuit_gates: Circuit to transpile
        topology: Hardware topology
        
    Returns:
        Transpilation benchmark results
    """
    from quantum_debugger.optimization import Transpiler
    
    transpiler = Transpiler(topology)
    
    # Benchmark transpilation
    start_time = time.time()
    transpiled = transpiler.transpile(circuit_gates)
    transpile_time = time.time() - start_time
    
    return {
        'original_gates': len(circuit_gates),
        'transpiled_gates': len(transpiled),
        'overhead': len(transpiled) - len(circuit_gates),
        'transpile_time': transpile_time,
        'topology': topology
    }


def measure_speedup(
    n_qubits_range: List[int],
    optimization_levels: List[int] = [0, 1, 2, 3]
) -> Dict:
    """
    Measure optimization speedup across different circuit sizes.
    
    Args:
        n_qubits_range: Range of qubit counts to test
        optimization_levels: Levels to benchmark
        
    Returns:
        Speedup analysis results
    """
    results = {}
    
    for n_qubits in n_qubits_range:
        # Generate test circuit
        gates = []
        for _ in range(n_qubits * 5):  # 5 gates per qubit
            gates.append(('h', np.random.randint(n_qubits)))
            if np.random.rand() > 0.5:
                gates.append(('h', np.random.randint(n_qubits)))  # Create cancellations
        
        level_results = {}
        
        for level in optimization_levels:
            benchmark = benchmark_optimization(gates, optimization_level=level)
            level_results[f'level_{level}'] = benchmark
        
        results[f'{n_qubits}_qubits'] = level_results
    
    return results


def optimization_comparison_suite() -> Dict:
    """
    Run comprehensive optimization comparison.
    
    Returns:
        Complete optimization benchmark suite results
    """
    # Test circuits with different characteristics
    test_cases = {
        'cancellations': [('h', 0), ('h', 0), ('x', 1), ('x', 1)],
        'rotations': [('rz', 0, 0.5), ('rz', 0, 0.3), ('ry', 1, 0.2)],
        'mixed': [
            ('h', 0), ('h', 0),
            ('rz', 1, 0.5), ('rz', 1, 0.3),
            ('cnot', (0, 1)),
            ('x', 2), ('x', 2)
        ]
    }
    
    results = {}
    
    for name, circuit in test_cases.items():
        logger.info(f"Benchmarking {name} circuit")
        results[name] = {}
        
        for level in [0, 1, 2, 3]:
            bench = benchmark_optimization(circuit, optimization_level=level)
            results[name][f'level_{level}'] = bench
    
    return results
