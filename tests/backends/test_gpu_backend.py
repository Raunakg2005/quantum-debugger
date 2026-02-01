"""
Tests for GPU Backend (Works with CPU fallback)
"""

import pytest
import numpy as np
from quantum_debugger.backends import (
    GPUBackend,
    get_optimal_backend,
    benchmark_backends,
)



try:
    import cupy
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


@pytest.mark.skipif(not CUPY_AVAILABLE, reason="CuPy not installed")
class TestGPUBackend:
    """Test GPU backend functionality"""

    def test_initialization(self):
        """Test GPU backend initialization"""
        backend = GPUBackend()

        assert backend is not None
        assert backend.xp is not None
        assert backend.device_name is not None

    def test_state_allocation(self):
        """Test quantum state allocation"""
        backend = GPUBackend()

        state = backend.allocate_state(n_qubits=3)
        state_cpu = backend.to_cpu(state)

        assert len(state_cpu) == 8  # 2^3
        assert state_cpu[0] == 1.0 + 0j  # Initialized to |000⟩
        assert np.sum(np.abs(state_cpu) ** 2) == pytest.approx(1.0)

    def test_to_cpu_conversion(self):
        """Test moving array to CPU"""
        backend = GPUBackend()

        state = backend.allocate_state(n_qubits=2)
        cpu_state = backend.to_cpu(state)

        # Should always be numpy array after to_cpu
        assert isinstance(cpu_state, np.ndarray)
        assert len(cpu_state) == 4

    def test_kronecker_product(self):
        """Test Kronecker product"""
        backend = GPUBackend()

        a = backend.to_gpu(np.array([[1, 0], [0, 1]]))
        b = backend.to_gpu(np.array([[0, 1], [1, 0]]))

        result = backend.kron(a, b)
        result_cpu = backend.to_cpu(result)

        expected = np.kron([[1, 0], [0, 1]], [[0, 1], [1, 0]])
        np.testing.assert_array_almost_equal(result_cpu, expected)

    def test_get_info(self):
        """Test backend information retrieval"""
        backend = GPUBackend()

        info = backend.get_info()

        assert "backend" in info
        assert "library" in info
        assert "device" in info


class TestOptimalBackend:
    """Test optimal backend selection"""

    def test_backend_selection(self):
        """Test get_optimal_backend works"""
        backend = get_optimal_backend(n_qubits=5, prefer_gpu=False)

        assert backend is not None
        assert hasattr(backend, "allocate_state")


class TestCPUMode:
    """Test CPU fallback mode"""

    def test_cpu_operations(self):
        """Test operations work in CPU mode"""
        backend = GPUBackend()

        state = backend.allocate_state(n_qubits=2)
        assert len(backend.to_cpu(state)) == 4

        # Matrix operations
        a = backend.to_gpu(np.array([[1, 2], [3, 4]]))
        b = backend.to_gpu(np.array([[5, 6], [7, 8]]))

        result = backend.dot(a, b)
        assert backend.to_cpu(result).shape == (2, 2)
