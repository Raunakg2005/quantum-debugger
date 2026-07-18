"""
Variational Quantum Deflation (VQD)

Finds low-lying excited states of a Hamiltonian, not just the ground state
(Higgott et al. 2019). After the ground state |psi_0> is found with VQE, each
subsequent state is found by minimizing

    E_k(theta) = <psi(theta)|H|psi(theta)> + sum_{j<k} beta * |<psi(theta)|psi_j>|^2

The overlap penalty pushes the k-th state to be orthogonal to all lower states,
so the optimizer converges to the next-higher eigenstate. Uses a self-contained
hardware-efficient ansatz and SciPy for the classical optimization.
"""

import numpy as np
from typing import Optional


class VQD:
    """
    Variational Quantum Deflation for ground and excited states.

    Examples:
        >>> H = np.diag([0.0, 1.0, 2.0, 3.0])          # any Hermitian 2**n x 2**n
        >>> vqd = VQD(H, num_qubits=2, n_states=3)
        >>> result = vqd.run()
        >>> result["energies"]                          # ~[0, 1, 2]
    """

    def __init__(
        self,
        hamiltonian: np.ndarray,
        num_qubits: int,
        n_states: int = 2,
        n_layers: Optional[int] = None,
        beta: float = 3.0,
        optimizer: str = "COBYLA",
        max_iterations: int = 250,
    ):
        H = np.asarray(hamiltonian, dtype=complex)
        expected = 2**num_qubits
        if H.shape != (expected, expected):
            raise ValueError(
                f"Hamiltonian {H.shape} does not match {num_qubits} qubits"
            )
        self.H = H
        self.num_qubits = num_qubits
        self.n_states = n_states
        self.n_layers = n_layers if n_layers is not None else num_qubits + 1
        self.beta = beta
        self.optimizer = optimizer
        self.max_iterations = max_iterations

        self.n_params = num_qubits * (self.n_layers + 1)
        self.found_states = []
        self.energies = []

    def _statevector(self, params: np.ndarray) -> np.ndarray:
        from ...core.circuit import QuantumCircuit

        circuit = QuantumCircuit(self.num_qubits)
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.num_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.num_qubits - 1):
                circuit.cnot(q, q + 1)
        for q in range(self.num_qubits):  # final rotation layer
            circuit.ry(float(params[p]), q)
            p += 1
        return circuit.get_statevector().state_vector

    def _energy(self, state: np.ndarray) -> float:
        return float(np.real(np.vdot(state, self.H @ state)))

    def _cost(self, params: np.ndarray, level: int) -> float:
        state = self._statevector(params)
        cost = self._energy(state)
        for j in range(level):
            overlap = np.abs(np.vdot(self.found_states[j], state)) ** 2
            cost += self.beta * overlap
        return cost

    def run(self, seed: Optional[int] = None) -> dict:
        """Find ``n_states`` eigenstates, lowest first."""
        from scipy.optimize import minimize

        rng = np.random.default_rng(seed)
        self.found_states = []
        self.energies = []

        for level in range(self.n_states):
            x0 = rng.uniform(0, 2 * np.pi, self.n_params)
            result = minimize(
                fun=lambda p, lvl=level: self._cost(p, lvl),
                x0=x0,
                method=self.optimizer,
                options={"maxiter": self.max_iterations},
            )
            state = self._statevector(result.x)
            self.found_states.append(state)
            self.energies.append(self._energy(state))

        return {
            "energies": self.energies,
            "states": self.found_states,
            "n_states": self.n_states,
        }

    def exact_spectrum(self) -> np.ndarray:
        """Exact eigenvalues (ascending) for reference."""
        return np.linalg.eigvalsh(self.H)
