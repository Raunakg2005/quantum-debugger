"""
Quantum noise models for realistic circuit simulation
"""

import numpy as np
from typing import Optional
from quantum_debugger.core.quantum_state import QuantumState


class NoiseModel:
    """Base class for all quantum noise models"""

    def apply(self, state: QuantumState, qubits: Optional[list] = None):
        """
        Apply noise to a quantum state

        Args:
            state: QuantumState to apply noise to
            qubits: Optional list of qubits to apply noise to (None = all qubits)
        """
        raise NotImplementedError("Subclasses must implement apply()")

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class DepolarizingNoise(NoiseModel):
    """
    Depolarizing channel: random Pauli errors

    With probability p, apply random Pauli (X, Y, or Z) error.
    Simulates random bit/phase flips.
    """

    def __init__(self, probability: float):
        """
        Initialize depolarizing noise

        Args:
            probability: Error probability (0 to 1)
        """
        if not 0 <= probability <= 1:
            raise ValueError(f"Probability must be in [0,1], got {probability}")
        self.probability = probability

    def apply(self, state: QuantumState, qubits: Optional[list] = None):
        """Apply depolarizing noise to state"""
        if state.state_vector is None:
            # Already using density matrix
            self._apply_to_density_matrix(state, qubits)
        else:
            # Convert to density matrix and apply
            self._convert_to_density_matrix_and_apply(state, qubits)

    def _convert_to_density_matrix_and_apply(self, state: QuantumState, qubits):
        """Convert state vector to density matrix and apply noise"""
        # Convert |ψ⟩ to ρ = |ψ⟩⟨ψ|
        psi = state.state_vector
        state.density_matrix = np.outer(psi, psi.conj())
        state.state_vector = None
        state.use_density_matrix = True

        # Now apply noise to density matrix
        self._apply_to_density_matrix(state, qubits)

    def _apply_to_density_matrix(self, state: QuantumState, qubits):
        """
        Apply depolarizing noise using Kraus operators

        ρ → (1-p)ρ + p/3(XρX + YρY + ZρZ)
        """
        p = self.probability
        rho = state.density_matrix

        if qubits is None:
            qubits = list(range(state.num_qubits))

        for qubit in qubits:
            # Pauli matrices
            X = np.array([[0, 1], [1, 0]], dtype=complex)
            Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
            Z = np.array([[1, 0], [0, -1]], dtype=complex)

            # Build full operators for the qubit
            X_full = self._build_single_qubit_operator(X, qubit, state.num_qubits)
            Y_full = self._build_single_qubit_operator(Y, qubit, state.num_qubits)
            Z_full = self._build_single_qubit_operator(Z, qubit, state.num_qubits)

            # Apply depolarizing channel
            new_rho = (1 - p) * rho
            new_rho = new_rho + (p / 3) * (X_full @ rho @ X_full.conj().T)
            new_rho = new_rho + (p / 3) * (Y_full @ rho @ Y_full.conj().T)
            new_rho = new_rho + (p / 3) * (Z_full @ rho @ Z_full.conj().T)

            rho = new_rho.astype(complex)  # Ensure complex type

        state.density_matrix = rho

    def _build_single_qubit_operator(self, gate, target_qubit, num_qubits):
        """Build full operator for single qubit gate"""
        identity = np.eye(2, dtype=complex)

        # Build tensor product: I ⊗ I ⊗ ... ⊗ gate ⊗ ... ⊗ I
        result = np.array([[1.0]], dtype=complex)
        for q in range(num_qubits):
            if q == target_qubit:
                result = np.kron(result, gate)
            else:
                result = np.kron(result, identity)

        return result

    def get_kraus_operators(self):
        """
        Get Kraus operators for stochastic sampling

        Returns:
            List of Kraus operators [K0, K1, K2, K3] for depolarizing channel
        """
        p = self.probability

        # Kraus operators: K0 = √(1-3p/4)I, K1 = √(p/4)X, K2 = √(p/4)Y, K3 = √(p/4)Z
        K0 = np.sqrt(1 - 3 * p / 4) * np.eye(2, dtype=complex)
        K1 = np.sqrt(p / 4) * np.array([[0, 1], [1, 0]], dtype=complex)  # X
        K2 = np.sqrt(p / 4) * np.array([[0, -1j], [1j, 0]], dtype=complex)  # Y
        K3 = np.sqrt(p / 4) * np.array([[1, 0], [0, -1]], dtype=complex)  # Z

        return [K0, K1, K2, K3]

    def __repr__(self):
        return f"DepolarizingNoise(p={self.probability})"


