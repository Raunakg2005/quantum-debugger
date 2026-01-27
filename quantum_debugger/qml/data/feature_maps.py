"""
Quantum Feature Maps

Encode classical data into quantum states through feature maps.
"""

import numpy as np
from typing import Callable
from ...core.circuit import QuantumCircuit


def zz_feature_map(n_qubits: int, reps: int = 2) -> Callable:
    """
    ZZ Feature Map for data encoding.

    Uses RZ rotations and ZZ entanglement to encode classical features
    into quantum states. This is one of the most commonly used feature maps.

    Args:
        n_qubits: Number of qubits (should match number of features)
        reps: Number of repetitions (depth)

    Returns:
        Function that encodes data into circuit

    Example:
        >>> feature_map = zz_feature_map(n_qubits=3, reps=2)
        >>> data = [0.5, 0.8, 0.3]
        >>> circuit = feature_map(data)
    """

    def encode(data: np.ndarray) -> QuantumCircuit:
        """Encode data into quantum circuit"""
        if len(data) != n_qubits:
            raise ValueError(f"Data dimension {len(data)} doesn't match n_qubits {n_qubits}")

        circuit = QuantumCircuit(n_qubits)

        for rep in range(reps):
            # Hadamard layer
            for i in range(n_qubits):
                circuit.h(i)

            # Encoding layer - RZ with data
            for i in range(n_qubits):
                # Encode feature as rotation angle
                circuit.rz(data[i], i)

            # Entanglement layer - ZZ interactions
            for i in range(n_qubits - 1):
                # ZZ(φ) = exp(-i φ Z⊗Z / 2) implemented with CNOTs and RZ
                phi = (np.pi - data[i]) * (np.pi - data[i+1])
                circuit.cnot(i, i+1)
                circuit.rz(phi, i+1)
                circuit.cnot(i, i+1)

        return circuit

    encode.n_qubits = n_qubits
    encode.reps = reps
    encode.name = 'zz_feature_map'

    return encode


def pauli_feature_map(n_qubits: int,
                      paulis: str = 'ZZ',
                      reps: int = 2) -> Callable:
    """
    Pauli Feature Map with configurable Pauli strings.

    Args:
        n_qubits: Number of qubits
        paulis: Pauli string pattern ('Z', 'ZZ', 'ZZZ', etc.)
        reps: Number of repetitions

    Returns:
        Encoding function

    Example:
        >>> feature_map = pauli_feature_map(n_qubits=4, paulis='ZZ')
        >>> circuit = feature_map([0.1, 0.2, 0.3, 0.4])
    """

    def encode(data: np.ndarray) -> QuantumCircuit:
        """Encode using Pauli rotations"""
        if len(data) != n_qubits:
            raise ValueError(f"Data dimension {len(data)} doesn't match n_qubits {n_qubits}")

        circuit = QuantumCircuit(n_qubits)

        for rep in range(reps):
            # Hadamard layer for superposition
            for i in range(n_qubits):
                circuit.h(i)

            # Feature encoding with specified Pauli
            if paulis == 'Z':
                # Single Z rotations
                for i in range(n_qubits):
                    circuit.rz(data[i], i)

            elif paulis == 'ZZ':
                # ZZ interactions
                for i in range(n_qubits):
                    circuit.rz(data[i], i)
                for i in range(n_qubits - 1):
                    phi = data[i] * data[i+1]
                    circuit.cnot(i, i+1)
                    circuit.rz(phi, i+1)
                    circuit.cnot(i, i+1)

            else:
                raise ValueError(f"Unsupported Pauli string: {paulis}")

        return circuit

    encode.n_qubits = n_qubits
    encode.paulis = paulis
    encode.reps = reps
    encode.name = 'pauli_feature_map'

    return encode


def angle_encoding(n_qubits: int, rotation: str = 'Y') -> Callable:
    """
    Simple angle encoding - encode features directly as rotation angles.

    Each feature is encoded as a rotation angle on one qubit.

    Args:
        n_qubits: Number of qubits (= number of features)
        rotation: Rotation axis ('X', 'Y', or 'Z')

    Returns:
        Encoding function

    Example:
        >>> encoder = angle_encoding(n_qubits=3, rotation='Y')
        >>> circuit = encoder([0.5, 1.0, 1.5])
    """

    def encode(data: np.ndarray) -> QuantumCircuit:
        """Encode data as rotation angles"""
        if len(data) != n_qubits:
            raise ValueError(f"Data dimension {len(data)} doesn't match n_qubits {n_qubits}")

        circuit = QuantumCircuit(n_qubits)

        for i, value in enumerate(data):
            if rotation == 'X':
                circuit.rx(value, i)
            elif rotation == 'Y':
                circuit.ry(value, i)
            elif rotation == 'Z':
                circuit.rz(value, i)
            else:
                raise ValueError(f"Unknown rotation: {rotation}")

        return circuit

    encode.n_qubits = n_qubits
    encode.rotation = rotation
    encode.name = 'angle_encoding'

    return encode


def amplitude_encoding(data: np.ndarray) -> QuantumCircuit:
    """
    Amplitude encoding - encode data directly into state amplitudes.

    For N features, needs log2(N) qubits. Data is normalized and
    encoded into quantum state amplitudes.

    Args:
        data: Feature vector to encode

    Returns:
        Circuit with encoded state

    Note:
        This is more complex and requires state preparation.
        For now, returns a placeholder.
    """
    # Calculate required qubits
    n_qubits = int(np.ceil(np.log2(len(data))))

    # Normalize data
    data_norm = data / np.linalg.norm(data)

    circuit = QuantumCircuit(n_qubits)

    # TODO: Implement full amplitude encoding
    # For now, use angle encoding as approximation
    for i in range(min(n_qubits, len(data))):
        circuit.ry(data_norm[i], i)

    return circuit


def get_feature_map(name: str, n_qubits: int, **kwargs) -> Callable:
    """
    Factory function to get feature map by name.

    Args:
        name: Feature map name ('zz', 'pauli', 'angle')
        n_qubits: Number of qubits
        **kwargs: Additional arguments for the feature map

    Returns:
        Feature map encoding function

    Example:
        >>> fm = get_feature_map('zz', n_qubits=4, reps=2)
        >>> circuit = fm([0.1, 0.2, 0.3, 0.4])
    """
    feature_maps = {
        'zz': zz_feature_map,
        'pauli': pauli_feature_map,
        'angle': angle_encoding,
    }

    if name not in feature_maps:
        raise ValueError(f"Unknown feature map: {name}. Choose from {list(feature_maps.keys())}")

    return feature_maps[name](n_qubits, **kwargs)
