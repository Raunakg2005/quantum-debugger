"""
Framework Integrations

Universal compatibility layer for quantum frameworks:
- Qiskit (IBM)
- PennyLane (Xanadu)
- Cirq (Google)

All integrations are optional - quantum-debugger works standalone.
"""

from .qiskit_bridge import from_qiskit, to_qiskit, QISKIT_AVAILABLE
from .pennylane_bridge import from_pennylane, to_pennylane, PENNYLANE_AVAILABLE
from .cirq_bridge import from_cirq, to_cirq, CIRQ_AVAILABLE
from .cirq_adapter import CirqAdapter
from .qiskit_adapter import QiskitAdapter

__all__ = [
    # Adapters
    "CirqAdapter",
    "QiskitAdapter",
    # Qiskit
    "from_qiskit",
    "to_qiskit",
    "QISKIT_AVAILABLE",
    # PennyLane
    "from_pennylane",
    "to_pennylane",
    "PENNYLANE_AVAILABLE",
    # Cirq
    "from_cirq",
    "to_cirq",
    "CIRQ_AVAILABLE",
]


def get_available_frameworks():
    """Get list of available quantum frameworks."""
    frameworks = []
    if QISKIT_AVAILABLE:
        frameworks.append("qiskit")
    if PENNYLANE_AVAILABLE:
        frameworks.append("pennylane")
    if CIRQ_AVAILABLE:
        frameworks.append("cirq")
    return frameworks
