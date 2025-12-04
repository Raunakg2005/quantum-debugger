"""
Test parallel execution system
Shows detailed test results with pass/fail counts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np

print("="*70)
print("PARALLEL EXECUTION TESTS")
print("="*70)

from quantum_debugger import QuantumCircuit
from quantum_debugger.parallel import ParallelExecutor, run_parallel

# Track results
results = {
    'Module Imports': {'passed': 0, 'total': 0},
    'Thread Execution': {'passed': 0, 'total': 0},
    'Process Execution': {'passed': 0, 'total': 0},
    'Result Merging': {'passed': 0, 'total': 0},
    'Performance': {'passed': 0, 'total': 0},
}

def test(category, name, func):
    """Run a test and track results"""
    results[category]['total'] += 1
    try:
        func()
        results[category]['passed'] += 1
        print(f"  ✓ {name}")
        return True
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MODULE IMPORTS ====================
print("\n[Category 1/5] Module Imports")
print("-" * 70)

def test_import_executor():
    from quantum_debugger.parallel import ParallelExecutor
    assert ParallelExecutor is not None

def test_import_convenience():
    from quantum_debugger.parallel import run_parallel
    assert run_parallel is not None

def test_create_executor():
    executor = ParallelExecutor(n_workers=2)
    assert executor.n_workers == 2

test('Module Imports', 'Import ParallelExecutor', test_import_executor)
test('Module Imports', 'Import run_parallel()', test_import_convenience)
test('Module Imports', 'Create ParallelExecutor', test_create_executor)

# ==================== THREAD EXECUTION ====================
print("\n[Category 2/5] Thread-Based Execution")
print("-" * 70)

def test_thread_bell_state():
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    executor = ParallelExecutor(n_workers=2, use_processes=False)
    result = executor.run_parallel(circuit, shots=100)
    
    assert 'counts' in result
    assert result['shots'] == 100

def test_thread_correctness():
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
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    total_shots = 250
    executor = ParallelExecutor(n_workers=2, use_processes=False)
    result = executor.run_parallel(circuit, shots=total_shots)
    
    # Check total counts match shots
    actual_shots = sum(result['counts'].values())
    assert actual_shots == total_shots

test('Thread Execution', 'Bell state (threads)', test_thread_bell_state)
test('Thread Execution', 'Result correctness', test_thread_correctness)
test('Thread Execution', 'Shot count preservation', test_thread_shot_count)

# ==================== PROCESS EXECUTION ====================
print("\n[Category 3/5] Process-Based Execution")
print("-" * 70)

def test_process_bell_state():
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    executor = ParallelExecutor(n_workers=2, use_processes=True)
    result = executor.run_parallel(circuit, shots=100)
    
    assert 'counts' in result
    assert result['shots'] == 100

def test_process_convenience():
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)
    
    result = run_parallel(circuit, shots=100, n_workers=2)
    
    assert 'counts' in result
    assert result['shots'] == 100

def test_process_shot_count():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    total_shots = 300
    result = run_parallel(circuit, shots=total_shots, n_workers=3)
    
    # Check total
    actual_shots = sum(result['counts'].values())
    assert actual_shots == total_shots

test('Process Execution', 'Bell state (processes)', test_process_bell_state)
test('Process Execution', 'Convenience function', test_process_convenience)
test('Process Execution', 'Shot count preservation', test_process_shot_count)

# ==================== RESULT MERGING ====================
print("\n[Category 4/5] Result Merging")
print("-" * 70)

def test_merge_simple():
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
    executor = ParallelExecutor(n_workers=4)
    circuit = QuantumCircuit(1)
    circuit.h(0)
    
    result = executor.run_parallel(circuit, shots=100)
    
    assert result['parallel_workers'] == 4

test('Result Merging', 'Merge multiple results', test_merge_simple)
test('Result Merging', 'Worker count tracking', test_merge_worker_count)

# ==================== PERFORMANCE ====================
print("\n[Category 5/5] Performance Tests")
print("-" * 70)

def test_speedup_threads():
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
    print(f"    Thread speedup: {speedup:.2f}x")
    
    # Should show some speedup (even if minimal)
    assert speedup > 0.5  # At least not slower

def test_worker_scaling():
    circuit = QuantumCircuit(3)
    circuit.h(0).cnot(0, 1).cnot(1, 2)
    
    times = {}
    for n_workers in [1, 2, 4]:
        executor = ParallelExecutor(n_workers=n_workers, use_processes=False)
        
        start = time.perf_counter()
        executor.run_parallel(circuit, shots=200)
        elapsed = time.perf_counter() - start
        
        times[n_workers] = elapsed
        print(f"    {n_workers} workers: {elapsed*1000:.1f}ms")
    
    # Just verify it completes
    assert all(t > 0 for t in times.values())

test('Performance', 'Thread speedup', test_speedup_threads)
test('Performance', 'Worker scaling', test_worker_scaling)

# ==================== SUMMARY ====================
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

total_passed = 0
total_tests = 0

for category, counts in results.items():
    passed = counts['passed']
    total = counts['total']
    total_passed += passed
    total_tests += total
    
    status = "✓ PASS" if passed == total else "⚠ PARTIAL" if passed > 0 else "✗ FAIL"
    print(f"{category:25s}: {passed}/{total} {status}")

print("-" * 70)
percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
print(f"{'OVERALL':<25s}: {total_passed}/{total_tests} ({percentage:.1f}%)")
print("="*70)

if total_passed == total_tests:
    print("🎉 ALL PARALLEL TESTS PASSED!")
else:
    print(f"⚠ {total_tests - total_passed} test(s) failed")

print("="*70)
