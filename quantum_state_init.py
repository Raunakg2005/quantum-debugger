"""
Quantum state representation and operations
"""

import numpy as np
from typing import List, Tuple, Optional
import copy


class QuantumState:
    """Represents a quantum state vector"""
    
    def __init__(self, num_qubits: int, state_vector: Optional[np.ndarray] = None, backend='auto'):
        """
        Initialize a quantum state
        
        Args:
            num_qubits: Number of qubits
            state_vector: Optional initial state vector (defaults to |0...0⟩)
            backend: Computational backend ('auto', 'numpy', 'numba', 'sparse')
        """
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        
        # Get computational backend (import here to avoid circular imports)
        from quantum_debugger.backends import get_backend
        self.backend = get_backend(backend)
        
        if state_vector is not None:
            if len(state_vector) != self.dim:
                raise ValueError(f"State vector size {len(state_vector)} doesn't match {self.dim}")
            self.state_vector = np.array(state_vector, dtype=complex)
            self._normalize()
        else:
            # Initialize to |0...0⟩ state
            self.state_vector = np.zeros(self.dim, dtype=complex)
            self.state_vector[0] = 1.0
