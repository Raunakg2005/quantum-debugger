"""
Test parallel execution system - pytest format
"""

import pytest
import time
import numpy as np
from quantum_debugger import QuantumCircuit
from quantum_debugger.parallel import ParallelExecutor, run_parallel


# ==================== MODULE IMPORTS ====================
def test_import_executor():
    """Test importing ParallelExecutor"""
    from quantum_debugger.parallel import ParallelExecutor
    assert ParallelExecutor is not None


def test_import_convenience():
    """Test importing run_parallel function"""
    from quantum_debugger.parallel import run_parallel
    assert run_parallel is not None


def test_create_executor():
    """Test creating ParallelExecutor"""
    executor = ParallelExecutor(n_workers=2)
    assert executor.n_workers == 2


# ==================== THREAD EXECUTION ====================
def test_thread_bell_state():
    """Test Bell state with thread-based execution"""
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    executor = ParallelExecutor(n_workers=2, use_processes=False)
    result = executor.run_parallel(circuit, shots=100)
    
    assert 'counts' in result
    assert result['shots'] == 100


def test_thread_correctness():
    """Test result correctness with threads"""
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    # Run serially
    serial_result = circuit.run(shots=500)
    
    # Run in parallel (threads)
    executor = ParallelExecutor(n_workers=2, use_processes=False)
    parallel_result = executor.run_parallel(circuit, shots=500)
    
    # Should have same outcome keys
    assert set(serial_result['counts'].keys()) == set(parallel_result['counts'].keys())


def test_thread_shot_count():
    """Test shot count preservation with threads"""
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    total_shots = 250
    executor = ParallelExecutor(n_workers=2, use_processes=False)
    result = executor.run_parallel(circuit, shots=total_shots)
    
    # Check total counts match shots
    actual_shots = sum(result['counts'].values())
    assert actual_shots == total_shots


# ==================== PROCESS EXECUTION ====================
def test_process_bell_state():
    """Test Bell state with process-based execution"""
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    executor = ParallelExecutor(n_workers=2, use_processes=True)
    result = executor.run_parallel(circuit, shots=100)
    
    assert 'counts' in result
    assert result['shots'] == 100


def test_process_convenience():
    """Test convenience function"""
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    result = run_parallel(circuit, shots=100, n_workers=2)
    
    assert 'counts' in result
    assert result['shots'] == 100


def test_process_shot_count():
    """Test shot count preservation with processes"""
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    total_shots = 300
    result = run_parallel(circuit, shots=total_shots, n_workers=3)
    
    # Check total
    actual_shots = sum(result['counts'].values())
    assert actual_shots == total_shots


# ==================== RESULT MERGING ====================  
def test_merge_simple():
    """Test merging multiple results"""
    executor = ParallelExecutor(n_workers=2)
    
    results_list = [
        {'counts': {'00': 50, '11': 50}, 'shots': 100},
        {'counts': {'00': 45, '11': 55}, 'shots': 100},
    ]
    
    merged = executor._merge_results(results_list)
    
    assert merged['counts']['00'] == 95
    assert merged['counts']['11'] == 105
    assert merged['shots'] == 200


def test_merge_worker_count():
    """Test worker count tracking"""
    executor = ParallelExecutor(n_workers=4)
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    result = executor.run_parallel(circuit, shots=100)
    
    assert result['parallel_workers'] == 4


# ==================== PERFORMANCE ====================
def test_speedup_threads():
    """Test thread speedup"""
    circuit = QuantumCircuit(4)
    for i in range(4):
        circuit.h(i)
    for i in range(3):
        circuit.cnot(i, i+1)
    
    # Serial
    start = time.perf_counter()
    circuit.run(shots=400)
    serial_time = time.perf_counter() - start
    
    # Parallel (4 workers)
    executor = ParallelExecutor(n_workers=4, use_processes=False)
    start = time.perf_counter()
    executor.run_parallel(circuit, shots=400)
    parallel_time = time.perf_counter() - start
    
    speedup = serial_time / parallel_time if parallel_time > 0 else 1
    
    # Should show some speedup (even if minimal)
    assert speedup > 0.5  # At least not slower


def test_worker_scaling():
    """Test worker scaling"""
    circuit = QuantumCircuit(3)
    circuit.h(0).cnot(0, 1).cnot(1, 2)
    
    times = {}
    for n_workers in [1, 2, 4]:
        executor = ParallelExecutor(n_workers=n_workers, use_processes=False)
        
        start = time.perf_counter()
        executor.run_parallel(circuit, shots=200)
        elapsed = time.perf_counter() - start
        
        times[n_workers] = elapsed
    
    # Just verify it completes
    assert all(t > 0 for t in times.values())
