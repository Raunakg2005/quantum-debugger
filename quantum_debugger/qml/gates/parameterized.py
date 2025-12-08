"""
Parameterized Quantum Gates
============================

Gates with trainable parameters for variational quantum algorithms.
"""

import numpy as np
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ParameterizedGate:
    """Base class for quantum gates with trainable parameters
    
    Attributes:
        target (int): Target qubit index
        parameter (float): Gate parameter (typically rotation angle in radians)
        trainable (bool): Whether this parameter can be trained
        gradient (Optional[float]): Computed gradient value
        name (str): Gate name
    
    Example:
        >>> gate = RXGate(target=0, parameter=np.pi/4, trainable=True)
        >>> matrix = gate.matrix()
        >>> gate.parameter = np.pi/2  # Update parameter
    """
    
    def __init__(
        self,
        target: int,
        parameter: float = 0.0,
        trainable: bool = True,
        name: str = "Parameterized"
    ):
        """Initialize parameterized gate
        
        Args:
            target: Target qubit index (0-indexed)
            parameter: Initial parameter value in radians
            trainable: Whether parameter can be optimized
            name: Gate name for debugging
        
        Raises:
            ValueError: If target qubit index is negative
        """
        if target < 0:
            raise ValueError(f"Target qubit index must be non-negative, got {target}")
        
        self.target = target
        self.parameter = parameter
        self.trainable = trainable
        self.gradient: Optional[float] = None
        self.name = name
        
        logger.debug(f"Created {self.name} gate on qubit {target} with θ={parameter:.4f}")
    
    def matrix(self) -> np.ndarray:
        """Return the unitary matrix for this gate
        
        Returns:
            2x2 unitary matrix
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement matrix()")
    
    def __repr__(self) -> str:
        return f"{self.name}(target={self.target}, θ={self.parameter:.4f}, trainable={self.trainable})"


class RXGate(ParameterizedGate):
    """Rotation around X-axis: RX(θ)
    
    Matrix:
        RX(θ) = [[cos(θ/2),    -i*sin(θ/2)],
                 [-i*sin(θ/2),  cos(θ/2)   ]]
    
    Effect:
        Rotates qubit state around X-axis of Bloch sphere
    
    Example:
        >>> rx = RXGate(target=0, parameter=np.pi)  # X gate
        >>> rx_half = RXGate(target=1, parameter=np.pi/2)
    """
    
    def __init__(self, target: int, parameter: float = 0.0, trainable: bool = True):
        super().__init__(target, parameter, trainable, name="RX")
    
    def matrix(self) -> np.ndarray:
        """Return RX(θ) matrix
        
        Returns:
            2x2 complex unitary matrix
        """
        theta = self.parameter
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)
        
        return np.array([
            [cos_half, -1j * sin_half],
            [-1j * sin_half, cos_half]
        ], dtype=complex)


class RYGate(ParameterizedGate):
    """Rotation around Y-axis: RY(θ)
    
    Matrix:
        RY(θ) = [[cos(θ/2),  -sin(θ/2)],
                 [sin(θ/2),   cos(θ/2)]]
    
    Effect:
        Rotates qubit state around Y-axis of Bloch sphere
    
    Example:
        >>> ry = RYGate(target=0, parameter=np.pi/4)
    """
    
    def __init__(self, target: int, parameter: float = 0.0, trainable: bool = True):
        super().__init__(target, parameter, trainable, name="RY")
    
    def matrix(self) -> np.ndarray:
        """Return RY(θ) matrix
        
        Returns:
            2x2 real unitary matrix
        """
        theta = self.parameter
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)
        
        return np.array([
            [cos_half, -sin_half],
            [sin_half, cos_half]
        ], dtype=complex)


class RZGate(ParameterizedGate):
    """Rotation around Z-axis: RZ(θ)
    
    Matrix:
        RZ(θ) = [[e^(-iθ/2),  0        ],
                 [0,          e^(iθ/2) ]]
    
    Effect:
        Rotates qubit state around Z-axis of Bloch sphere (phase rotation)
    
    Example:
        >>> rz = RZGate(target=0, parameter=np.pi)  # Z gate
        >>> s_gate = RZGate(target=1, parameter=np.pi/2)  # S gate
    """
    
    def __init__(self, target: int, parameter: float = 0.0, trainable: bool = True):
        super().__init__(target, parameter, trainable, name="RZ")
    
    def matrix(self) -> np.ndarray:
        """Return RZ(θ) matrix
        
        Returns:
            2x2 complex diagonal unitary matrix
        """
        theta = self.parameter
        
        return np.array([
            [np.exp(-1j * theta / 2), 0],
            [0, np.exp(1j * theta / 2)]
        ], dtype=complex)
