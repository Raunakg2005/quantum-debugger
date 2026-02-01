"""
VQE (Variational Quantum Eigensolver)
=====================================

Find ground state energies of molecules using variational principles.
"""

import numpy as np
from typing import Callable, Dict, Optional
import logging
import inspect

logger = logging.getLogger(__name__)


class VQE:
    """
    Variational Quantum Eigensolver

    Finds the ground state energy of a Hamiltonian using a parameterized
    quantum circuit (ansatz) and classical optimization.
    """

    def __init__(
        self,
        hamiltonian,
        ansatz_builder: Callable,
        num_qubits: int,
        optimizer: str = "COBYLA",
        max_iterations: int = 100,
    ):
        """
        Initialize VQE.

        Args:
            hamiltonian: Hamiltonian matrix (2^n × 2^n) or tuple (matrix, offset)
            ansatz_builder: Ansatz builder function
            num_qubits: Number of qubits
            optimizer: Classical optimizer
            max_iterations: Maximum iterations for optimizer
        """
        self.num_qubits = num_qubits

        # Convert Hamiltonian to numpy array if needed
        if isinstance(hamiltonian, (tuple, list)):
            # If tuple/list, extract just the matrix (first element)
            # Some hamiltonians return (matrix, energy_offset)
            self.hamiltonian = np.array(hamiltonian[0])
        else:
            self.hamiltonian = hamiltonian

        # Handle ansatz builders that need to be called with num_qubits first
        # (like hardware_efficient_ansatz)
        sig = inspect.signature(ansatz_builder)
        params = list(sig.parameters.keys())

        if len(params) >= 1 and params[0] in ["num_qubits", "n_qubits"]:
            # This is a factory function, call it to get actual builder
            self.ansatz_builder = ansatz_builder(num_qubits)
        else:
            # This is already the builder function
            self.ansatz_builder = ansatz_builder

        # Detect whether the builder expects `num_qubits` as an argument
        try:
            builder_sig = inspect.signature(self.ansatz_builder)
            builder_params = list(builder_sig.parameters.keys())
        except (TypeError, ValueError):
            builder_params = []

        # If the builder has a parameter named 'num_qubits' or 'n_qubits',
        # or if it expects at least two positional args, call it with
        # (params, num_qubits) in `cost_function`.
        self._builder_accepts_num_qubits = (
            any(p in ["num_qubits", "n_qubits"] for p in builder_params)
            or len(builder_params) >= 2
        )

        self.optimizer = optimizer
        self.max_iterations = max_iterations
        self.history = []

        # Validate Hamiltonian size
        expected_size = 2**num_qubits
        if self.hamiltonian.shape != (expected_size, expected_size):
            raise ValueError(
                f"Hamiltonian size {self.hamiltonian.shape} doesn't match "
                f"{num_qubits} qubits (expected {expected_size}×{expected_size})"
            )

        logger.info(f"VQE initialized: {num_qubits} qubits, optimizer={optimizer}")

    def cost_function(self, params: np.ndarray) -> float:
        """
        Compute energy expectation value.

        E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
        """
        # Build circuit with ansatz
        if self._builder_accepts_num_qubits:
            result = self.ansatz_builder(params, self.num_qubits)
        else:
            result = self.ansatz_builder(params)

        # If ansatz returns a list of gates, build circuit manually
        if isinstance(result, list):
            from ...core.circuit import QuantumCircuit

            circuit = QuantumCircuit(self.num_qubits)
            for gate in result:
                # Apply parameterized gate using its matrix
                circuit._add_gate(gate.name, gate.matrix(), gate.target)
        else:
            circuit = result

        # Get statevector from circuit
        statevector = circuit.get_statevector().state_vector

        # Compute expectation value
        energy = np.real(statevector.conj().T @ self.hamiltonian @ statevector)

        # Track history
        self.history.append({"params": params.copy(), "energy": energy})

        logger.debug(f"Iteration {len(self.history)}: E = {energy:.6f}")

        return energy

    def run(self, initial_params: np.ndarray, method: Optional[str] = None) -> Dict:
        """Run VQE optimization."""
        from scipy.optimize import minimize

        self.history = []
        opt_method = method if method is not None else self.optimizer

        logger.info(f"Starting VQE optimization with {opt_method}")

        result = minimize(
            fun=self.cost_function,
            x0=initial_params,
            method=opt_method,
            options={"maxiter": self.max_iterations},
        )

        logger.info(f"VQE completed: E = {result.fun:.6f}")

        iterations = getattr(result, "nit", getattr(result, "nfev", len(self.history)))

        return {
            "optimal_params": result.x,
            "ground_state_energy": result.fun,
            "iterations": iterations,
            "history": self.history,
            "success": result.success,
            "message": getattr(result, "message", ""),
        }

    def exact_ground_state(self) -> float:
        """Compute exact ground state energy by diagonalization."""
        eigenvalues = np.linalg.eigvalsh(self.hamiltonian)
        return eigenvalues[0]
