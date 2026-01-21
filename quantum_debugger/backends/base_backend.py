"""
Base Quantum Backend Interface

Abstract base class for quantum hardware backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class QuantumBackend(ABC):
    """
    Abstract base class for quantum hardware backends.

    All backend implementations must inherit from this class.
    """

    def __init__(self, name: str):
        """
        Initialize backend.

        Args:
            name: Backend name
        """
        self.name = name
        self.is_available = False
        self.is_connected = False

    @abstractmethod
    def connect(self, credentials: Dict[str, str]):
        """
        Connect to quantum backend.

        Args:
            credentials: API credentials (token, secret, etc.)
        """
        pass

    @abstractmethod
    def execute(self, circuit_gates: List, n_shots: int = 1024) -> Dict[str, int]:
        """
        Execute circuit on quantum hardware.

        Args:
            circuit_gates: Circuit in quantum-debugger format
            n_shots: Number of measurement shots

        Returns:
            Measurement counts dictionary
        """
        pass

    @abstractmethod
    def get_available_devices(self) -> List[str]:
        """Get list of available quantum devices."""
        pass

    @abstractmethod
    def get_device_info(self, device_name: str) -> Dict:
        """Get information about specific device."""
        pass

    def disconnect(self):
        """Disconnect from backend."""
        self.is_connected = False

    def __repr__(self):
        status = "connected" if self.is_connected else "disconnected"
        return f"{self.__class__.__name__}(name='{self.name}', status='{status}')"
