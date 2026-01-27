"""
State inspection utilities for debugging
"""

import numpy as np
from typing import Dict, List, Tuple
from quantum_debugger.core.quantum_state import QuantumState


class StateInspector:
    """Utilities for inspecting quantum states during debugging"""

    @staticmethod
    def get_state_summary(state: QuantumState) -> Dict:
        """
        Get a comprehensive summary of a quantum state

        Args:
            state: Quantum state to inspect

        Returns:
            Dictionary with state information
        """
        probabilities = state.get_probabilities()

        summary = {
            "num_qubits": state.num_qubits,
            "dimension": state.dim,
            "norm": np.linalg.norm(state.state_vector),
            "entropy": state.entropy(),
            "is_entangled": state.is_entangled() if state.num_qubits == 2 else None,
            "max_amplitude": float(np.max(np.abs(state.state_vector))),
            "nonzero_amplitudes": int(np.sum(np.abs(state.state_vector) > 1e-10)),
            "most_likely_state": int(np.argmax(probabilities)),
            "max_probability": float(np.max(probabilities)),
        }

        return summary

    @staticmethod
    def get_measurement_stats(state: QuantumState) -> Dict[str, float]:
        """
        Get measurement statistics for all computational basis states

        Args:
            state: Quantum state

        Returns:
            Dictionary mapping basis states to probabilities
        """
        probabilities = state.get_probabilities()
        stats = {}

        for i, prob in enumerate(probabilities):
            if prob > 1e-10:  # Only include non-negligible probabilities
                binary = format(i, f"0{state.num_qubits}b")
                stats[binary] = float(prob)

        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def get_qubit_probabilities(state: QuantumState, qubit: int) -> Tuple[float, float]:
        """
        Get measurement probabilities for a specific qubit

        Args:
            state: Quantum state
            qubit: Qubit index

        Returns:
            (probability of 0, probability of 1)
        """
        prob_0 = state.get_measurement_probability(qubit, 0)
        prob_1 = state.get_measurement_probability(qubit, 1)
        return (prob_0, prob_1)

    @staticmethod
    def get_amplitude_info(state: QuantumState) -> List[Dict]:
        """
        Get detailed amplitude information for all basis states

        Args:
            state: Quantum state

        Returns:
            List of dictionaries with amplitude information
        """
        amplitudes = []

        for i, amplitude in enumerate(state.state_vector):
            if abs(amplitude) > 1e-10:
                binary = format(i, f"0{state.num_qubits}b")
                amplitudes.append(
                    {
                        "basis_state": binary,
                        "index": i,
                        "amplitude": complex(amplitude),
                        "magnitude": float(abs(amplitude)),
                        "phase": float(np.angle(amplitude)),
                        "probability": float(abs(amplitude) ** 2),
                    }
                )

        return sorted(amplitudes, key=lambda x: x["probability"], reverse=True)

    @staticmethod
    def compare_states(state1: QuantumState, state2: QuantumState) -> Dict:
        """
        Compare two quantum states

        Args:
            state1: First quantum state
            state2: Second quantum state

        Returns:
            Dictionary with comparison metrics
        """
        if state1.num_qubits != state2.num_qubits:
            raise ValueError("States must have same number of qubits")

        fidelity = state1.fidelity(state2)

        # Calculate trace distance
        trace_distance = np.linalg.norm(
            state1.state_vector - state2.state_vector
        ) / np.sqrt(2)

        return {
            "fidelity": float(fidelity),
            "trace_distance": float(trace_distance),
            "are_equal": fidelity > 0.9999,
        }

    @staticmethod
    def check_superposition(
        state: QuantumState, qubit: int, threshold: float = 0.1
    ) -> bool:
        """
        Check if a qubit is in superposition

        Args:
            state: Quantum state
            qubit: Qubit index
            threshold: Threshold for considering a state in superposition

        Returns:
            True if qubit is in superposition
        """
        prob_0, prob_1 = StateInspector.get_qubit_probabilities(state, qubit)

        # In superposition if neither probability is close to 0 or 1
        return threshold < prob_0 < (1 - threshold) and threshold < prob_1 < (
            1 - threshold
        )

    @staticmethod
    def format_state_string(state: QuantumState, max_terms: int = 10) -> str:
        """
        Format quantum state as readable string

        Args:
            state: Quantum state
            max_terms: Maximum number of terms to show

        Returns:
            Formatted string representation
        """
        amplitudes = StateInspector.get_amplitude_info(state)

        if not amplitudes:
            return "|0>"

        terms = []
        for amp_info in amplitudes[:max_terms]:
            magnitude = amp_info["magnitude"]
            phase = amp_info["phase"]
            basis = amp_info["basis_state"]

            # Format coefficient
            if abs(phase) < 1e-10:
                coef = f"{magnitude:.3f}"
            elif abs(phase - np.pi) < 1e-10:
                coef = f"-{magnitude:.3f}"
            else:
                coef = f"{magnitude:.3f}e^({phase:.2f}i)"

            terms.append(f"{coef}|{basis}>")

        if len(amplitudes) > max_terms:
            terms.append("...")

        return " + ".join(terms)

    @staticmethod
    def print_state_info(state: QuantumState):
        """
        Print comprehensive state information to console

        Args:
            state: Quantum state to inspect
        """
        print("=" * 60)
        print("QUANTUM STATE INSPECTION")
        print("=" * 60)

        summary = StateInspector.get_state_summary(state)
        print(f"\nState Vector: {StateInspector.format_state_string(state)}")
        print(f"\nNumber of Qubits: {summary['num_qubits']}")
        print(f"Dimension: {summary['dimension']}")
        print(f"Entropy: {summary['entropy']:.4f}")

        if summary["is_entangled"] is not None:
            print(f"Entangled: {summary['is_entangled']}")

        print("\nMeasurement Statistics:")
        stats = StateInspector.get_measurement_stats(state)
        for basis_state, prob in list(stats.items())[:5]:
            print(f"  |{basis_state}>: {prob:.4f} ({prob * 100:.2f}%)")

        print("\nPer-Qubit Probabilities:")
        for q in range(state.num_qubits):
            prob_0, prob_1 = StateInspector.get_qubit_probabilities(state, q)
            print(f"  Qubit {q}: |0>={prob_0:.4f}, |1>={prob_1:.4f}")

        print("=" * 60)
