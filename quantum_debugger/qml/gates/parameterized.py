"""
Parameterized Quantum Gates
============================

Gates with trainable parameters for variational quantum algorithms.
"""

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ParameterizedGate:
    """
    Base class for parameterized quantum gates.

    A parameterized gate is a quantum gate whose operation depends on one or more
    continuous parameters (e.g., rotation angles). These gates are the foundation
    of variational quantum algorithms like VQE and QAOA.

    Attributes:
        target (int): Index of the qubit this gate acts on
        parameter (float): The parameter value (e.g., rotation angle)
        trainable (bool): Whether this parameter should be optimized during training
        gradient (float): Stored gradient value for optimization
        name (str): Name of the gate (e.g., "RX", "RY", "RZ")

    Examples:
        >>> from quantum_debugger.qml import RXGate
        >>> import numpy as np
        >>>
        >>> # Create a trainable RX gate
        >>> rx = RXGate(target=0, parameter=np.pi/4, trainable=True)
        >>>
        >>> # Get the unitary matrix
        >>> U = rx.matrix()
        >>>
        >>> # Update the parameter
        >>> rx.parameter = np.pi/2
        >>>
        >>> # Store gradient from optimizer
        >>> rx.gradient = 0.123
    """

    def __init__(
        self, target: int, parameter: float, trainable: bool = True, name: str = "Param"
    ):
        """
        Initialize a parameterized gate.

        Args:
            target: Qubit index (0-based)
            parameter: Initial parameter value (typically an angle in radians)
            trainable: If True, this parameter will be optimized during training
            name: Gate name for debugging/logging

        Raises:
            ValueError: If target is negative
        """
        if target < 0:
            raise ValueError(f"Target qubit index must be non-negative, got {target}")

        self.target = target
        self.parameter = parameter
        self.trainable = trainable
        self.gradient = None
        self.name = name

        logger.info(
            f"Created {name}(target={target}, θ={parameter:.4f}, trainable={trainable})"
        )

    def matrix(self) -> np.ndarray:
        """
        Return the unitary matrix for this gate.

        Returns:
            2x2 complex numpy array representing the gate's unitary matrix
        """
        raise NotImplementedError("Subclasses must implement matrix()")

    def __repr__(self) -> str:
        return f"{self.name}(target={self.target}, θ={self.parameter:.4f}, trainable={self.trainable})"


class RXGate(ParameterizedGate):
    """
    Rotation gate around the X-axis.

    The RX gate performs a rotation around the X-axis of the Bloch sphere.

    Matrix representation:
        RX(θ) = cos(θ/2) * I - i*sin(θ/2) * X
              = [[cos(θ/2),    -i*sin(θ/2)],
                 [-i*sin(θ/2),  cos(θ/2)  ]]

    Examples:
        >>> rx = RXGate(target=0, parameter=np.pi)
        >>> U = rx.matrix()
        >>> # RX(π) = -iX (Pauli X with phase)
    """

    def __init__(self, target: int, parameter: float, trainable: bool = True):
        super().__init__(target, parameter, trainable, "RX")

    def matrix(self) -> np.ndarray:
        """Compute RX rotation matrix."""
        theta = self.parameter
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)

        return np.array(
            [[cos_half, -1j * sin_half], [-1j * sin_half, cos_half]], dtype=complex
        )


class RYGate(ParameterizedGate):
    """
    Rotation gate around the Y-axis.

    The RY gate performs a rotation around the Y-axis of the Bloch sphere.

    Matrix representation:
        RY(θ) = cos(θ/2) * I - i*sin(θ/2) * Y
              = [[cos(θ/2),  -sin(θ/2)],
                 [sin(θ/2),   cos(θ/2)]]

    Examples:
        >>> ry = RYGate(target=0, parameter=np.pi/2)
        >>> U = ry.matrix()
        >>> # Creates superposition (|0⟩ + |1⟩)/√2
    """

    def __init__(self, target: int, parameter: float, trainable: bool = True):
        super().__init__(target, parameter, trainable, "RY")

    def matrix(self) -> np.ndarray:
        """Compute RY rotation matrix."""
        theta = self.parameter
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)

        return np.array([[cos_half, -sin_half], [sin_half, cos_half]], dtype=complex)


class RZGate(ParameterizedGate):
    """
    Rotation gate around the Z-axis.

    The RZ gate performs a rotation around the Z-axis of the Bloch sphere.
    This is a phase gate that adds relative phase between |0⟩ and |1⟩.

    Matrix representation:
        RZ(θ) = [[e^(-iθ/2),    0      ],
                 [   0,      e^(iθ/2) ]]

    Examples:
        >>> rz = RZGate(target=0, parameter=np.pi/2)
        >>> U = rz.matrix()
        >>> # RZ(π/2) is the S gate
    """

    def __init__(self, target: int, parameter: float, trainable: bool = True):
        super().__init__(target, parameter, trainable, "RZ")

    def matrix(self) -> np.ndarray:
        """Compute RZ rotation matrix."""
        theta = self.parameter

        return np.array(
            [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
        )
