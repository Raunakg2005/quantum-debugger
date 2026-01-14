"""
Comprehensive backend tests

Tests all backends for correctness and performance.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger.backends import get_backend, list_available_backends


def test_sparse_backend():
    """Test Sparse backend operations"""
    backend = get_backend("sparse")
    assert backend.name == "Sparse (SciPy)"

    # Test with sparse matrix (CNOT)
    cnot = np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
    )

    # Check sparsity detection
    is_sparse = backend.is_sparse(cnot, threshold=0.5)
    assert is_sparse

    # Test operations - CNOT @ CNOT = I
    result = backend.matmul(cnot, cnot)
    expected = np.eye(4)
    diff = np.max(np.abs(backend.to_numpy(result) - expected))
    assert diff < 1e-10


def test_backend_consistency():
    """Test backend consistency across all available backends"""
    available = list_available_backends()
    backends_to_test = [name for name, avail in available.items() if avail]

    # Create test data
    a = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
    b = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
    reference = np.matmul(a, b)

    for backend_name in backends_to_test:
        backend = get_backend(backend_name)
        result = backend.matmul(a, b)
        result_np = backend.to_numpy(result)

        diff = np.max(np.abs(result_np - reference))
        assert diff < 1e-10, f"{backend_name} matmul differs by {diff}"


def test_kronecker_product():
    """Test Kronecker product across all backends"""
    available = list_available_backends()
    backends_to_test = [name for name, avail in available.items() if avail]

    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    reference = np.kron(h, h)

    for backend_name in backends_to_test:
        backend = get_backend(backend_name)
        result = backend.kron(h, h)
        result_np = backend.to_numpy(result)

        diff = np.max(np.abs(result_np - reference))
        assert diff < 1e-10, f"{backend_name} kron differs by {diff}"


def test_conjugate_transpose():
    """Test conjugate transpose across all backends"""
    available = list_available_backends()
    backends_to_test = [name for name, avail in available.items() if avail]

    test_matrix = np.array([[1 + 1j, 2 - 1j], [3 + 2j, 4 - 3j]])
    reference = np.conj(test_matrix.T)

    for backend_name in backends_to_test:
        backend = get_backend(backend_name)
        result = backend.conjugate_transpose(test_matrix)
        result_np = backend.to_numpy(result)

        diff = np.max(np.abs(result_np - reference))
        assert diff < 1e-10, f"{backend_name} dag differs by {diff}"


def test_memory_efficiency():
    """Test memory efficiency of sparse backend"""
    available = list_available_backends()

    if "sparse" in [name for name, avail in available.items() if avail]:
        backend = get_backend("sparse")

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
            sparse_bytes = (
                sparse_matrix.data.nbytes
                + sparse_matrix.indices.nbytes
                + sparse_matrix.indptr.nbytes
            )
            savings = (dense_bytes - sparse_bytes) / dense_bytes * 100

            assert savings > 50, f"Savings {savings}% too low"


def test_auto_selection():
    """Test auto backend selection logic"""
    available = list_available_backends()
    backend = get_backend("auto")

    # Should select Numba if available, else NumPy
    if available.get("numba", False):
        assert backend.name == "Numba (JIT)"
    else:
        assert backend.name == "NumPy"
