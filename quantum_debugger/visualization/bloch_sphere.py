"""
Bloch sphere visualization for single-qubit states
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from quantum_debugger.core.quantum_state import QuantumState


class BlochSphere:
    """Bloch sphere visualization for single qubits"""

    @staticmethod
    def plot(state: QuantumState, qubit: int = 0, figsize: tuple = (8, 8)):
        """
        Plot qubit state on Bloch sphere

        Args:
            state: Quantum state
            qubit: Index of qubit to visualize (for multi-qubit systems)
            figsize: Figure size
        """
        # Get Bloch vector
        x, y, z = state.bloch_vector(qubit)

        # Create figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

        ax.plot_surface(
            x_sphere, y_sphere, z_sphere, color="lightblue", alpha=0.2, linewidth=0
        )

        # Draw axes
        axis_length = 1.3
        ax.plot([0, axis_length], [0, 0], [0, 0], "k-", linewidth=1, alpha=0.5)
        ax.plot([0, 0], [0, axis_length], [0, 0], "k-", linewidth=1, alpha=0.5)
        ax.plot([0, 0], [0, 0], [0, axis_length], "k-", linewidth=1, alpha=0.5)

        # Labels
        ax.text(axis_length, 0, 0, "X", fontsize=14, fontweight="bold")
        ax.text(0, axis_length, 0, "Y", fontsize=14, fontweight="bold")
        ax.text(0, 0, axis_length, "|0⟩", fontsize=14, fontweight="bold")
        ax.text(0, 0, -axis_length, "|1⟩", fontsize=14, fontweight="bold")

        # Draw state vector
        ax.quiver(
            0,
            0,
            0,
            x,
            y,
            z,
            color="red",
            arrow_length_ratio=0.15,
            linewidth=3,
            label="State Vector",
        )

        # Draw projection onto XY plane
        ax.plot([x, x], [y, y], [0, z], "r--", alpha=0.5, linewidth=1)
        ax.plot([0, x], [0, y], [0, 0], "r--", alpha=0.5, linewidth=1)

        # Mark poles
        ax.scatter([0], [0], [1], color="blue", s=100, marker="o", label="|0⟩")
        ax.scatter([0], [0], [-1], color="orange", s=100, marker="o", label="|1⟩")

        # Mark current state
        ax.scatter(
            [x],
            [y],
            [z],
            color="red",
            s=150,
            marker="*",
            label=f"Qubit {qubit}",
            zorder=10,
        )

        # Settings
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.set_zlabel("Z", fontsize=12)
        ax.set_title(f"Bloch Sphere - Qubit {qubit}", fontsize=16, fontweight="bold")
        ax.legend(loc="upper right")

        # Set viewing angle
        ax.view_init(elev=20, azim=45)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_trajectory(states: list, qubit: int = 0, figsize: tuple = (8, 8)):
        """
        Plot trajectory of state evolution on Bloch sphere

        Args:
            states: List of QuantumState objects
            qubit: Qubit index to visualize
            figsize: Figure size
        """
        # Get Bloch vectors for all states
        vectors = [s.bloch_vector(qubit) for s in states]
        xs, ys, zs = zip(*vectors)

        # Create figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

        ax.plot_surface(
            x_sphere, y_sphere, z_sphere, color="lightblue", alpha=0.15, linewidth=0
        )

        # Draw axes
        axis_length = 1.3
        ax.plot([0, axis_length], [0, 0], [0, 0], "k-", linewidth=1, alpha=0.5)
        ax.plot([0, 0], [0, axis_length], [0, 0], "k-", linewidth=1, alpha=0.5)
        ax.plot([0, 0], [0, 0], [0, axis_length], "k-", linewidth=1, alpha=0.5)

        # Labels
        ax.text(axis_length, 0, 0, "X", fontsize=14, fontweight="bold")
        ax.text(0, axis_length, 0, "Y", fontsize=14, fontweight="bold")
        ax.text(0, 0, axis_length, "|0⟩", fontsize=14, fontweight="bold")
        ax.text(0, 0, -axis_length, "|1⟩", fontsize=14, fontweight="bold")

        # Draw trajectory
        ax.plot(xs, ys, zs, "r-", linewidth=2, alpha=0.7, label="Trajectory")

        # Mark start and end
        ax.scatter(
            [xs[0]],
            [ys[0]],
            [zs[0]],
            color="green",
            s=150,
            marker="o",
            label="Start",
            zorder=10,
        )
        ax.scatter(
            [xs[-1]],
            [ys[-1]],
            [zs[-1]],
            color="red",
            s=150,
            marker="*",
            label="End",
            zorder=10,
        )

        # Mark intermediate points
        if len(states) > 2:
            ax.scatter(xs[1:-1], ys[1:-1], zs[1:-1], color="orange", s=50, alpha=0.6)

        # Settings
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.set_zlabel("Z", fontsize=12)
        ax.set_title(f"State Evolution - Qubit {qubit}", fontsize=16, fontweight="bold")
        ax.legend(loc="upper right")

        ax.view_init(elev=20, azim=45)

        plt.tight_layout()
        plt.show()
