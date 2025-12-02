"""
Quantum state representation and operations
"""

import numpy as np
from typing import List, Tuple, Optional
import copy


class QuantumState:
    """Represents a quantum state vector"""
    
    def __init__(self, num_qubits: int, state_vector: Optional[np.ndarray] = None):
        """
        Initialize a quantum state
        
        Args:
            num_qubits: Number of qubits
            state_vector: Optional initial state vector (defaults to |0...0>)
        """
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        
        if state_vector is not None:
            if len(state_vector) != self.dim:
                raise ValueError(f"State vector size {len(state_vector)} doesn't match {self.dim}")
            self.state_vector = np.array(state_vector, dtype=complex)
            self._normalize()
        else:
            # Initialize to |0...0> state
            self.state_vector = np.zeros(self.dim, dtype=complex)
            self.state_vector[0] = 1.0
    
    def _normalize(self):
        """Normalize the state vector"""
        norm = np.linalg.norm(self.state_vector)
        if norm > 0:
            self.state_vector /= norm
    
    def copy(self):
        """Create a deep copy of this state"""
        return copy.deepcopy(self)
    
    def apply_gate(self, gate_matrix: np.ndarray, target_qubits: List[int]):
        """
        Apply a quantum gate to specific qubits
        
        Args:
            gate_matrix: Unitary matrix of the gate
            target_qubits: List of qubit indices to apply gate to
        """
        # Build full gate matrix for entire system
        full_matrix = self._build_full_gate_matrix(gate_matrix, target_qubits)
        
        # Apply gate
        self.state_vector = full_matrix @ self.state_vector
        self._normalize()
    
    def _build_full_gate_matrix(self, gate_matrix: np.ndarray, target_qubits: List[int]) -> np.ndarray:
        """Build the full gate matrix for the entire quantum system"""
        num_gate_qubits = int(np.log2(gate_matrix.shape[0]))
        
        if num_gate_qubits == self.num_qubits and target_qubits == list(range(self.num_qubits)):
            return gate_matrix
        
        # For single and multi-qubit gates on subset of qubits
        return self._expand_gate_to_full_space(gate_matrix, target_qubits)
    
    def _expand_gate_to_full_space(self, gate_matrix: np.ndarray, target_qubits: List[int]) -> np.ndarray:
        """Expand a gate acting on subset of qubits to full Hilbert space"""
        full_matrix = np.eye(self.dim, dtype=complex)
        
        # Build permutation that brings target qubits to front
        num_gate_qubits = len(target_qubits)
        other_qubits = [q for q in range(self.num_qubits) if q not in target_qubits]
        
        for i in range(self.dim):
            for j in range(self.dim):
                # Extract qubit states
                i_bits = [(i >> k) & 1 for k in range(self.num_qubits)]
                j_bits = [(j >> k) & 1 for k in range(self.num_qubits)]
                
                # Check if non-target qubits match
                match = all(i_bits[q] == j_bits[q] for q in other_qubits)
                
                if match:
                    # Get indices for gate matrix
                    i_gate = sum(i_bits[target_qubits[k]] << k for k in range(num_gate_qubits))
                    j_gate = sum(j_bits[target_qubits[k]] << k for k in range(num_gate_qubits))
                    
                    full_matrix[i, j] = gate_matrix[i_gate, j_gate]
                else:
                    full_matrix[i, j] = 0.0
        
        return full_matrix
    
    def measure(self, qubit: int) -> int:
        """
        Measure a qubit and collapse the state
        
        Args:
            qubit: Index of qubit to measure
            
        Returns:
            Measurement result (0 or 1)
        """
        # Calculate probabilities
        prob_0 = self.get_measurement_probability(qubit, 0)
        
        # Randomly choose outcome
        outcome = 0 if np.random.random() < prob_0 else 1
        
        # Collapse state
        self._collapse_state(qubit, outcome)
        
        return outcome
    
    def measure_all(self) -> List[int]:
        """Measure all qubits"""
        return [self.measure(q) for q in range(self.num_qubits)]
    
    def get_measurement_probability(self, qubit: int, outcome: int) -> float:
        """Get probability of measuring a specific outcome for a qubit"""
        prob = 0.0
        for i, amplitude in enumerate(self.state_vector):
            if (i >> qubit) & 1 == outcome:
                prob += abs(amplitude) ** 2
        return prob
    
    def get_probabilities(self) -> np.ndarray:
        """Get probability distribution over all basis states"""
        return np.abs(self.state_vector) ** 2
    
    def _collapse_state(self, qubit: int, outcome: int):
        """Collapse state after measurement"""
        new_state = np.zeros_like(self.state_vector)
        
        for i, amplitude in enumerate(self.state_vector):
            if (i >> qubit) & 1 == outcome:
                new_state[i] = amplitude
        
        self.state_vector = new_state
        self._normalize()
    
    def fidelity(self, other: 'QuantumState') -> float:
        """
        Calculate fidelity with another quantum state
        
        Args:
            other: Another quantum state
            
        Returns:
            Fidelity value between 0 and 1
        """
        if self.num_qubits != other.num_qubits:
            raise ValueError("States must have same number of qubits")
        
        overlap = np.abs(np.vdot(self.state_vector, other.state_vector))
        return overlap ** 2
    
    def entropy(self) -> float:
        """Calculate von Neumann entropy"""
        probabilities = self.get_probabilities()
        # Filter out zero probabilities to avoid log(0)
        probabilities = probabilities[probabilities > 1e-10]
        return -np.sum(probabilities * np.log2(probabilities))
    
    def is_entangled(self) -> bool:
        """
        Check if state is entangled (simple check for 2-qubit systems)
        
        For 2 qubits: state is entangled if it cannot be written as tensor product
        """
        if self.num_qubits != 2:
            # More complex check needed for >2 qubits
            return True  # Conservative assumption
        
        # Reshape state vector to 2x2 matrix
        state_matrix = self.state_vector.reshape(2, 2)
        
        # Check if matrix has rank 1 (separable) or rank 2 (entangled)
        singular_values = np.linalg.svd(state_matrix, compute_uv=False)
        
        # If only one significant singular value, state is separable
        return not (singular_values[1] < 1e-10)
    
    def bloch_vector(self, qubit: int = 0) -> Tuple[float, float, float]:
        """
        Get Bloch sphere coordinates for a single qubit
        
        Args:
            qubit: Index of qubit (for multi-qubit systems, traces out other qubits)
            
        Returns:
            (x, y, z) coordinates on Bloch sphere
        """
        if self.num_qubits == 1:
            rho = np.outer(self.state_vector, self.state_vector.conj())
        else:
            # Partial trace to get single-qubit density matrix
            rho = self._partial_trace(qubit)
        
        # Pauli matrices
        sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        x = np.real(np.trace(rho @ sigma_x))
        y = np.real(np.trace(rho @ sigma_y))
        z = np.real(np.trace(rho @ sigma_z))
        
        return (x, y, z)
    
    def _partial_trace(self, keep_qubit: int) -> np.ndarray:
        """Partial trace to get single-qubit density matrix"""
        rho = np.zeros((2, 2), dtype=complex)
        
        for i in range(self.dim):
            for j in range(self.dim):
                i_bit = (i >> keep_qubit) & 1
                j_bit = (j >> keep_qubit) & 1
                
                # Check if other qubits match
                i_other = i & ~(1 << keep_qubit)
                j_other = j & ~(1 << keep_qubit)
                
                if i_other == j_other:
                    rho[i_bit, j_bit] += self.state_vector[i] * self.state_vector[j].conj()
        
        return rho
    
    def __repr__(self):
        """String representation of quantum state"""
        state_str = []
        for i, amplitude in enumerate(self.state_vector):
            if abs(amplitude) > 1e-10:
                binary = format(i, f'0{self.num_qubits}b')
                real = np.real(amplitude)
                imag = np.imag(amplitude)
                
                if abs(imag) < 1e-10:
                    coef = f"{real:.3f}"
                elif abs(real) < 1e-10:
                    coef = f"{imag:.3f}i"
                else:
                    coef = f"{real:.3f}+{imag:.3f}i"
                
                state_str.append(f"{coef}|{binary}>")
        
        return " + ".join(state_str) if state_str else "0"
    
    def __str__(self):
        return self.__repr__()
