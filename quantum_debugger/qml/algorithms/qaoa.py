"""
QAOA (Quantum Approximate Optimization Algorithm)
=================================================

Solve combinatorial optimization problems.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QAOA:
    """
    Quantum Approximate Optimization Algorithm
    
    Solves combinatorial optimization problems like MaxCut using a
    parameterized quantum circuit.
    
    Attributes:
        graph: List of edges [(i,j), ...] defining the problem
        p: Number of QAOA layers
        num_qubits: Number of qubits (nodes in graph)
        
    Examples:
        >>> # MaxCut on a square graph
        >>> graph = [(0,1), (1,2), (2,3), (3,0)]
        >>> qaoa = QAOA(graph=graph, p=2)
        >>> result = qaoa.run()
        >>> print(f"Best cut value: {result['best_value']}")
    """
    
    def __init__(
        self,
        graph: List[Tuple[int, int]],
        p: int = 1,
        optimizer: str = 'COBYLA',
        max_iterations: int = 100
    ):
        """
        Initialize QAOA.
        
        Args:
            graph: List of edges defining the problem
            p: Number of QAOA layers
            optimizer: Classical optimizer
            max_iterations: Maximum iterations
        """
        self.graph = graph
        self.p = p
        self.optimizer = optimizer
        self.max_iterations = max_iterations
        self.history = []
        
        # Determine number of qubits from graph
        nodes = set()
        for edge in graph:
            nodes.add(edge[0])
            nodes.add(edge[1])
        self.num_qubits = max(nodes) + 1
        
        logger.info(f"QAOA initialized: {self.num_qubits} qubits, p={p}, {len(graph)} edges")
    
    def cost_function(self, params: np.ndarray) -> float:
        """
        Compute cost function (negative for maximization).
        
        For MaxCut: maximize number of edges between different partitions.
        
        Args:
            params: Parameters [γ₀, γ₁, ..., γₚ, β₀, β₁, ..., βₚ]
            
        Returns:
            Negative cost value (for minimization)
        """
        # Split parameters
        gamma = params[:self.p]
        beta = params[self.p:]
        
        # Build QAOA circuit
        from ..gates import RXGate, RZGate
        
        gates = []
        
        # Initial state: |++++...⟩ (Hadamard on all - not parameterized)
        
        for layer in range(self.p):
            # Cost layer: RZ gates
            for i, j in self.graph:
                gates.append(RZGate(i, gamma[layer], trainable=True))
                gates.append(RZGate(j, gamma[layer], trainable=True))
            
            # Mixing layer: RX gates
            for q in range(self.num_qubits):
                gates.append(RXGate(q, 2 * beta[layer], trainable=True))
        
        # Simulate circuit
        statevector = self._simulate_qaoa(gates)
        
        # Evaluate MaxCut
        cost = self._evaluate_maxcut(statevector)
        
        self.history.append({
            'params': params.copy(),
            'cost': cost
        })
        
        # Return negative for minimization
        return -cost
    
    def _simulate_qaoa(self, gates: List) -> np.ndarray:
        """Simulate QAOA circuit starting from |++++...⟩"""
        # Start with superposition state |++++...⟩
        state = np.ones(2 ** self.num_qubits, dtype=complex) / np.sqrt(2 ** self.num_qubits)
        
        # Apply gates (simplified - same as VQE)
        for gate in gates:
            state = self._apply_gate(state, gate)
        
        return state
    
    def _apply_gate(self, state: np.ndarray, gate) -> np.ndarray:
        """Apply single-qubit gate (same as VQE)"""
        n = self.num_qubits
        target = gate.target
        U = gate.matrix()
        
        # Build full gate
        full_gate = np.eye(1, dtype=complex)
        for q in range(n):
            if q == target:
                full_gate = np.kron(full_gate, U)
            else:
                full_gate = np.kron(full_gate, np.eye(2, dtype=complex))
        
        return full_gate @ state
    
    def _evaluate_maxcut(self, statevector: np.ndarray) -> float:
        """Evaluate MaxCut cost from statevector"""
        probabilities = np.abs(statevector) ** 2
        
        cost = 0.0
        for bitstring_int, prob in enumerate(probabilities):
            bitstring = format(bitstring_int, f'0{self.num_qubits}b')
            cut_value = self._count_cut_edges(bitstring)
            cost += prob * cut_value
        
        return cost
    
    def _count_cut_edges(self, bitstring: str) -> int:
        """Count edges in the cut"""
        count = 0
        for i, j in self.graph:
            if bitstring[i] != bitstring[j]:
                count += 1
        return count
    
    def run(self, initial_params: Optional[np.ndarray] = None) -> Dict:
        """
        Run QAOA optimization.
        
        Args:
            initial_params: Starting parameters (optional)
            
        Returns:
            Result dictionary
        """
        from scipy.optimize import minimize
        
        if initial_params is None:
            # Random initialization
            initial_params = np.random.rand(2 * self.p) * np.pi
        
        self.history = []
        
        logger.info("Starting QAOA optimization")
        
        result = minimize(
            fun=self.cost_function,
            x0=initial_params,
            method=self.optimizer,
            options={'maxiter': self.max_iterations}
        )
        
        # Extract iteration count safely
        iterations = getattr(result, 'nit', getattr(result, 'nfev', len(self.history)))
        
        return {
            'optimal_params': result.x,
            'best_value': -result.fun,  # Negate back
            'iterations': iterations,
            'history': self.history,
            'success': result.success
        }
