"""
CuPy backend - GPU acceleration with NVIDIA CUDA

Provides 5-10x speedup over NumPy for matrix operations.
Requires NVIDIA GPU and CuPy installation.
"""

import numpy as np
from .base import Backend

try:
    import cupy as cp

    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False


class CuPyBackend(Backend):
    """
    GPU-accelerated backend using CuPy and CUDA.

    Advantages:
    - 5-10x faster than NumPy for large operations
    - Automatic GPU memory management
    - CUDA-optimized kernels

    Requirements:
    - NVIDIA GPU with CUDA support
    - CuPy installed (pip install cupy-cuda11x or cupy-cuda12x)

    Best for: Large circuits (10+ qubits) with NVIDIA GPU
    """

    def __init__(self, device_id=0):
        """
        Initialize GPU backend

        Args:
            device_id: GPU device ID (default: 0 for first GPU)
        """
        if not HAS_CUPY:
            raise ImportError(
                "CuPy not installed. For GPU acceleration, install with:\\n"
                "  pip install cupy-cuda12x  # CUDA 12.x\\n"
                "  pip install cupy-cuda11x  # CUDA 11.x\\n"
                "Check https://docs.cupy.dev/en/stable/install.html"
            )

        # Set GPU device
        cp.cuda.Device(device_id).use()
        self.device_id = device_id

        # Get total GPU memory
        self.total_memory = cp.cuda.Device().mem_info[1]  # Total GPU memory

    def zeros(self, shape, dtype=complex):
        return cp.zeros(shape, dtype=cp.complex128 if dtype == complex else dtype)

    def ones(self, shape, dtype=complex):
        return cp.ones(shape, dtype=cp.complex128 if dtype == complex else dtype)

    def eye(self, n, dtype=complex):
        return cp.eye(n, dtype=cp.complex128 if dtype == complex else dtype)

    def array(self, data, dtype=complex):
        return cp.array(data, dtype=cp.complex128 if dtype == complex else dtype)

    def matmul(self, a, b):
        """GPU-accelerated matrix multiplication"""
        # Ensure data is on GPU
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        if not isinstance(b, cp.ndarray):
            b = cp.asarray(b)

        return cp.matmul(a, b)

    def kron(self, a, b):
        """GPU-accelerated Kronecker product"""
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        if not isinstance(b, cp.ndarray):
            b = cp.asarray(b)

        return cp.kron(a, b)

    def conj(self, a):
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        return cp.conj(a)

    def transpose(self, a):
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        return cp.transpose(a)

    def conjugate_transpose(self, a):
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        return cp.conj(a.T)

    def norm(self, a):
        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        return float(cp.linalg.norm(a))

    def sqrt(self, a):
        if np.isscalar(a):
            return np.sqrt(a)

        if not isinstance(a, cp.ndarray):
            a = cp.asarray(a)
        return cp.sqrt(a)

    def to_numpy(self, arr):
        """Transfer data from GPU to CPU"""
        if isinstance(arr, cp.ndarray):
            return cp.asnumpy(arr)
        return np.asarray(arr)

    @property
    def name(self):
        return f"CuPy (GPU:{self.device_id})"

    def memory_info(self):
        """Get GPU memory usage info"""
        mempool = cp.get_default_memory_pool()
        used = mempool.used_bytes()
        total = self.total_memory

        return {
            "used_mb": used / 1024**2,
            "total_mb": total / 1024**2,
            "free_mb": (total - used) / 1024**2,
            "usage_percent": (used / total) * 100,
        }
