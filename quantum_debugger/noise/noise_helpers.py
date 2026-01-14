"""
Helper functions for noise simulation
Adds density matrix support without modifying core QuantumState
"""

import numpy as np
from quantum_debugger.core.quantum_state import QuantumState as _QuantumState


class QuantumState(_QuantumState):
    """
    Extended QuantumState with density matrix support for noise simulation
    """

    def __init__(self, num_qubits, state_vector=None, use_density_matrix=False):
        """
        Initialize quantum state with optional density matrix support

        Args:
            num_qubits: Number of qubits
            state_vector: Initial state vector
            use_density_matrix: If True, use density matrix representation
        """
        super().__init__(num_qubits, state_vector)

        self.use_density_matrix = use_density_matrix

        if use_density_matrix:
            # Convert state vector to density matrix
            if state_vector is not None:
                psi = np.array(state_vector, dtype=complex)
                psi /= np.linalg.norm(psi)
            else:
                psi = self.state_vector

            self.density_matrix = np.outer(psi, psi.conj())
            self.state_vector = None  # Mark that we're using density matrix
        else:
            self.density_matrix = None

    def apply_gate(self, gate_matrix, target_qubits):
        """
        Apply gate to quantum state (supports both state vector and density matrix)

        Args:
            gate_matrix: Gate unitary matrix
            target_qubits: Qubit indices to apply gate to
        """
        # If using density matrix, apply as ρ' = UρU†
        if self.use_density_matrix and self.density_matrix is not None:
            # Expand gate to full system
            full_matrix = self._expand_gate_matrix(gate_matrix, target_qubits)

            # Apply: ρ' = U ρ U†
            self.density_matrix = (
                full_matrix @ self.density_matrix @ full_matrix.conj().T
            )
        else:
            # Use base class implementation for state vectors
            super().apply_gate(gate_matrix, target_qubits)

    def _expand_gate_matrix(self, gate_matrix, target_qubits):
        """Expand gate matrix to full Hilbert space"""
        # This is the same logic as in base QuantumState
        # Get matrix size to determine single/multi-qubit
        gate_size = gate_matrix.shape[0]
        num_gate_qubits = int(np.log2(gate_size))

        if not isinstance(target_qubits, list):
            target_qubits = [target_qubits]

        # Start with identity
        full_dim = 2**self.num_qubits
        full_matrix = np.eye(full_dim, dtype=complex)

        # Build full matrix using Kronecker products
        I = np.eye(2, dtype=complex)
        result = np.array([[1.0]], dtype=complex)

        for qubit_idx in range(self.num_qubits):
            if qubit_idx in target_qubits:
                # Find position in target_qubits list
                pos = target_qubits.index(qubit_idx)
                # Extract corresponding 2x2 block from gate
                if num_gate_qubits == 1:
                    result = np.kron(result, gate_matrix)
                else:
                    # For multi-qubit gates, apply the full gate
                    if qubit_idx == target_qubits[0]:
                        result = np.kron(result, gate_matrix)
                    # Skip other target qubits as they're part of the gate
                    elif qubit_idx in target_qubits[1:]:
                        continue
            else:
                result = np.kron(result, I)

        return (
            result
            if result.shape[0] == full_dim
            else super()._expand_gate_matrix(gate_matrix, target_qubits)
        )
