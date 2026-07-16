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
        optimizer: str = "COBYLA",
        max_iterations: int = 100,
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

        logger.info(
            f"QAOA initialized: {self.num_qubits} qubits, p={p}, {len(graph)} edges"
        )

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
        gamma = params[: self.p]
        beta = params[self.p :]

        # Simulate the QAOA ansatz and evaluate the expected cut
        statevector = self._simulate_qaoa(gamma, beta)
        cost = self._evaluate_maxcut(statevector)

        self.history.append({"params": params.copy(), "cost": cost})

        # Return negative for minimization
        return -cost

    def _simulate_qaoa(self, gamma: np.ndarray, beta: np.ndarray) -> np.ndarray:
        """
        Simulate the QAOA circuit on the shared state-vector simulator.

        Cost layer applies a genuine two-qubit ZZ interaction per edge
        (CNOT · RZ · CNOT), which entangles the qubits — the previous version
        used only single-qubit RZ rotations, so the state stayed a product state
        and could not represent correlated MaxCut solutions. Node ``i`` maps to
        qubit ``i`` consistently here and in the cut evaluation below.
        """
        from ...core.quantum_state import QuantumState
        from ...core.gates import GateLibrary

        qs = QuantumState(self.num_qubits)

        # Initial state |++...+>: Hadamard on every qubit
        for q in range(self.num_qubits):
            qs.apply_gate(GateLibrary.H, [q])

        for layer in range(self.p):
            # Cost layer: exp(i γ Z_i Z_j) on each edge via CNOT–RZ–CNOT
            for i, j in self.graph:
                qs.apply_gate(GateLibrary.CNOT, [i, j])
                qs.apply_gate(GateLibrary.RZ(2 * gamma[layer]), [j])
                qs.apply_gate(GateLibrary.CNOT, [i, j])

            # Mixing layer: RX(2β) on every qubit
            for q in range(self.num_qubits):
                qs.apply_gate(GateLibrary.RX(2 * beta[layer]), [q])

        return qs.state_vector

    def _evaluate_maxcut(self, statevector: np.ndarray) -> float:
        """Expected MaxCut value under the measured probability distribution."""
        probabilities = np.abs(statevector) ** 2

        cost = 0.0
        for state_int, prob in enumerate(probabilities):
            if prob < 1e-12:
                continue
            cost += prob * self._count_cut_edges(state_int)

        return cost

    def _count_cut_edges(self, state_int: int) -> int:
        """Count cut edges for a basis state (node i is bit i of state_int)."""
        count = 0
        for i, j in self.graph:
            if ((state_int >> i) & 1) != ((state_int >> j) & 1):
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
            options={"maxiter": self.max_iterations},
        )

        # Extract iteration count safely
        iterations = getattr(result, "nit", getattr(result, "nfev", len(self.history)))

        return {
            "optimal_params": result.x,
            "best_value": -result.fun,  # Negate back
            "iterations": iterations,
            "history": self.history,
            "success": result.success,
        }
