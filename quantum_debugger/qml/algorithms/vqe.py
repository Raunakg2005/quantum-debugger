"""
VQE (Variational Quantum Eigensolver)
=====================================

Find ground state energies of molecules using variational principles.
"""

import numpy as np
from typing import Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class VQE:
    """
    Variational Quantum Eigensolver
    
    Finds the ground state energy of a Hamiltonian using a parameterized
    quantum circuit (ansatz) and classical optimization.
    
    Algorithm:
        1. Prepare trial state |ψ(θ)⟩ using ansatz
        2. Measure energy E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
        3. Classically optimize θ to minimize E(θ)
        4. Repeat until convergence
    
    Attributes:
        hamiltonian: System Hamiltonian matrix
        ansatz_builder: Function that builds ansatz from parameters
        num_qubits: Number of qubits
        optimizer: Optimization method ('COBYLA', 'L-BFGS-B', etc.)
        max_iterations: Maximum optimization iterations
        history: List of (parameters, energy) from each iteration
        
    Examples:
        >>> from quantum_debugger.qml import VQE
        >>> from quantum_debugger.qml.hamiltonians import h2_hamiltonian
        >>> from quantum_debugger.qml.ansatz import hardware_efficient_ansatz
        >>> 
        >>> H = h2_hamiltonian()
        >>> vqe = VQE(hamiltonian=H, ansatz_builder=hardware_efficient_ansatz, num_qubits=2)
        >>> result = vqe.run(initial_params=np.random.rand(4))
        >>> print(f"Ground state energy: {result['ground_state_energy']:.6f} Hartree")
    """
    
    def __init__(
        self,
        hamiltonian: np.ndarray,
        ansatz_builder: Callable,
        num_qubits: int,
        optimizer: str = 'COBYLA',
        max_iterations: int = 100
    ):
        """
        Initialize VQE.
        
        Args:
            hamiltonian: Hamiltonian matrix (2^n × 2^n)
            ansatz_builder: Function(params, num_qubits) -> gates
            num_qubits: Number of qubits
            optimizer: Classical optimizer ('COBYLA', 'L-BFGS-B', 'SLSQP')
            max_iterations: Maximum iterations for optimizer
        """
        self.hamiltonian = hamiltonian
        self.ansatz_builder = ansatz_builder
        self.num_qubits = num_qubits
        self.optimizer = optimizer
        self.max_iterations = max_iterations
        self.history = []
        
        # Validate Hamiltonian size
        expected_size = 2 ** num_qubits
        if hamiltonian.shape != (expected_size, expected_size):
            raise ValueError(
                f"Hamiltonian size {hamiltonian.shape} doesn't match "
                f"{num_qubits} qubits (expected {expected_size}×{expected_size})"
            )
        
        logger.info(f"VQE initialized: {num_qubits} qubits, optimizer={optimizer}")
    
    def cost_function(self, params: np.ndarray) -> float:
        """
        Compute energy expectation value for given parameters.
        
        E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
        
        Args:
            params: Circuit parameters
            
        Returns:
            Energy expectation value (real number)
        """
        # Build circuit with ansatz
        gates = self.ansatz_builder(params, self.num_qubits)
        
        # Simulate circuit to get statevector
        statevector = self._simulate_circuit(gates)
        
        # Compute expectation value
        energy = np.real(statevector.conj().T @ self.hamiltonian @ statevector)
        
        # Track history
        self.history.append({
            'params': params.copy(),
            'energy': energy
        })
        
        logger.debug(f"Iteration {len(self.history)}: E = {energy:.6f}")
        
        return energy
    
    def _simulate_circuit(self, gates: List) -> np.ndarray:
        """
        Simulate quantum circuit and return statevector.
        
        Args:
            gates: List of parameterized gates
            
        Returns:
            Statevector |ψ⟩
        """
        # Initialize state to |00...0⟩
        state = np.zeros(2 ** self.num_qubits, dtype=complex)
        state[0] = 1.0
        
        # Apply each gate
        for gate in gates:
            state = self._apply_gate(state, gate)
        
        return state
    
    def _apply_gate(self, state: np.ndarray, gate) -> np.ndarray:
        """
        Apply a single-qubit gate to the statevector.
        
        Args:
            state: Current statevector
            gate: Parameterized gate (RX, RY, RZ)
            
        Returns:
            New statevector after applying gate
        """
        n = self.num_qubits
        target = gate.target
        U = gate.matrix()
        
        # Build full gate matrix for n qubits
        # U_full = I ⊗ ... ⊗ U ⊗ ... ⊗ I
        full_gate = np.eye(1, dtype=complex)
        
        for q in range(n):
            if q == target:
                full_gate = np.kron(full_gate, U)
            else:
                full_gate = np.kron(full_gate, np.eye(2, dtype=complex))
        
        # Apply gate
        new_state = full_gate @ state
        
        return new_state
    
    def run(self, initial_params: np.ndarray, method: Optional[str] = None) -> Dict:
        """
        Run VQE optimization.
        
        Args:
            initial_params: Starting parameter values
            method: Override optimizer method
            
        Returns:
            Dictionary with results:
            - 'optimal_params': Best parameters found
            - 'ground_state_energy': Minimum energy
            - 'iterations': Number of iterations
            - 'history': Full optimization history
            - 'success': Whether optimization converged
        """
        from scipy.optimize import minimize
        
        # Clear history
        self.history = []
        
        # Use provided method or default
        opt_method = method if method is not None else self.optimizer
        
        logger.info(f"Starting VQE optimization with {opt_method}")
        logger.info(f"Initial parameters: {initial_params}")
        
        # Run optimization
        result = minimize(
            fun=self.cost_function,
            x0=initial_params,
            method=opt_method,
            options={'maxiter': self.max_iterations}
        )
        
        logger.info(f"VQE completed: E = {result.fun:.6f}")
        
        # Extract iteration count (different optimizers have different attributes)
        iterations = getattr(result, 'nit', getattr(result, 'nfev', len(self.history)))
        
        return {
            'optimal_params': result.x,
            'ground_state_energy': result.fun,
            'iterations': iterations,
            'history': self.history,
            'success': result.success,
            'message': getattr(result, 'message', '')
        }
    
    def exact_ground_state(self) -> float:
        """
        Compute exact ground state energy by diagonalization.
        
        Returns:
            Exact ground state energy
        """
        eigenvalues = np.linalg.eigvalsh(self.hamiltonian)
        return eigenvalues[0]
