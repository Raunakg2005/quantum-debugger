"""
IBM Quantum Backend

Interface to IBM Quantum cloud services (https://quantum.ibm.com)

REQUIRES: User must have IBM Quantum account and API token
FREE TIER AVAILABLE: https://quantum.ibm.com (sign up for free)

Usage:
    1. Sign up at https://quantum.ibm.com
    2. Get your API token from account settings
    3. Use token to connect
"""

import logging
from typing import Dict, List

from .base_backend import QuantumBackend

logger = logging.getLogger(__name__)

# Check if Qiskit is available
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit import transpile

    IBM_AVAILABLE = True
except ImportError:
    IBM_AVAILABLE = False
    logger.debug(
        "IBM Quantum not available. Install with: pip install qiskit-ibm-runtime"
    )


class IBMQuantumBackend(QuantumBackend):
    """
    IBM Quantum cloud backend.

    Provides access to real IBM quantum computers and simulators.

    FREE TIER:
    - 10 minutes/month execution time
    - Access to 5-127 qubit systems
    - Unlimited simulator access

    Examples:
        >>> # Get free API token from https://quantum.ibm.com
        >>> backend = IBMQuantumBackend()
        >>> backend.connect({'token': 'YOUR_IBM_TOKEN'})
        >>>
        >>> # Execute circuit
        >>> gates = [('h', 0), ('cnot', (0, 1))]
        >>> counts = backend.execute(gates, n_shots=1024)
    """

    def __init__(self):
        """Initialize IBM Quantum backend."""
        super().__init__(name="ibm_quantum")

        if not IBM_AVAILABLE:
            raise ImportError(
                "Qiskit IBM Runtime not installed. "
                "Install with: pip install qiskit-ibm-runtime"
            )

        self.service = None
        self.current_device = None
        self.is_available = IBM_AVAILABLE

    def connect(self, credentials: Dict[str, str]):
        """
        Connect to IBM Quantum.

        Args:
            credentials: Must contain 'token' key with IBM Quantum API token

        Raises:
            ValueError: If token not provided
            RuntimeError: If connection fails

        Examples:
            >>> backend.connect({'token': 'your_ibm_token_here'})
        """
        if "token" not in credentials:
            raise ValueError(
                "IBM Quantum token required. Get free token at https://quantum.ibm.com"
            )

        try:
            # Save credentials and initialize service
            QiskitRuntimeService.save_account(
                token=credentials["token"], overwrite=True
            )

            self.service = QiskitRuntimeService()
            self.is_connected = True

            logger.info("Connected to IBM Quantum successfully")

        except Exception as e:
            raise RuntimeError(f"Failed to connect to IBM Quantum: {e}")

    def execute(
        self, circuit_gates: List, n_shots: int = 1024, device: str = None
    ) -> Dict[str, int]:
        """
        Execute circuit on IBM Quantum hardware.

        Args:
            circuit_gates: Circuit in quantum-debugger format
            n_shots: Number of measurement shots
            device: Device name (e.g., 'ibm_brisbane'). If None, uses least busy.

        Returns:
            Measurement counts

        Examples:
            >>> gates = [('h', 0), ('x', 1), ('cnot', (0, 1))]
            >>> counts = backend.execute(gates, n_shots=1000, device='ibm_kyoto')
        """
        if not self.is_connected:
            raise RuntimeError("Not connected. Call connect() first.")

        # Convert to Qiskit circuit
        from quantum_debugger.integrations import to_qiskit

        qc = to_qiskit(circuit_gates)
        qc.measure_all()

        # Get backend
        if device is None:
            # Get least busy device
            device = self.service.least_busy(operational=True, simulator=False)
        else:
            device = self.service.backend(device)

        # Transpile for hardware
        transpiled = transpile(qc, backend=device, optimization_level=2)

        # Execute
        job = device.run(transpiled, shots=n_shots)
        result = job.result()
        counts = result.get_counts()

        logger.info(f"Executed on {device.name}: {n_shots} shots")

        return counts

    def get_available_devices(self) -> List[str]:
        """
        Get list of available IBM Quantum devices.

        Returns:
            List of device names
        """
        if not self.is_connected:
            raise RuntimeError("Not connected")

        backends = self.service.backends(simulator=False, operational=True)
        return [b.name for b in backends]

    def get_device_info(self, device_name: str) -> Dict:
        """
        Get information about IBM Quantum device.

        Args:
            device_name: Name of device

        Returns:
            Device information dictionary
        """
        if not self.is_connected:
            raise RuntimeError("Not connected")

        backend = self.service.backend(device_name)
        config = backend.configuration()

        return {
            "name": backend.name,
            "n_qubits": config.n_qubits,
            "basis_gates": config.basis_gates,
            "coupling_map": config.coupling_map,
            "simulator": backend.simulator,
            "operational": backend.status().operational,
            "pending_jobs": backend.status().pending_jobs,
        }

    def get_free_tier_info(self) -> Dict:
        """
        Get information about free tier usage.

        Returns:
            Dictionary with free tier limits and current usage
        """
        return {
            "monthly_limit_minutes": 10,
            "cost_per_minute": 0.0,  # Free!
            "available_qubits": "5-127",
            "how_to_sign_up": "https://quantum.ibm.com",
        }


def is_ibm_available() -> bool:
    """Check if IBM Quantum backend is available."""
    return IBM_AVAILABLE
