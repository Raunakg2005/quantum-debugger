"""
Backend abstraction for quantum operations

Supports multiple computational backends:
- NumPy (reference, CPU)
- Numba (JIT-compiled CPU, 2-3x faster)
- CuPy (GPU acceleration, 5-10x faster)
- Sparse (memory-efficient for sparse matrices)

Author: QuantumDebugger Team
Version: 0.4.0
"""

from abc import ABC, abstractmethod
import numpy as np


class Backend(ABC):
    """
    Abstract base class for computational backends.
    
    All backends must implement these core operations for
    quantum state manipulation and gate application.
    """
    
    @abstractmethod
    def zeros(self, shape, dtype=complex):
        """Create zero-filled array"""
        pass
    
    @abstractmethod
    def ones(self, shape, dtype=complex):
        """Create ones-filled array"""
        pass
    
    @abstractmethod
    def eye(self, n, dtype=complex):
        """Create identity matrix"""
        pass
    
    @abstractmethod
    def array(self, data, dtype=complex):
        """Create array from data"""
        pass
    
    @abstractmethod
    def matmul(self, a, b):
        """Matrix multiplication: a @ b"""
        pass
    
    @abstractmethod
    def kron(self, a, b):
        """Kronecker product"""
        pass
    
    @abstractmethod
    def conj(self, a):
        """Complex conjugate"""
        pass
    
    @abstractmethod
    def transpose(self, a):
        """Matrix transpose"""
        pass
    
    @abstractmethod
    def conjugate_transpose(self, a):
        """Hermitian conjugate (dagger)"""
        pass
    
    @abstractmethod
    def norm(self, a):
        """Vector/matrix norm"""
        pass
    
    @abstractmethod
    def sqrt(self, a):
        """Square root (element-wise or matrix)"""
        pass
    
    @abstractmethod
    def to_numpy(self, arr):
        """Convert to NumPy array (for compatibility)"""
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Backend name"""
        pass
    
    def __repr__(self):
        return f"<{self.name} Backend>"
