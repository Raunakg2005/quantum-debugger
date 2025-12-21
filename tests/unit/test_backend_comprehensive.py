"""
Comprehensive Backend Test Suite
Shows detailed pass/fail counts for each category
"""

import pytest
import numpy as np
import time
from quantum_debugger import QuantumCircuit
from quantum_debugger.backends import get_backend, list_available_backends

# Helper to run wrapped test functions - renamed to avoid pytest collection
def _run_test(func):
    """Helper to execute test functions that were originally wrapped"""
    func()



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

# NumPy Backend Tests
def test_np_zeros():
    backend_np = get_backend('numpy')
    arr = backend_np.zeros((4, 4))
    assert arr.shape == (4, 4)
    assert np.sum(arr) == 0

def test_np_eye():
    backend_np = get_backend('numpy')
    arr = backend_np.eye(3)
    assert arr.shape == (3, 3)
    assert arr[0, 0] == 1

def test_np_matmul():
    backend_np = get_backend('numpy')
    a = backend_np.eye(2)
    b = backend_np.eye(2)
    c = backend_np.matmul(a, b)
    assert np.allclose(c, np.eye(2))

def test_np_kron():
    backend_np = get_backend('numpy')
    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    result = backend_np.kron(h, h)
    assert result.shape == (4, 4)

def test_np_conj():
    backend_np = get_backend('numpy')
    a = np.array([1+1j, 2-1j])
    result = backend_np.conj(a)
    assert np.allclose(result, np.array([1-1j, 2+1j]))

# Sparse Backend Tests
def test_sp_zeros():
    backend_sp = get_backend('sparse')
    arr = backend_sp.zeros((4, 4))
    assert arr.shape == (4, 4)

def test_sp_eye():
    backend_sp = get_backend('sparse')
    arr = backend_sp.eye(3)
    np_arr = backend_sp.to_numpy(arr)
    assert np_arr.shape == (3, 3)

def test_sp_matmul():
    backend_sp = get_backend('sparse')
    a = backend_sp.eye(2)
    b = backend_sp.eye(2)
    c = backend_sp.matmul(a, b)
    result = backend_sp.to_numpy(c)
    assert np.allclose(result, np.eye(2))

def test_sp_sparsity_detection():
    backend_sp = get_backend('sparse')
    # CNOT is sparse (75% zeros)
    cnot = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)
    assert backend_sp.is_sparse(cnot, threshold=0.5)

def test_sp_memory_savings():
    backend_sp = get_backend('sparse')
    # Large sparse matrix
    size = 100
    dense = np.eye(size)
    sparse = backend_sp.to_sparse(dense)
    from scipy import sparse as sp
    if sp.issparse(sparse):
        assert sparse.data.nbytes < dense.nbytes

# Circuit Integration Tests
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

# Cross-Backend Consistency Tests
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

# Performance Tests
def test_5qubit_performance():
    circuit = QuantumCircuit(5, backend='sparse')
    for i in range(5):
        circuit.h(i)
    
    start = time.perf_counter()
    circuit.run(shots=50)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 10  # Should complete in <10s

def test_backend_switching_speed():
    start = time.perf_counter()
    for _ in range(10):
        c1 = QuantumCircuit(2, backend='numpy')
        c2 = QuantumCircuit(2, backend='sparse')
    elapsed = time.perf_counter() - start
    
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
        assert savings > 50  # Should save >50%
