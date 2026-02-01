"""
Ansatz module for variational quantum circuits

Provides various ansatz (trial wavefunctions) for VQE and QAOA.
"""

# Import new ansatz types
from .real_amplitudes import real_amplitudes
from .two_local import two_local
from .excitation_preserving import excitation_preserving
from .strongly_entangling import strongly_entangling


# Keep existing hardware_efficient for backward compatibility
def hardware_efficient_ansatz(num_qubits: int, depth: int = 0):
    """
    Hardware-efficient ansatz with RY rotations and CNOT entanglement

    Args:
        num_qubits: Number of qubits
        depth: Circuit depth (number of layers)
    """

    def build(params):
        from ...core.circuit import QuantumCircuit

        circuit = QuantumCircuit(num_qubits)
        idx = 0
        for d in range(depth):
            for q in range(num_qubits):
                circuit.ry(params[idx], q)
                idx += 1
            for q in range(num_qubits - 1):
                circuit.cnot(q, q + 1)
        # Final rotation layer
        for q in range(num_qubits):
            circuit.ry(params[idx], q)
            idx += 1
        return circuit

    return build


__all__ = [
    "hardware_efficient_ansatz",
    "real_amplitudes",
    "two_local",
    "excitation_preserving",
    "strongly_entangling",
]
