"""
Ansatz (Variational Circuit) Builders
=====================================

Pre-built ansatz templates for variational algorithms.
"""

from typing import List
import numpy as np
from quantum_debugger.qml.gates.parameterized import RYGate, RXGate, RZGate


def hardware_efficient_ansatz(params: np.ndarray, num_qubits: int, depth: int = 1) -> List:
    """
    Hardware-efficient ansatz using RY rotations.
    
    Circuit structure:
    - Layer of RY gates (parameterized)
    - CNOT entanglement (not parameterized, handled by circuit)
    - Repeated 'depth' times
    
    Args:
        params: Parameter array [θ₀, θ₁, ..., θₙ]
        num_qubits: Number of qubits
        depth: Number of layers (default=1)
        
    Returns:
        List of parameterized gates
        
    Number of parameters: num_qubits * depth
    
    Examples:
        >>> params = np.array([0.5, 0.8])
        >>> gates = hardware_efficient_ansatz(params, num_qubits=2, depth=1)
        >>> # Returns [RY(0, 0.5), RY(1, 0.8)]
    """
    gates = []
    param_idx = 0
    
    expected_params = num_qubits * depth
    if len(params) < expected_params:
        raise ValueError(
            f"Expected {expected_params} parameters for {num_qubits} qubits "
            f"and depth {depth}, got {len(params)}"
        )
    
    for d in range(depth):
        # Layer of single-qubit rotations
        for q in range(num_qubits):
            gates.append(RYGate(target=q, parameter=params[param_idx], trainable=True))
            param_idx += 1
        
        # Note: CNOT gates for entanglement would be added by the circuit
        # For now, we only return parameterized gates
    
    return gates


def real_amplitudes_ansatz(params: np.ndarray, num_qubits: int, depth: int = 1) -> List:
    """
    Real amplitudes ansatz (RY rotations only, produces real amplitudes).
    
    Same as hardware_efficient_ansatz but emphasizes real-valued states.
    
    Args:
        params: Parameter array
        num_qubits: Number of qubits
        depth: Number of layers
        
    Returns:
        List of RY gates
    """
    return hardware_efficient_ansatz(params, num_qubits, depth)


def ucc_singlet_ansatz(params: np.ndarray, num_qubits: int) -> List:
    """
    Unitary Coupled Cluster Singles ansatz.
    
    Chemistry-inspired ansatz for molecular ground states.
    Uses RY rotations to represent single excitations.
    
    Args:
        params: Parameters for single excitations
        num_qubits: Number of qubits
        
    Returns:
        List of gates
    """
    gates = []
    
    # Single excitations: one parameter per qubit pair
    param_idx = 0
    for i in range(0, num_qubits, 2):
        if param_idx < len(params):
            # RY rotation represents excitation
            gates.append(RYGate(target=i, parameter=params[param_idx], trainable=True))
            if i + 1 < num_qubits:
                gates.append(RYGate(target=i+1, parameter=params[param_idx], trainable=True))
            param_idx += 1
    
    return gates


def alternating_layered_ansatz(params: np.ndarray, num_qubits: int, depth: int = 1) -> List:
    """
    Alternating RX and RY layers.
    
    Structure:
    - RY layer
    - RX layer
    - Repeated 'depth' times
    
    Args:
        params: Parameters (2 * num_qubits * depth)
        num_qubits: Number of qubits
        depth: Number of repetitions
        
    Returns:
        List of gates
    """
    gates = []
    param_idx = 0
    
    for d in range(depth):
        # RY layer
        for q in range(num_qubits):
            gates.append(RYGate(target=q, parameter=params[param_idx], trainable=True))
            param_idx += 1
        
        # RX layer
        for q in range(num_qubits):
            gates.append(RXGate(target=q, parameter=params[param_idx], trainable=True))
            param_idx += 1
    
    return gates


def num_parameters(ansatz_name: str, num_qubits: int, depth: int = 1) -> int:
    """
    Calculate number of parameters for an ansatz.
    
    Args:
        ansatz_name: Name of ansatz ('hardware_efficient', 'alternating', etc.)
        num_qubits: Number of qubits
        depth: Depth/layers
        
    Returns:
        Number of parameters needed
    """
    param_counts = {
        'hardware_efficient': num_qubits * depth,
        'real_amplitudes': num_qubits * depth,
        'ucc_singlet': num_qubits // 2,
        'alternating': 2 * num_qubits * depth,
    }
    
    return param_counts.get(ansatz_name, num_qubits * depth)
