"""
Sparse matrix backend for memory-efficient quantum operations

Uses SciPy sparse matrices for gates with high sparsity.
Can reduce memory usage by 50%+ for certain operations.
"""

import numpy as np
from scipy import sparse
from .base import Backend


class SparseBackend(Backend):
    """
    Sparse matrix backend using SciPy.
    
    Advantages:
    - 50%+ memory savings for sparse operations
    - Faster for very sparse matrices
    - Good for large-qubit circuits
    
    Best for: Circuits with many sparse gates (CNOT, CZ, etc.)
    """
    
    def __init__(self, sparsity_threshold=0.5):
        """
        Args:
            sparsity_threshold: Fraction of zeros to consider matrix sparse
                               0.5 means >50% zeros
        """
        self.threshold = sparsity_threshold
    
    @staticmethod
    def is_sparse(matrix, threshold=0.5):
        """Check if matrix is sparse enough to benefit from sparse format"""
        if isinstance(matrix, sparse.spmatrix):
            return True
        
        if isinstance(matrix, np.ndarray):
            # Count non-zero elements
            nonzero = np.count_nonzero(matrix)
            sparsity = 1.0 - (nonzero / matrix.size)
            return sparsity >= threshold
        
        return False
    
    @staticmethod
    def to_sparse(matrix, format='csr'):
        """Convert to sparse format"""
        if isinstance(matrix, sparse.spmatrix):
            return matrix.asformat(format)
        return sparse.csr_matrix(matrix)
    
    def zeros(self, shape, dtype=complex):
        # Sparse zeros matrix
        return sparse.csr_matrix(shape, dtype=dtype)
    
    def ones(self, shape, dtype=complex):
        # Dense ones (not sparse)
        return np.ones(shape, dtype=dtype)
    
    def eye(self, n, dtype=complex):
        # Sparse identity
        return sparse.eye(n, dtype=dtype, format='csr')
    
    def array(self, data, dtype=complex):
        arr = np.array(data, dtype=dtype)
        if self.is_sparse(arr, self.threshold):
            return self.to_sparse(arr)
        return arr
    
    def matmul(self, a, b):
        """Smart matrix multiplication"""
        # Convert to sparse if beneficial
        if self.is_sparse(a, self.threshold):
            a = self.to_sparse(a)
        if self.is_sparse(b, self.threshold):
            b = self.to_sparse(b)
        
        # Sparse @ sparse = sparse
        if sparse.issparse(a) or sparse.issparse(b):
            result = a @ b
            
            # Convert back to dense if result is not sparse
            if sparse.issparse(result):
                if self.is_sparse(result, self.threshold):
                    return result
                return result.toarray()
            return result
        
        # Both dense
        return np.matmul(a, b)
    
    def kron(self, a, b):
        """Sparse Kronecker product"""
        # Convert to sparse if beneficial
        if self.is_sparse(a, self.threshold):
            a = self.to_sparse(a, format='coo')
        if self.is_sparse(b, self.threshold):
            b = self.to_sparse(b, format='coo')
        
        # Use sparse.kron
        if sparse.issparse(a) or sparse.issparse(b):
            result = sparse.kron(a, b, format='csr')
            
            # Keep as sparse if still sparse
            if self.is_sparse(result, self.threshold):
                return result
            return result.toarray()
        
        return np.kron(a, b)
    
    def conj(self, a):
        if sparse.issparse(a):
            return a.conjugate()
        return np.conj(a)
    
    def transpose(self, a):
        if sparse.issparse(a):
            return a.transpose()
        return np.transpose(a)
    
    def conjugate_transpose(self, a):
        if sparse.issparse(a):
            return a.conjugate().transpose()
        return np.conj(a.T)
    
    def norm(self, a):
        if sparse.issparse(a):
            return sparse.linalg.norm(a)
        return np.linalg.norm(a)
    
    def sqrt(self, a):
        if sparse.issparse(a):
            # For sparse, use element-wise sqrt on data
            result = a.copy()
            result.data = np.sqrt(result.data)
            return result
        
        if np.isscalar(a):
            return np.sqrt(a)
        return np.sqrt(a)
    
    def to_numpy(self, arr):
        if sparse.issparse(arr):
            return arr.toarray()
        return np.asarray(arr)
    
    @property
    def name(self):
        return "Sparse (SciPy)"
