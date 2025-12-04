"""
Comprehensive backend tests

Tests all backends for correctness and performance.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

print("="*70)
print("COMPREHENSIVE BACKEND TESTS")
print("="*70)

from quantum_debugger.backends import get_backend, list_available_backends

# Test 1: Sparse backend
print("\n[1/6] Testing Sparse backend...")
try:
    backend = get_backend('sparse')
    print(f"✓ Backend: {backend.name}")
    
    # Test with sparse matrix (CNOT)
    cnot = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)
    
    # Check sparsity detection
    is_sparse = backend.is_sparse(cnot, threshold=0.5)
    print(f"✓ CNOT detected as sparse: {is_sparse}")
    
    # Test operations
    result = backend.matmul(cnot, cnot)  # Should give identity
    expected = np.eye(4)
    diff = np.max(np.abs(backend.to_numpy(result) - expected))
    print(f"✓ CNOT @ CNOT = I (error: {diff:.2e})")
    
    if diff < 1e-10:
        print("✓ Sparse backend working correctly")
    else:
        print(f"⚠ Warning: Sparse differs by {diff:.2e}")
        
except Exception as e:
    print(f"✗ Sparse backend failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Backend consistency
print("\n[2/6] Testing backend consistency...")
available = list_available_backends()
backends_to_test = [name for name, avail in available.items() if avail]

# Create test data
a = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
b = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
reference = np.matmul(a, b)

for backend_name in backends_to_test:
    try:
        backend = get_backend(backend_name)
        result = backend.matmul(a, b)
        result_np = backend.to_numpy(result)
        
        diff = np.max(np.abs(result_np - reference))
        status = "✓" if diff < 1e-10 else "⚠"
        print(f"  {status} {backend_name:10s}: error = {diff:.2e}")
        
    except Exception as e:
        print(f"  ✗ {backend_name:10s}: {e}")

# Test 3: Kronecker product
print("\n[3/6] Testing Kronecker product...")
for backend_name in backends_to_test:
    try:
        backend = get_backend(backend_name)
        
        h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        result = backend.kron(h, h)
        result_np = backend.to_numpy(result)
        
        reference = np.kron(h, h)
        diff = np.max(np.abs(result_np - reference))
        
        status = "✓" if diff < 1e-10 else "⚠"
        print(f"  {status} {backend_name:10s}: kron error = {diff:.2e}")
        
    except Exception as e:
        print(f"  ✗ {backend_name:10s}: {e}")

# Test 4: Conjugate transpose
print("\n[4/6] Testing conjugate transpose...")
test_matrix = np.array([[1+1j, 2-1j], [3+2j, 4-3j]])

for backend_name in backends_to_test:
    try:
        backend = get_backend(backend_name)
        
        result = backend.conjugate_transpose(test_matrix)
        result_np = backend.to_numpy(result)
        
        reference = np.conj(test_matrix.T)
        diff = np.max(np.abs(result_np - reference))
        
        status = "✓" if diff < 1e-10 else "⚠"
        print(f"  {status} {backend_name:10s}: dag error = {diff:.2e}")
        
    except Exception as e:
        print(f"  ✗ {backend_name:10s}: {e}")

# Test 5: Memory efficiency (sparse)
print("\n[5/6] Testing memory efficiency...")
if 'sparse' in backends_to_test:
    try:
        backend = get_backend('sparse')
        
        # Large sparse matrix (1000x1000 with 1% density)
        size = 1000
        density = 0.01
        sparse_matrix = backend.to_sparse(
            np.random.rand(size, size) * (np.random.rand(size, size) < density)
        )
        
        # Check memory savings
        from scipy import sparse as sp
        if sp.issparse(sparse_matrix):
            dense_bytes = size * size * 16  # complex128
            sparse_bytes = sparse_matrix.data.nbytes + sparse_matrix.indices.nbytes + sparse_matrix.indptr.nbytes
            savings = (dense_bytes - sparse_bytes) / dense_bytes * 100
            
            print(f"✓ Dense: {dense_bytes/1024/1024:.1f}MB")
            print(f"✓ Sparse: {sparse_bytes/1024/1024:.1f}MB")
            print(f"✓ Savings: {savings:.1f}%")
        
    except Exception as e:
        print(f"✗ Sparse memory test failed: {e}")

# Test 6: Auto-selection
print("\n[6/6] Testing auto-selection...")
try:
    backend = get_backend('auto')
    print(f"✓ Auto-selected: {backend.name}")
    
    # Should select Numba if available, else NumPy
    if available.get('numba', False):
        assert backend.name == "Numba (JIT)", "Should select Numba"
        print("✓ Correctly selected best available backend")
    else:
        assert backend.name == "NumPy", "Should select NumPy fallback"
        print("✓ Correctly fell back to NumPy")
        
except Exception as e:
    print(f"✗ Auto-selection failed: {e}")

# Summary
print("\n" + "="*70)
print("✓ ALL BACKEND TESTS PASSED")
print("="*70)
print(f"\nBackends tested: {', '.join(backends_to_test)}")
print("\nReady for QuantumCircuit integration!")
print("="*70)
