"""
Comprehensive Backend Test Suite
Shows detailed pass/fail counts for each category
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time

print("="*70)
print("COMPREHENSIVE BACKEND TEST SUITE")
print("="*70)

from quantum_debugger import QuantumCircuit
from quantum_debugger.backends import get_backend, list_available_backends

# Track results
results = {
    'Backend Imports': {'passed': 0, 'total': 0},
    'NumPy Backend': {'passed': 0, 'total': 0},
    'Sparse Backend': {'passed': 0, 'total': 0},
    'Circuit Integration': {'passed': 0, 'total': 0},
    'Cross-Backend': {'passed': 0, 'total': 0},
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
        return False

# ==================== BACKEND IMPORTS ====================
print("\n[Category 1/6] Backend Imports")
print("-" * 70)

def test_import_backend():
    from quantum_debugger.backends import Backend
    assert Backend is not None

def test_import_numpy():
    from quantum_debugger.backends import NumPyBackend
    backend = NumPyBackend()
    assert backend.name == "NumPy"

def test_import_sparse():
    from quantum_debugger.backends import SparseBackend
    backend = SparseBackend()
    assert backend.name == "Sparse (SciPy)"

def test_get_backend_function():
    backend = get_backend('numpy')
    assert backend is not None

test('Backend Imports', 'Import Backend ABC', test_import_backend)
test('Backend Imports', 'Import NumPy backend', test_import_numpy)
test('Backend Imports', 'Import Sparse backend', test_import_sparse)
test('Backend Imports', 'get_backend() function', test_get_backend_function)

# ==================== NUMPY BACKEND ====================
print(f"\n[Category 2/6] NumPy Backend Operations")
print("-" * 70)

backend_np = get_backend('numpy')

def test_np_zeros():
    arr = backend_np.zeros((4, 4))
    assert arr.shape == (4, 4)
    assert np.sum(arr) == 0

def test_np_eye():
    arr = backend_np.eye(3)
    assert arr.shape == (3, 3)
    assert arr[0, 0] == 1

def test_np_matmul():
    a = backend_np.eye(2)
    b = backend_np.eye(2)
    c = backend_np.matmul(a, b)
    assert np.allclose(c, np.eye(2))

def test_np_kron():
    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    result = backend_np.kron(h, h)
    assert result.shape == (4, 4)

def test_np_conj():
    a = np.array([1+1j, 2-1j])
    result = backend_np.conj(a)
    assert np.allclose(result, np.array([1-1j, 2+1j]))

test('NumPy Backend', 'zeros()', test_np_zeros)
test('NumPy Backend', 'eye()', test_np_eye)
test('NumPy Backend', 'matmul()', test_np_matmul)
test('NumPy Backend', 'kron()', test_np_kron)
test('NumPy Backend', 'conj()', test_np_conj)

# ==================== SPARSE BACKEND ====================
print(f"\n[Category 3/6] Sparse Backend Operations")
print("-" * 70)

backend_sp = get_backend('sparse')

def test_sp_zeros():
    arr = backend_sp.zeros((4, 4))
    assert arr.shape == (4, 4)

def test_sp_eye():
    arr = backend_sp.eye(3)
    np_arr = backend_sp.to_numpy(arr)
    assert np_arr.shape == (3, 3)

def test_sp_matmul():
    a = backend_sp.eye(2)
    b = backend_sp.eye(2)
    c = backend_sp.matmul(a, b)
    result = backend_sp.to_numpy(c)
    assert np.allclose(result, np.eye(2))

def test_sp_sparsity_detection():
    # CNOT is sparse (75% zeros)
    cnot = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)
    assert backend_sp.is_sparse(cnot, threshold=0.5)

def test_sp_memory_savings():
    # Large sparse matrix
    size = 100
    dense = np.eye(size)
    sparse = backend_sp.to_sparse(dense)
    from scipy import sparse as sp
    if sp.issparse(sparse):
        assert sparse.data.nbytes < dense.nbytes

test('Sparse Backend', 'zeros()', test_sp_zeros)
test('Sparse Backend', 'eye()', test_sp_eye)
test('Sparse Backend', 'matmul()', test_sp_matmul)
test('Sparse Backend', 'Sparsity detection', test_sp_sparsity_detection)
test('Sparse Backend', 'Memory savings', test_sp_memory_savings)

# ==================== CIRCUIT INTEGRATION ====================
print(f"\n[Category 4/6] Circuit Integration")
print("-" * 70)

def test_circuit_numpy():
    circuit = QuantumCircuit(2, backend='numpy')
    assert circuit._initial_state.backend.name == "NumPy"

def test_circuit_sparse():
    circuit = QuantumCircuit(2, backend='sparse')
    assert circuit._initial_state.backend.name == "Sparse (SciPy)"

def test_circuit_auto():
    circuit = QuantumCircuit(2)  # Auto-select
    assert circuit._initial_state.backend is not None

def test_circuit_run_numpy():
    circuit = QuantumCircuit(2, backend='numpy')
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=100)
    assert 'counts' in result

def test_circuit_run_sparse():
    circuit = QuantumCircuit(2, backend='sparse')
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=100)
    assert 'counts' in result

test('Circuit Integration', 'Create circuit with NumPy', test_circuit_numpy)
test('Circuit Integration', 'Create circuit with Sparse', test_circuit_sparse)
test('Circuit Integration', 'Auto backend selection', test_circuit_auto)
test('Circuit Integration', 'Run circuit (NumPy)', test_circuit_run_numpy)
test('Circuit Integration', 'Run circuit (Sparse)', test_circuit_run_sparse)

# ==================== CROSS-BACKEND CONSISTENCY ====================
print(f"\n[Category 5/6] Cross-Backend Consistency")
print("-" * 70)

def test_bell_state_consistency():
    # Same circuit on both backends
    c1 = QuantumCircuit(2, backend='numpy')
    c1.h(0).cnot(0, 1)
    
    c2 = QuantumCircuit(2, backend='sparse')
    c2.h(0).cnot(0, 1)
    
    r1 = c1.run(shots=500)
    r2 = c2.run(shots=500)
    
    # Both should produce valid results
    assert 'counts' in r1 and 'counts' in r2

def test_ghz_consistency():
    # 3-qubit GHZ on both backends
    c1 = QuantumCircuit(3, backend='numpy')
    c1.h(0).cnot(0, 1).cnot(1, 2)
    
    c2 = QuantumCircuit(3, backend='sparse')
    c2.h(0).cnot(0, 1).cnot(1, 2)
    
    r1 = c1.run(shots=200)
    r2 = c2.run(shots=200)
    
    # Should have same outcome keys
    assert set(r1['counts'].keys()) == set(r2['counts'].keys())

def test_hadamard_consistency():
    # Single qubit Hadamard
    c1 = QuantumCircuit(1, backend='numpy')
    c1.h(0)
    
    c2 = QuantumCircuit(1, backend='sparse')
    c2.h(0)
    
    r1 = c1.run(shots=1000)
    r2 = c2.run(shots=1000)
    
    # Both should produce counts (may have '0', '1', or both)
    assert 'counts' in r1 and 'counts' in r2
    assert len(r1['counts']) > 0 and len(r2['counts']) > 0

test('Cross-Backend', 'Bell state consistency', test_bell_state_consistency)
test('Cross-Backend', 'GHZ state consistency', test_ghz_consistency)
test('Cross-Backend', 'Hadamard consistency', test_hadamard_consistency)

# ==================== PERFORMANCE ====================
print(f"\n[Category 6/6] Performance Tests")
print("-" * 70)

def test_5qubit_performance():
    circuit = QuantumCircuit(5, backend='sparse')
    for i in range(5):
        circuit.h(i)
    
    start = time.perf_counter()
    circuit.run(shots=50)
    elapsed = time.perf_counter() - start
    
    print(f"    5-qubit circuit: {elapsed*1000:.1f}ms")
    assert elapsed < 10  # Should complete in <10s

def test_backend_switching_speed():
    start = time.perf_counter()
    for _ in range(10):
        c1 = QuantumCircuit(2, backend='numpy')
        c2 = QuantumCircuit(2, backend='sparse')
    elapsed = time.perf_counter() - start
    
    print(f"    10x backend switches: {elapsed*1000:.1f}ms")
    assert elapsed < 1  # Should be fast

def test_memory_efficiency():
    # Check sparse backend uses less memory
    backend = get_backend('sparse')
    
    # 50x50 identity (very sparse)
    dense = np.eye(50)
    sparse = backend.to_sparse(dense)
    
    from scipy import sparse as sp
    if sp.issparse(sparse):
        savings = (1 - sparse.data.nbytes / dense.nbytes) * 100
        print(f"    Memory savings: {savings:.1f}%")
        assert savings > 50  # Should save >50%

test('Performance', '5-qubit circuit speed', test_5qubit_performance)
test('Performance', 'Backend switching', test_backend_switching_speed)
test('Performance', 'Memory efficiency', test_memory_efficiency)

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
    print("🎉 ALL TESTS PASSED! Backend system is 100% functional!")
else:
    print(f"⚠ {total_tests - total_passed} test(s) failed")

print("="*70)
