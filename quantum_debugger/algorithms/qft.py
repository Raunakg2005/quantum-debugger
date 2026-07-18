"""
Quantum Fourier Transform (QFT)

Gate-based QFT and inverse QFT built from Hadamards and controlled-phase gates,
followed by the qubit-reversal swaps. Matches the standard discrete Fourier
transform on the computational basis.
"""

import numpy as np

from ..core.circuit import QuantumCircuit


def apply_qft(
    circuit: QuantumCircuit, qubits=None, swaps: bool = True
) -> QuantumCircuit:
    """
    Append a QFT over ``qubits`` (default: all) to ``circuit``.

    Uses H on each qubit followed by controlled-phase rotations from the
    lower-order qubits, then reverses the qubit order with SWAPs.
    """
    n = circuit.num_qubits
    # Reversed default so the whole-register QFT matches the standard DFT matrix
    # in this little-endian simulator (qubit 0 = least significant bit).
    qubits = list(reversed(range(n))) if qubits is None else list(qubits)
    m = len(qubits)

    for i in range(m):
        q = qubits[i]
        circuit.h(q)
        for j in range(i + 1, m):
            angle = np.pi / (2 ** (j - i))
            circuit.cp(angle, qubits[j], q)

    if swaps:
        for i in range(m // 2):
            circuit.swap(qubits[i], qubits[m - 1 - i])

    return circuit


def apply_inverse_qft(
    circuit: QuantumCircuit, qubits=None, swaps: bool = True
) -> QuantumCircuit:
    """Append the inverse QFT (dagger of :func:`apply_qft`) to ``circuit``."""
    n = circuit.num_qubits
    # Reversed default so the whole-register QFT matches the standard DFT matrix
    # in this little-endian simulator (qubit 0 = least significant bit).
    qubits = list(reversed(range(n))) if qubits is None else list(qubits)
    m = len(qubits)

    if swaps:
        for i in range(m // 2):
            circuit.swap(qubits[i], qubits[m - 1 - i])

    for i in reversed(range(m)):
        q = qubits[i]
        for j in reversed(range(i + 1, m)):
            angle = -np.pi / (2 ** (j - i))
            circuit.cp(angle, qubits[j], q)
        circuit.h(q)

    return circuit


def qft(n_qubits: int, inverse: bool = False) -> QuantumCircuit:
    """Return a fresh circuit implementing the (inverse) QFT on n_qubits."""
    circuit = QuantumCircuit(n_qubits)
    if inverse:
        apply_inverse_qft(circuit)
    else:
        apply_qft(circuit)
    return circuit


def qft_matrix(n_qubits: int) -> np.ndarray:
    """The analytic QFT (DFT) matrix, for reference/verification."""
    N = 2**n_qubits
    omega = np.exp(2j * np.pi / N)
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    return omega ** (j * k) / np.sqrt(N)
