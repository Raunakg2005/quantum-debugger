"""
Quantum state visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
from quantum_debugger.core.quantum_state import QuantumState


class StateVisualizer:
    """Visualize quantum states"""

    @staticmethod
    def plot_state_vector(
        state: QuantumState, show_phase: bool = True, figsize: tuple = (12, 5)
    ):
        """
        Plot state vector amplitudes and phases

        Args:
            state: Quantum state to visualize
            show_phase: Whether to show phase information
            figsize: Figure size
        """
        probabilities = state.get_probabilities()
        amplitudes = np.abs(state.state_vector)
        phases = np.angle(state.state_vector)

        # Basis state labels
        labels = [format(i, f"0{state.num_qubits}b") for i in range(state.dim)]
        x = np.arange(state.dim)

        if show_phase:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

            # Amplitudes
            ax1.bar(x, amplitudes, color="steelblue", alpha=0.7)
            ax1.set_xlabel("Basis State")
            ax1.set_ylabel("Amplitude")
            ax1.set_title("State Vector Amplitudes")
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels, rotation=45, ha="right")
            ax1.grid(True, alpha=0.3)

            # Phases
            colors = plt.cm.hsv(phases / (2 * np.pi) + 0.5)
            ax2.bar(x, amplitudes, color=colors, alpha=0.7)
            ax2.set_xlabel("Basis State")
            ax2.set_ylabel("Amplitude")
            ax2.set_title("Phases (color-coded)")
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels, rotation=45, ha="right")
            ax2.grid(True, alpha=0.3)

        else:
            fig, ax = plt.subplots(figsize=(figsize[0] // 2, figsize[1]))
            ax.bar(x, amplitudes, color="steelblue", alpha=0.7)
            ax.set_xlabel("Basis State")
            ax.set_ylabel("Amplitude")
            ax.set_title("State Vector Amplitudes")
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha="right")
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_probabilities(state: QuantumState, figsize: tuple = (10, 6)):
        """
        Plot measurement probabilities

        Args:
            state: Quantum state
            figsize: Figure size
        """
        probabilities = state.get_probabilities()
        labels = [format(i, f"0{state.num_qubits}b") for i in range(state.dim)]
        x = np.arange(state.dim)

        plt.figure(figsize=figsize)
        bars = plt.bar(x, probabilities, color="coral", alpha=0.7, edgecolor="darkred")

        # Highlight most probable states
        max_prob = np.max(probabilities)
        for i, (bar, prob) in enumerate(zip(bars, probabilities)):
            if prob > max_prob * 0.9:
                bar.set_color("darkred")
                bar.set_alpha(0.9)

        plt.xlabel("Basis State", fontsize=12)
        plt.ylabel("Probability", fontsize=12)
        plt.title("Measurement Probabilities", fontsize=14, fontweight="bold")
        plt.xticks(x, labels, rotation=45, ha="right")
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_density_matrix(state: QuantumState, figsize: tuple = (10, 8)):
        """
        Plot density matrix representation

        Args:
            state: Quantum state
            figsize: Figure size
        """
        # Create density matrix
        rho = np.outer(state.state_vector, state.state_vector.conj())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Real part
        im1 = ax1.imshow(np.real(rho), cmap="RdBu", vmin=-1, vmax=1)
        ax1.set_title("Density Matrix (Real Part)")
        ax1.set_xlabel("Basis State")
        ax1.set_ylabel("Basis State")
        plt.colorbar(im1, ax=ax1)

        # Imaginary part
        im2 = ax2.imshow(np.imag(rho), cmap="RdBu", vmin=-1, vmax=1)
        ax2.set_title("Density Matrix (Imaginary Part)")
        ax2.set_xlabel("Basis State")
        ax2.set_ylabel("Basis State")
        plt.colorbar(im2, ax=ax2)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_qubit_probabilities(state: QuantumState, figsize: tuple = (10, 6)):
        """
        Plot per-qubit measurement probabilities

        Args:
            state: Quantum state
            figsize: Figure size
        """
        qubits = range(state.num_qubits)
        prob_0 = []
        prob_1 = []

        for q in qubits:
            p0 = state.get_measurement_probability(q, 0)
            p1 = state.get_measurement_probability(q, 1)
            prob_0.append(p0)
            prob_1.append(p1)

        x = np.arange(state.num_qubits)
        width = 0.35

        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(x - width / 2, prob_0, width, label="|0⟩", color="steelblue", alpha=0.8)
        ax.bar(x + width / 2, prob_1, width, label="|1⟩", color="coral", alpha=0.8)

        ax.set_xlabel("Qubit Index", fontsize=12)
        ax.set_ylabel("Probability", fontsize=12)
        ax.set_title(
            "Per-Qubit Measurement Probabilities", fontsize=14, fontweight="bold"
        )
        ax.set_xticks(x)
        ax.set_xticklabels([f"q{i}" for i in qubits])
        ax.legend()
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_state_comparison(
        state1: QuantumState,
        state2: QuantumState,
        labels: tuple = ("State 1", "State 2"),
        figsize: tuple = (12, 6),
    ):
        """
        Compare two quantum states

        Args:
            state1: First quantum state
            state2: Second quantum state
            labels: Labels for the states
            figsize: Figure size
        """
        if state1.num_qubits != state2.num_qubits:
            raise ValueError("States must have same number of qubits")

        prob1 = state1.get_probabilities()
        prob2 = state2.get_probabilities()

        basis_labels = [format(i, f"0{state1.num_qubits}b") for i in range(state1.dim)]
        x = np.arange(state1.dim)
        width = 0.35

        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(x - width / 2, prob1, width, label=labels[0], alpha=0.8)
        ax.bar(x + width / 2, prob2, width, label=labels[1], alpha=0.8)

        ax.set_xlabel("Basis State")
        ax.set_ylabel("Probability")
        ax.set_title("State Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(basis_labels, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.show()
