"""
NumPy backend - reference CPU implementation

This is the default, always-available backend.
"""

import numpy as np
from .base import Backend


class NumPyBackend(Backend):
    """Reference NumPy backend (CPU, single-threaded)"""

    def zeros(self, shape, dtype=complex):
        return np.zeros(shape, dtype=dtype)

    def ones(self, shape, dtype=complex):
        return np.ones(shape, dtype=dtype)

    def eye(self, n, dtype=complex):
        return np.eye(n, dtype=dtype)

    def array(self, data, dtype=complex):
        return np.array(data, dtype=dtype)

    def matmul(self, a, b):
        return np.matmul(a, b)

    def kron(self, a, b):
        return np.kron(a, b)

    def conj(self, a):
        return np.conj(a)

    def transpose(self, a):
        return np.transpose(a)

    def conjugate_transpose(self, a):
        return np.conj(a.T)

    def norm(self, a):
        return np.linalg.norm(a)

    def sqrt(self, a):
        if np.isscalar(a):
            return np.sqrt(a)
        # For matrices, use element-wise sqrt
        return np.sqrt(a)

    def to_numpy(self, arr):
        # Already NumPy
        return arr

    @property
    def name(self):
        return "NumPy"
