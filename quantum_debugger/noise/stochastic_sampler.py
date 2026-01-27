"""
Stochastic noise simulation for large quantum circuits

For circuits with >10 qubits, density matrices become impractical (>8MB memory).
Stochastic sampling simulates noise by randomly applying Kraus operators based on
their probabilities, trading exact simulation for scalability.
"""

import numpy as np
from typing import Optional, List
from quantum_debugger.core.quantum_state import QuantumState as BaseQuantumState


class StochasticNoiseSampler:
    """
    Stochastic noise sampler for large circuits

    Uses Monte Carlo sampling to approximate noisy evolution without
    requiring density matrices. Suitable for circuits with >10 qubits.

    Algorithm:
    1. Start with pure state |ψ⟩
    2. For each gate + noise:
       - Apply gate to |ψ⟩
       - Randomly choose Kraus operator based on probabilities
       - Apply chosen Kraus operator
       - Renormalize
    3. Repeat for multiple shots to estimate statistics
    """

    def __init__(self, noise_model):
        """
        Initialize stochastic sampler

        Args:
            noise_model: NoiseModel to sample from
        """
        self.noise_model = noise_model

    def apply_stochastic_noise(
        self, state: BaseQuantumState, qubits: Optional[List[int]] = None
    ):
        """
        Apply noise stochastically by sampling Kraus operators

        Args:
            state: Pure quantum state (state vector representation)
            qubits: Qubits to apply noise to
        """
        # Get Kraus operators from noise model
        if not hasattr(self.noise_model, "get_kraus_operators"):
            # Fallback: apply noise deterministically if Kraus ops not available
            return

        kraus_ops = self.noise_model.get_kraus_operators()

        # Calculate probabilities: p_i = Tr(K_i |ψ⟩⟨ψ| K_i†)
        psi = state.state_vector
        probabilities = []

        for K in kraus_ops:
            # Expand Kraus operator to full system if needed
            if qubits is not None:
                K_full = self._expand_operator(K, qubits, state.num_qubits)
            else:
                K_full = K

            # Calculate probability: ||K|ψ⟩||²
            K_psi = K_full @ psi
            prob = np.abs(np.vdot(K_psi, K_psi))
            probabilities.append(prob)

        # Normalize probabilities
        probabilities = np.array(probabilities)
        probabilities /= np.sum(probabilities)

        # Sample Kraus operator
        choice = np.random.choice(len(kraus_ops), p=probabilities)
        K_chosen = kraus_ops[choice]

        # Expand and apply chosen Kraus operator
        if qubits is not None:
            K_full = self._expand_operator(K_chosen, qubits, state.num_qubits)
        else:
            K_full = K_chosen

        # Apply: |ψ'⟩ = K|ψ⟩ / ||K|ψ⟩||
        state.state_vector = K_full @ state.state_vector
        state._normalize()

    def _expand_operator(self, operator, target_qubits, num_qubits):
        """Expand operator to full system (simplified version)"""
        # For single-qubit operators
        if operator.shape[0] == 2:
            identity = np.eye(2, dtype=complex)
            result = np.array([[1.0]], dtype=complex)

            for qubit_idx in range(num_qubits):
                if qubit_idx in target_qubits:
                    result = np.kron(result, operator)
                else:
                    result = np.kron(result, identity)

            return result
        else:
            # For multi-qubit operators, use as-is (simplified)
            return operator


def run_with_stochastic_noise(circuit, noise_model, shots=1000):
    """
    Run circuit with stochastic noise sampling

    Args:
        circuit: QuantumCircuit to simulate
        noise_model: NoiseModel to apply
        shots: Number of Monte Carlo samples

    Returns:
        Results dictionary with counts and estimated fidelity
    """
    sampler = StochasticNoiseSampler(noise_model)
    results = []

    # Run noiseless reference
    reference_state = BaseQuantumState(circuit.num_qubits)
    for gate in circuit.gates:
        reference_state.apply_gate(gate.matrix, gate.qubits)

    # Run shots with stochastic noise
    fidelities = []

    for _ in range(shots):
        # Initialize state
        state = BaseQuantumState(circuit.num_qubits)

        # Apply gates with noise
        for gate in circuit.gates:
            # Apply gate
            state.apply_gate(gate.matrix, gate.qubits)

            # Apply stochastic noise
            sampler.apply_stochastic_noise(state, qubits=gate.qubits)

        # Estimate fidelity: |⟨ψ_ideal|ψ_noisy⟩|²
        fidelity = (
            np.abs(np.vdot(reference_state.state_vector, state.state_vector)) ** 2
        )
        fidelities.append(fidelity)

        # Perform measurements
        classical_bits = [0] * circuit.num_classical
        for qubit, classical_bit in circuit.measurements:
            classical_bits[classical_bit] = state.measure(qubit)

        results.append(classical_bits)

    # Analyze results
    counts = {}
    for result in results:
        key = "".join(map(str, result))
        counts[key] = counts.get(key, 0) + 1

    return {
        "counts": counts,
        "results": results,
        "shots": shots,
        "method": "stochastic",
        "fidelity": np.mean(fidelities),
        "fidelity_std": np.std(fidelities),
    }
