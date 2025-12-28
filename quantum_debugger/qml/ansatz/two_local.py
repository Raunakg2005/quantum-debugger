"""
TwoLocal Ansatz

A highly customizable ansatz with alternating rotation and entanglement layers.
Users can specify which gates to use in each layer.
"""

import numpy as np
from typing import Callable, List, Union
from ...core.circuit import QuantumCircuit


def two_local(num_qubits: int,
              rotation_blocks: Union[str, List[str]] = 'ry',
              entanglement_blocks: str = 'cnot',
              entanglement: str = 'linear',
              reps: int = 1) -> Callable:
    """
    Create a highly customizable TwoLocal ansatz.
    
    This ansatz alternates between rotation layers (single-qubit gates) and
    entanglement layers (two-qubit gates), allowing full customization.
    
    Args:
        num_qubits: Number of qubits
        rotation_blocks: Single-qubit gates to use. Can be:
            - Single gate: 'ry', 'rz', 'rx'
            - List of gates: ['ry', 'rz'] (alternates between them)
        entanglement_blocks: Two-qubit gate to use:
            - 'cnot': CNOT gates
            - 'cz': CZ gates
            - 'swap': SWAP gates
        entanglement: Connection pattern:
            - 'linear': Chain 0-1, 1-2, 2-3, ...
            - 'full': All-to-all
            - 'circular': Ring with wrap-around
        reps: Number of repetitions
        
    Returns:
        Function that builds circuit with given parameters
        
    Example:
        >>> # Simple RY + CNOT ansatz
        >>> ansatz = two_local(3, rotation_blocks='ry', reps=2)
        >>> 
        >>> # Mixed rotations
        >>> ansatz = two_local(3, rotation_blocks=['ry', 'rz'], reps=2)
    """
    
    # Normalize rotation_blocks to list
    if isinstance(rotation_blocks, str):
        rotation_blocks = [rotation_blocks]
    
    def build_circuit(params: np.ndarray) -> QuantumCircuit:
        """Build the TwoLocal circuit"""
        circuit = QuantumCircuit(num_qubits)
        param_idx = 0
        
        for rep in range(reps + 1):
            # Rotation layer
            # Determine which rotation gates to use in this layer
            block_idx = rep % len(rotation_blocks)
            gate_type = rotation_blocks[block_idx]
            
            for qubit in range(num_qubits):
                if param_idx < len(params):
                    angle = params[param_idx]
                    param_idx += 1
                    
                    # Apply the rotation gate
                    if gate_type == 'ry':
                        circuit.ry(angle, qubit)
                    elif gate_type == 'rz':
                        circuit.rz(angle, qubit)
                    elif gate_type == 'rx':
                        circuit.rx(angle, qubit)
                    else:
                        raise ValueError(f"Unknown rotation gate: {gate_type}")
            
            # Entanglement layer (skip after last rotation)
            if rep < reps:
                # Get qubit pairs based on entanglement pattern
                pairs = _get_entanglement_pairs(num_qubits, entanglement)
                
                for control, target in pairs:
                    if entanglement_blocks == 'cnot':
                        circuit.cnot(control, target)
                    elif entanglement_blocks == 'cz':
                        circuit.cz(control, target)
                    elif entanglement_blocks == 'swap':
                        circuit.swap(control, target)
                    else:
                        raise ValueError(f"Unknown entanglement gate: {entanglement_blocks}")
        
        return circuit
    
    # Calculate required parameters
    params_needed = (reps + 1) * num_qubits
    build_circuit.num_parameters = params_needed
    build_circuit.num_qubits = num_qubits
    build_circuit.reps = reps
    build_circuit.rotation_blocks = rotation_blocks
    build_circuit.entanglement_blocks = entanglement_blocks
    build_circuit.entanglement = entanglement
    
    return build_circuit


def _get_entanglement_pairs(num_qubits: int, pattern: str) -> List[tuple]:
    """
    Get list of qubit pairs for entanglement.
    
    Args:
        num_qubits: Number of qubits
        pattern: Entanglement pattern
        
    Returns:
        List of (control, target) pairs
    """
    if pattern == 'linear':
        return [(i, i+1) for i in range(num_qubits - 1)]
    
    elif pattern == 'full':
        return [(i, j) for i in range(num_qubits) 
                for j in range(i+1, num_qubits)]
    
    elif pattern == 'circular':
        return [(i, (i+1) % num_qubits) for i in range(num_qubits)]
    
    else:
        raise ValueError(f"Unknown entanglement pattern: {pattern}")


def count_gates(num_qubits: int, reps: int, entanglement: str) -> dict:
    """
    Count the number of gates in a TwoLocal circuit.
    
    Args:
        num_qubits: Number of qubits
        reps: Number of repetitions
        entanglement: Entanglement pattern
        
    Returns:
        Dictionary with gate counts
    """
    rotation_gates = (reps + 1) * num_qubits
    
    if entanglement == 'linear':
        entanglement_gates = reps * (num_qubits - 1)
    elif entanglement == 'full':
        entanglement_gates = reps * (num_qubits * (num_qubits - 1)) // 2
    elif entanglement == 'circular':
        entanglement_gates = reps * num_qubits
    else:
        entanglement_gates = 0
    
    return {
        'rotation_gates': rotation_gates,
        'entanglement_gates': entanglement_gates,
        'total_gates': rotation_gates + entanglement_gates,
        'parameters': rotation_gates
    }
