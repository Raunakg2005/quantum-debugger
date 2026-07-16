"""
Quantum Kernel Computation

Implements quantum kernel methods for computing similarity
between data points using quantum circuits.
"""

import numpy as np
from typing import Optional
from abc import ABC, abstractmethod


class QuantumKernel(ABC):
    """
    Base class for quantum kernels

    A quantum kernel measures similarity between data points
    by encoding them into quantum states and computing overlaps.
    """

    def __init__(self, feature_map: str = "zz", n_qubits: int = 4, reps: int = 2):
        self.feature_map = feature_map
        self.n_qubits = n_qubits
        self.reps = reps
        self._kernel_cache = {}
        self._state_cache = {}

    def _build_feature_circuit(self, x: np.ndarray):
        """
        Build the feature-map circuit U(x) that prepares |phi(x)> = U(x)|0>.

        Uses the real feature-map circuits from qml.data.feature_maps rather than
        any analytic approximation.
        """
        from ..data.feature_maps import get_feature_map

        x = np.asarray(x, dtype=float).ravel()
        # Match the feature vector to the qubit count (pad / truncate).
        if x.shape[0] < self.n_qubits:
            x = np.concatenate([x, np.zeros(self.n_qubits - x.shape[0])])
        else:
            x = x[: self.n_qubits]

        if self.feature_map in ("zz", "pauli"):
            fm = get_feature_map(self.feature_map, self.n_qubits, reps=self.reps)
        else:  # angle encoding (no reps argument)
            fm = get_feature_map("angle", self.n_qubits)
        return fm(x)

    def _feature_qstate(self, x: np.ndarray):
        """Simulate U(x)|0> and return the resulting QuantumState (cached by x)."""
        key = tuple(np.asarray(x, dtype=float).ravel()[: self.n_qubits])
        cached = self._state_cache.get(key)
        if cached is None:
            cached = self._build_feature_circuit(x).get_statevector()
            self._state_cache[key] = cached
        return cached

    def _feature_state(self, x: np.ndarray) -> np.ndarray:
        """State vector for |phi(x)>."""
        return self._feature_qstate(x).state_vector

    @abstractmethod
    def compute_kernel_element(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Compute single kernel element K(x1, x2)

        Args:
            x1: First data point
            x2: Second data point

        Returns:
            Kernel value (similarity)
        """
        pass

    def compute_kernel_matrix(
        self, X1: np.ndarray, X2: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute kernel matrix between datasets

        Args:
            X1: First dataset (n_samples1, n_features)
            X2: Second dataset (n_samples2, n_features), or None for X1==X2

        Returns:
            Kernel matrix (n_samples1, n_samples2)
        """
        if X2 is None:
            X2 = X1
            symmetric = True
        else:
            symmetric = False

        n1, n2 = len(X1), len(X2)
        K = np.zeros((n1, n2))

        for i in range(n1):
            for j in range(n2):
                # Use symmetry to avoid redundant computation
                if symmetric and j < i:
                    K[i, j] = K[j, i]
                else:
                    # Check cache
                    cache_key = (tuple(X1[i]), tuple(X2[j]))
                    if cache_key in self._kernel_cache:
                        K[i, j] = self._kernel_cache[cache_key]
                    else:
                        k_val = self.compute_kernel_element(X1[i], X2[j])
                        K[i, j] = k_val
                        self._kernel_cache[cache_key] = k_val

        return K

    def clear_cache(self):
        """Clear kernel and feature-state caches"""
        self._kernel_cache = {}
        self._state_cache = {}

    def encode_data(self, x: np.ndarray) -> np.ndarray:
        """
        Encode classical data into quantum state parameters

        Args:
            x: Classical data point

        Returns:
            Quantum encoding parameters
        """
        if self.feature_map == "zz":
            # ZZ feature map with entanglement
            params = []
            for _ in range(self.reps):
                params.extend(x[: self.n_qubits])
            return np.array(params)

        elif self.feature_map == "pauli":
            # Pauli feature map
            return x[: self.n_qubits] * np.pi

        elif self.feature_map == "angle":
            # Simple angle encoding
            return x[: self.n_qubits]

        else:
            return x[: self.n_qubits]


class FidelityKernel(QuantumKernel):
    """
    Quantum kernel based on state fidelity

    K(x1, x2) = |⟨φ(x1)|φ(x2)⟩|²

    where |φ(x)⟩ is the quantum state encoding x.
    """

    def compute_kernel_element(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Compute the fidelity kernel element by simulating the feature-map circuits.

        K(x1, x2) = |<phi(x1)|phi(x2)>|^2, where |phi(x)> = U(x)|0> is produced by
        the real feature-map circuit. This Gram matrix is symmetric and positive
        semdefinite (Schur product theorem), so it is a valid kernel.

        Args:
            x1: First data point
            x2: Second data point

        Returns:
            Kernel value (state fidelity) in [0, 1]
        """
        state1 = self._feature_state(x1)
        state2 = self._feature_state(x2)
        overlap = np.vdot(state1, state2)
        return float(np.abs(overlap) ** 2)


class ProjectedKernel(QuantumKernel):
    """
    Projected quantum kernel

    K(x1, x2) = ⟨φ(x1)|M|φ(x2)⟩

    where M is a measurement operator.
    """

    def __init__(
        self,
        feature_map: str = "zz",
        n_qubits: int = 4,
        reps: int = 2,
        measurement_basis: str = "z",
        gamma: float = 1.0,
    ):
        super().__init__(feature_map, n_qubits, reps)
        self.measurement_basis = measurement_basis
        self.gamma = gamma

    def compute_kernel_element(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Projected quantum kernel (Huang et al. 2021).

        K(x1, x2) = exp(-gamma * sum_q ||rho_q(x1) - rho_q(x2)||_F^2), where
        rho_q(x) is the single-qubit reduced density matrix of |phi(x)> on qubit
        q, obtained by partial trace of the simulated feature state. Using Bloch
        vectors r_q, ||rho_q(x1) - rho_q(x2)||_F^2 = 0.5 * ||r_q(x1) - r_q(x2)||^2.

        Args:
            x1: First data point
            x2: Second data point

        Returns:
            Kernel value in (0, 1]
        """
        state1 = self._feature_qstate(x1)
        state2 = self._feature_qstate(x2)

        distance = 0.0
        for qubit in range(self.n_qubits):
            r1 = np.array(state1.bloch_vector(qubit))
            r2 = np.array(state2.bloch_vector(qubit))
            distance += 0.5 * np.sum((r1 - r2) ** 2)

        return float(np.exp(-self.gamma * distance))


def compute_gram_matrix(X: np.ndarray, kernel: QuantumKernel) -> np.ndarray:
    """
    Compute Gram (kernel) matrix for dataset

    Args:
        X: Dataset (n_samples, n_features)
        kernel: Quantum kernel instance

    Returns:
        Gram matrix (n_samples, n_samples)
    """
    return kernel.compute_kernel_matrix(X, X)


def kernel_centering(K: np.ndarray) -> np.ndarray:
    """
    Center kernel matrix

    Args:
        K: Kernel matrix (n, n)

    Returns:
        Centered kernel matrix
    """
    n = K.shape[0]
    one_n = np.ones((n, n)) / n
    K_centered = K - one_n @ K - K @ one_n + one_n @ K @ one_n
    return K_centered