class AmplitudeDamping(NoiseModel):
    """
    Amplitude damping: Energy loss (T1 decay)

    |1⟩ can decay to |0⟩ with rate γ.
    Models spontaneous emission and energy relaxation.
    """

    def __init__(self, gamma: float):
        """
        Initialize amplitude damping

        Args:
            gamma: Damping rate (0 to 1)
        """
        if not 0 <= gamma <= 1:
            raise ValueError(f"Gamma must be in [0,1], got {gamma}")
        self.gamma = gamma

    def apply(self, state: QuantumState, qubits: Optional[list] = None):
        """Apply amplitude damping"""
        if state.state_vector is not None:
            # Convert to density matrix
            psi = state.state_vector
            state.density_matrix = np.outer(psi, psi.conj())
            state.state_vector = None
            state.use_density_matrix = True

        # Apply using Kraus operators
        gamma = self.gamma

        # Kraus operators for amplitude damping
        # K0 = [[1, 0], [0, sqrt(1-γ)]]
        # K1 = [[0, sqrt(γ)], [0, 0]]

        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
        K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)

        if qubits is None:
            qubits = list(range(state.num_qubits))

        rho = state.density_matrix

        for qubit in qubits:
            K0_full = self._build_single_qubit_operator(K0, qubit, state.num_qubits)
            K1_full = self._build_single_qubit_operator(K1, qubit, state.num_qubits)

            # ρ' = K0 ρ K0† + K1 ρ K1†
            new_rho = (
                K0_full @ rho @ K0_full.conj().T + K1_full @ rho @ K1_full.conj().T
            )
            rho = new_rho

        state.density_matrix = rho

    def _build_single_qubit_operator(self, gate, target_qubit, num_qubits):
        """Build full operator for single qubit gate"""
        identity = np.eye(2, dtype=complex)
        result = np.array([[1.0]], dtype=complex)
        for q in range(num_qubits):
            if q == target_qubit:
                result = np.kron(result, gate)
            else:
                result = np.kron(result, identity)
        return result

    def __repr__(self):
        return f"AmplitudeDamping(γ={self.gamma})"


class PhaseDamping(NoiseModel):
    """
    Phase damping: Phase coherence loss (T2 dephasing)

    Random Z rotations causing phase errors.
    Preserves populations but destroys coherence.
    """

    def __init__(self, gamma: float):
        """
        Initialize phase damping

        Args:
            gamma: Dephasing rate (0 to 1)
        """
        if not 0 <= gamma <= 1:
            raise ValueError(f"Gamma must be in [0,1], got {gamma}")
        self.gamma = gamma

    def apply(self, state: QuantumState, qubits: Optional[list] = None):
        """Apply phase damping"""
        if state.state_vector is not None:
            psi = state.state_vector
            state.density_matrix = np.outer(psi, psi.conj())
            state.state_vector = None
            state.use_density_matrix = True

        # Kraus operators for phase damping
        # K0 = [[1, 0], [0, sqrt(1-γ)]]
        # K1 = [[0, 0], [0, sqrt(γ)]]

        gamma = self.gamma
        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
        K1 = np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=complex)

        if qubits is None:
            qubits = list(range(state.num_qubits))

        rho = state.density_matrix

        for qubit in qubits:
            K0_full = self._build_single_qubit_operator(K0, qubit, state.num_qubits)
            K1_full = self._build_single_qubit_operator(K1, qubit, state.num_qubits)

            new_rho = (
                K0_full @ rho @ K0_full.conj().T + K1_full @ rho @ K1_full.conj().T
            )
            rho = new_rho

        state.density_matrix = rho

    def _build_single_qubit_operator(self, gate, target_qubit, num_qubits):
        """Build full operator for single qubit gate"""
        identity = np.eye(2, dtype=complex)
        result = np.array([[1.0]], dtype=complex)
        for q in range(num_qubits):
            if q == target_qubit:
                result = np.kron(result, gate)
            else:
                result = np.kron(result, identity)
        return result

    def __repr__(self):
        return f"PhaseDamping(γ={self.gamma})"


class ThermalRelaxation(NoiseModel):
    """
    Thermal relaxation: Combined T1 and T2 effects

    Models realistic decoherence with both amplitude and phase damping.
    Based on T1 (energy relaxation) and T2 (phase coherence) times.
    """

    def __init__(self, t1: float, t2: float, gate_time: float):
        """
        Initialize thermal relaxation

        Args:
            t1: T1 relaxation time (seconds)
            t2: T2 dephasing time (seconds), must have t2 <= 2*t1
            gate_time: Duration of the gate operation (seconds)
        """
        if t2 > 2 * t1:
            raise ValueError(f"T2 ({t2}) must be <= 2 * T1 ({2 * t1})")

        self.t1 = t1
        self.t2 = t2
        self.gate_time = gate_time

        # Calculate probabilities
        self.p_reset = 1 - np.exp(-gate_time / t1)  # Probability of |1⟩→|0⟩
        self.p_dephase = 0.5 * (1 - np.exp(-gate_time / t2))  # Pure dephasing

        # Ensure p_dephase accounts for T1 effect
        if t1 > 0:
            self.p_dephase = max(0, self.p_dephase - 0.5 * self.p_reset)

    def apply(self, state: QuantumState, qubits: Optional[list] = None):
        """Apply thermal relaxation"""
        # Apply amplitude damping (T1)
        amp_damp = AmplitudeDamping(self.p_reset)
        amp_damp.apply(state, qubits)

        # Apply phase damping (T2)
        phase_damp = PhaseDamping(self.p_dephase)
        phase_damp.apply(state, qubits)

    def __repr__(self):
        return f"ThermalRelaxation(T1={self.t1}, T2={self.t2}, time={self.gate_time})"
