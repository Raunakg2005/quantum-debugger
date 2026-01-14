"""
Scalability Analysis

Analyze how quantum algorithms scale with problem size.
"""

import time
import numpy as np
from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)


def scalability_analysis(
    n_qubits_range: List[int],
    algorithm: str = 'qnn',
    epochs: int = 5
) -> Dict:
    """
    Analyze algorithm scalability.
    
    Args:
        n_qubits_range: Range of qubit counts [2, 4, 6, ...]
        algorithm: 'qnn', 'qsvm', or 'vqe'
        epochs: Training epochs
        
    Returns:
        Scalability analysis results
        
    Examples:
        >>> results = scalability_analysis([2, 4, 6], algorithm='qnn')
        >>> for n in [2, 4, 6]:
        ...     print(f"{n} qubits: {results[n]['time']:.2f}s")
    """
    from quantum_debugger.qml.qnn import QuantumNeuralNetwork
    
    results = {}
    
    for n_qubits in n_qubits_range:
        logger.info(f"Testing {algorithm} with {n_qubits} qubits")
        
        # Generate data
        dataset_size = 50
        X = np.random.randn(dataset_size, n_qubits)
        y = np.random.randint(0, 2, dataset_size)
        
        if algorithm == 'qnn':
            model = QuantumNeuralNetwork(n_qubits=n_qubits)
            model.compile(optimizer='adam', loss='mse')
            
            start_time = time.time()
            model.fit(X, y, epochs=epochs, verbose=0)
            elapsed_time = time.time() - start_time
            
            results[n_qubits] = {
                'time': elapsed_time,
                'time_per_epoch': elapsed_time / epochs,
                'n_parameters': model._parameters.size if model._parameters is not None else 0
            }
        
        elif algorithm == 'qsvm':
            from quantum_debugger.qml.kernels import QSVM
            
            model = QSVM(n_qubits=n_qubits)
            
            start_time = time.time()
            model.fit(X, y)
            elapsed_time = time.time() - start_time
            
            results[n_qubits] = {
                'time': elapsed_time,
                'kernel_evaluations': dataset_size * dataset_size
            }
    
    # Calculate scaling factors
    if len(results) > 1:
        qubits_list = sorted(results.keys())
        for i in range(1, len(qubits_list)):
            prev_q = qubits_list[i-1]
            curr_q = qubits_list[i]
            
            time_ratio = results[curr_q]['time'] / results[prev_q]['time']
            qubit_ratio = curr_q / prev_q
            
            results[curr_q]['scaling_factor'] = time_ratio
            results[curr_q]['expected_exponential'] = 2 ** (curr_q - prev_q)
    
    return results


def parallel_benchmark(
    n_workers: int = 4,
    task_count: int = 10
) -> Dict:
    """
    Benchmark parallel execution capability.
    
    Args:
        n_workers: Number of parallel workers
        task_count: Number of tasks to execute
        
    Returns:
        Parallel performance results
    """
    # Simple benchmark: measure speedup from parallelization
    from concurrent.futures import ThreadPoolExecutor
    
    def dummy_task(task_id):
        """Simulate quantum circuit execution"""
        time.sleep(0.1)  # Simulate work
        return task_id
    
    # Sequential execution
    start_time = time.time()
    for i in range(task_count):
        dummy_task(i)
    sequential_time = time.time() - start_time
    
    # Parallel execution
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        list(executor.map(dummy_task, range(task_count)))
    parallel_time = time.time() - start_time
    
    speedup = sequential_time / parallel_time
    efficiency = speedup / n_workers
    
    return {
        'n_workers': n_workers,
        'task_count': task_count,
        'sequential_time': sequential_time,
        'parallel_time': parallel_time,
        'speedup': speedup,
        'efficiency': efficiency
    }


def memory_profiling(
    n_qubits_range: List[int]
) -> Dict:
    """
    Profile memory usage for different qubit counts.
    
    Args:
        n_qubits_range: Qubit counts to test
        
    Returns:
        Memory usage results
    """
    import sys
    from quantum_debugger.qml.qnn import QuantumNeuralNetwork
    
    results = {}
    
    for n_qubits in n_qubits_range:
        qnn = QuantumNeuralNetwork(n_qubits=n_qubits)
        qnn.compile(optimizer='adam', loss='mse')
        
        # Estimate memory (rough approximation)
        state_vector_size = 2 ** n_qubits * 16  # Complex128 = 16 bytes
        
        # Check for parameters
        parameter_size = 0
        if hasattr(qnn, '_parameters') and qnn._parameters is not None:
            parameter_size = sys.getsizeof(qnn._parameters)
        elif hasattr(qnn, 'weights') and qnn.weights is not None:
            parameter_size = sys.getsizeof(qnn.weights)
        
        results[n_qubits] = {
            'state_vector_bytes': state_vector_size,
            'state_vector_mb': state_vector_size / (1024 * 1024),
            'parameters_bytes': parameter_size,
            'total_mb': (state_vector_size + parameter_size) / (1024 * 1024)
        }
    
    return results
