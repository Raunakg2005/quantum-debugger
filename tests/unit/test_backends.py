"""
Test backend system

Quick verification that backends work correctly.
"""

import pytest
import numpy as np


def test_backend_imports():
    """Test that backend modules can be imported"""
    try:
        from quantum_debugger.backends import get_backend, list_available_backends
        from quantum_debugger.backends import NumPyBackend

        assert True
    except ImportError as e:
        pytest.fail(f"Backend import failed: {e}")


def test_list_available_backends():
    """Test listing available backends"""
    from quantum_debugger.backends import list_available_backends

    available = list_available_backends()
    assert isinstance(available, dict)
    assert "numpy" in available
    assert available["numpy"] is True  # NumPy should always be available


def test_numpy_backend():
    """Test NumPy backend basic operations"""
    from quantum_debugger.backends import get_backend

    backend = get_backend("numpy")
    assert backend.name in ["numpy", "NumPy"]  # Accept both casings

    # Test basic operations
    a = backend.zeros((4, 4))
    b = backend.eye(4)
    c = backend.matmul(a, b)

    assert a.shape == (4, 4)
    assert b.shape == (4, 4)
    assert c.shape == (4, 4)


def test_numba_backend():
    """Test Numba backend if available"""
    from quantum_debugger.backends import get_backend

    try:
        backend = get_backend("numba")
        assert backend.name in ["numba", "Numba (JIT)"]  # Accept both casings

        # Test JIT compilation
        a = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
        b = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)

        c = backend.matmul(a, b)
        c_ref = np.matmul(a, b)

        # Check correctness
        diff = np.max(np.abs(c - c_ref))
        assert diff < 1e-10, f"Numba differs from NumPy by {diff:.2e}"
    except ImportError:
        pytest.skip("Numba not available")
